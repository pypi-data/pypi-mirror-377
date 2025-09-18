"""Async GitHub API client with batch processing capabilities."""

import asyncio
import base64
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, AsyncIterator
from urllib.parse import quote

import httpx

from .exceptions import (
    AuthenticationError,
    NetworkError,
    RateLimitError,
    APIError,
    RepositoryNotFoundError,
    OrganizationNotFoundError,
    TeamNotFoundError,
    wrap_exception,
    get_error_context
)
from .logging_config import get_logger, log_exception, log_rate_limit
from .models import APIResponse, FileContent, FileInfo, Repository
from .batch_models import (
    BatchRequest, BatchResult, BatchMetrics, AsyncBatchContext,
    BatchConfig, NetworkConditions
)

logger = get_logger(__name__)


class AsyncGitHubClient:
    """Async client for interacting with the GitHub API with batch processing capabilities."""

    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None, config: Optional[BatchConfig] = None) -> None:
        """Initialize the async GitHub client with authentication token.
        
        Args:
            token: GitHub personal access token. If None, will attempt auto-discovery.
            config: Batch processing configuration
        """
        self.token = token or self._discover_token()
        self.config = config or BatchConfig()
        self.client: Optional[httpx.AsyncClient] = None
        self._session_lock = asyncio.Lock()
        
    def _discover_token(self) -> str:
        """Discover GitHub token from environment or gh CLI."""
        # Try GITHUB_TOKEN environment variable first
        token = os.getenv("GITHUB_TOKEN")
        if token:
            logger.debug("Using GITHUB_TOKEN environment variable")
            return token
            
        # Try gh auth token command
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            token = result.stdout.strip()
            if token:
                logger.debug("Using token from 'gh auth token' command")
                return token
        except subprocess.CalledProcessError as e:
            logger.debug(f"'gh auth token' command failed with exit code {e.returncode}")
        except subprocess.TimeoutExpired:
            logger.debug("'gh auth token' command timed out")
        except FileNotFoundError:
            logger.debug("'gh' command not found in PATH")
        except Exception as e:
            logger.debug(f"Unexpected error running 'gh auth token': {e}")
            
        raise AuthenticationError(
            "No GitHub token found. Please set GITHUB_TOKEN environment variable or run 'gh auth login'"
        )
    
    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create async HTTP session."""
        async with self._session_lock:
            if self.client is None or self.client.is_closed:
                self.client = httpx.AsyncClient(
                    base_url=self.BASE_URL,
                    headers={
                        "Authorization": f"Bearer {self.token}",
                        "Accept": "application/vnd.github.v3+json",
                        "User-Agent": "github-ioc-scanner/0.1.0",
                    },
                    timeout=30.0,
                    limits=httpx.Limits(
                        max_keepalive_connections=20,
                        max_connections=100,
                        keepalive_expiry=30.0
                    )
                )
            return self.client
    
    async def _make_request(
        self, 
        method: str, 
        url: str, 
        etag: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """Make an async request to the GitHub API with rate limiting and ETag support."""
        headers = kwargs.pop("headers", {})
        
        # Add ETag for conditional requests
        if etag:
            headers["If-None-Match"] = etag
            
        try:
            session = await self._get_session()
            response = await session.request(method, url, headers=headers, params=params, **kwargs)
            

            # Log rate limit information
            remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            log_rate_limit(logger, remaining, reset_time)
            
            # Handle rate limiting
            if response.status_code == 403:
                error_message = response.text.lower()
                if "rate limit exceeded" in error_message or "api rate limit exceeded" in error_message:
                    reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                    raise RateLimitError(
                        f"GitHub API rate limit exceeded. Resets at {datetime.fromtimestamp(reset_time)}",
                        reset_time=reset_time
                    )
                elif "forbidden" in error_message:
                    raise AuthenticationError("Access forbidden. Check token permissions for this resource.")
                else:
                    raise APIError(f"Forbidden: {response.text}", status_code=403)
            
            # Handle 304 Not Modified
            if response.status_code == 304:
                logger.debug(f"Resource not modified: {url}")
                return APIResponse(
                    data=None,
                    etag=etag,
                    not_modified=True,
                    rate_limit_remaining=remaining,
                    rate_limit_reset=reset_time,
                )
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            # Parse response data
            try:
                data = response.json() if response.content else None
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response from {url}: {e}")
                data = None
            
            return APIResponse(
                data=data,
                etag=response.headers.get("ETag"),
                not_modified=False,
                rate_limit_remaining=remaining,
                rate_limit_reset=reset_time,
            )
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid GitHub token or insufficient permissions")
            elif e.response.status_code == 404:
                logger.debug(f"Resource not found: {url}")
                return APIResponse(data=None)
            elif e.response.status_code == 422:
                raise APIError(f"Unprocessable entity: {e.response.text}", status_code=422)
            else:
                raise APIError(f"HTTP {e.response.status_code}: {e.response.text}", status_code=e.response.status_code)
        except httpx.ConnectTimeout as e:
            raise NetworkError(f"Connection timeout to GitHub API: {url}", cause=e)
        except httpx.ReadTimeout as e:
            raise NetworkError(f"Read timeout from GitHub API: {url}", cause=e)
        except httpx.RequestError as e:
            raise NetworkError(f"Network error accessing GitHub API: {url}", cause=e)
        except (RateLimitError, AuthenticationError, APIError, NetworkError):
            # These are expected exceptions that should be re-raised as-is
            raise
        except Exception as e:
            log_exception(logger, f"Unexpected error making request to {url}", e)
            raise wrap_exception(e, f"Unexpected error making request to {url}")
    
    async def get_file_content_async(
        self, repo: Repository, path: str, etag: Optional[str] = None
    ) -> APIResponse:
        """Get the content of a specific file asynchronously.
        
        Args:
            repo: Repository containing the file
            path: Path to the file
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing FileContent object
        """
        try:
            url = f"/repos/{quote(repo.full_name)}/contents/{quote(path, safe='/')}"
            response = await self._make_request("GET", url, etag=etag)
            
            if response.not_modified or not response.data:
                return response
                
            file_data = response.data
            
            # Handle directory responses
            if isinstance(file_data, list):
                logger.warning(f"Path {path} in {repo.full_name} is a directory, not a file")
                return APIResponse(data=None)
            
            # Validate required fields
            if not isinstance(file_data, dict):
                logger.warning(f"Invalid file data format for {repo.full_name}/{path}")
                return APIResponse(data=None)
            
            required_fields = ["content", "sha", "size"]
            missing_fields = [field for field in required_fields if field not in file_data]
            if missing_fields:
                logger.warning(f"Missing required fields {missing_fields} in file data for {repo.full_name}/{path}")
                return APIResponse(data=None)
            
            # Decode base64 content
            content_b64 = file_data.get("content", "")
            try:
                content = base64.b64decode(content_b64).decode("utf-8")
            except (ValueError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to decode file content for {repo.full_name}/{path}: {e}")
                # Try with different encodings
                try:
                    content = base64.b64decode(content_b64).decode("utf-8", errors="replace")
                    logger.info(f"Decoded file content with replacement characters for {repo.full_name}/{path}")
                except Exception:
                    logger.error(f"Could not decode file content for {repo.full_name}/{path}")
                    return APIResponse(data=None)
            
            try:
                file_content = FileContent(
                    content=content,
                    sha=file_data["sha"],
                    size=file_data["size"],
                )
            except (KeyError, TypeError) as e:
                logger.warning(f"Failed to create FileContent object for {repo.full_name}/{path}: {e}")
                return APIResponse(data=None)
            
            return APIResponse(
                data=file_content,
                etag=response.etag,
                not_modified=False,
                rate_limit_remaining=response.rate_limit_remaining,
                rate_limit_reset=response.rate_limit_reset,
            )
            
        except (RepositoryNotFoundError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            log_exception(logger, f"Failed to get file content for {repo.full_name}/{path}", e)
            raise wrap_exception(e, f"Failed to get file content for {repo.full_name}/{path}")
    
    async def get_blob_content_async(self, repo: Repository, sha: str) -> Optional[str]:
        """Get blob content by SHA using Git Blob API asynchronously.
        
        Args:
            repo: Repository containing the blob
            sha: SHA hash of the blob
            
        Returns:
            Decoded file content as string, or None if failed
            
        Raises:
            RateLimitError: If rate limit is exceeded
            NetworkError: If network operations fail
            AuthenticationError: If authentication fails
        """
        try:
            url = f"/repos/{quote(repo.full_name)}/git/blobs/{sha}"
            response = await self._make_request("GET", url)
            
            if not response.data:
                logger.debug(f"No blob data returned for SHA {sha}")
                return None
            
            blob_data = response.data
            
            # Validate blob data structure
            if not isinstance(blob_data, dict):
                logger.warning(f"Invalid blob data format for SHA {sha}")
                return None
            
            content = blob_data.get('content', '')
            encoding = blob_data.get('encoding', 'base64')
            
            if not content:
                logger.debug(f"Empty content for blob {sha}")
                return ""
            
            if encoding == 'base64':
                try:
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    return decoded_content
                except (UnicodeDecodeError, ValueError) as e:
                    logger.warning(f"Failed to decode blob {sha} as UTF-8: {e}")
                    # Try with error replacement
                    try:
                        decoded_content = base64.b64decode(content).decode('utf-8', errors='replace')
                        logger.info(f"Decoded blob {sha} with replacement characters")
                        return decoded_content
                    except Exception as e2:
                        logger.error(f"Could not decode blob {sha} at all: {e2}")
                        return None
            else:
                # Assume it's already text
                return content
                
        except (RateLimitError, NetworkError, AuthenticationError):
            # Re-raise these exceptions for proper handling upstream
            raise
        except Exception as e:
            logger.warning(f"Failed to get blob content for SHA {sha}: {e}")
            return None
    
    async def get_tree_async(self, repo: Repository, etag: Optional[str] = None) -> APIResponse:
        """Get the Git tree for a repository asynchronously.
        
        Args:
            repo: Repository to get tree for
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing list of FileInfo objects
        """
        url = f"/repos/{quote(repo.full_name)}/git/trees/{repo.default_branch}"
        params = {"recursive": "1"}
        
        response = await self._make_request("GET", url, etag=etag, params=params)
        
        if response.not_modified or not response.data:
            return response
            
        tree_data = response.data
        files = []
        
        for item in tree_data.get("tree", []):
            if item["type"] == "blob":  # Only include files, not directories
                file_info = FileInfo(
                    path=item["path"],
                    sha=item["sha"],
                    size=item.get("size", 0),
                )
                files.append(file_info)
        
        return APIResponse(
            data=files,
            etag=response.etag,
            not_modified=False,
            rate_limit_remaining=response.rate_limit_remaining,
            rate_limit_reset=response.rate_limit_reset,
        )
    
    async def get_multiple_file_contents_parallel(
        self,
        repo: Repository,
        file_paths: List[str],
        max_concurrent: Optional[int] = None
    ) -> Dict[str, FileContent]:
        """Get multiple file contents with parallel processing and enhanced error handling.
        
        This method uses the Git Tree API to get file metadata, then fetches file contents
        in parallel using the Git Blob API for optimal performance.
        
        Args:
            repo: Repository containing the files
            file_paths: List of file paths to fetch
            max_concurrent: Maximum concurrent requests (uses config default if None)
            
        Returns:
            Dictionary mapping file paths to FileContent objects
            
        Raises:
            RepositoryNotFoundError: If the repository doesn't exist
            NetworkError: If network operations fail
        """
        if not file_paths:
            return {}
        
        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        try:
            logger.debug(f"Fetching {len(file_paths)} files from {repo.full_name} with {max_concurrent} concurrent requests")
            
            # Get the repository tree first
            tree_response = await self.get_tree_async(repo)
            if not tree_response.data:
                logger.warning(f"No tree data available for {repo.full_name}")
                return {}
            
            tree_files = tree_response.data
            
            # Create a mapping of path to tree entry
            tree_map = {file_info.path: file_info for file_info in tree_files}
            
            # Filter out files that don't exist in the tree
            existing_files = [path for path in file_paths if path in tree_map]
            missing_files = [path for path in file_paths if path not in tree_map]
            
            if missing_files:
                logger.debug(f"Files not found in tree for {repo.full_name}: {missing_files}")
            
            if not existing_files:
                logger.debug(f"No existing files to fetch for {repo.full_name}")
                return {}
            
            # Create tasks for parallel blob fetching
            tasks = []
            for file_path in existing_files:
                file_info = tree_map[file_path]
                task = self._fetch_blob_with_semaphore(
                    semaphore, repo, file_path, file_info
                )
                tasks.append(task)
            
            # Execute all tasks in parallel with proper error handling
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            file_contents = {}
            successful_fetches = 0
            failed_fetches = 0
            
            for i, result in enumerate(results):
                file_path = existing_files[i]
                
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch file content for {repo.full_name}/{file_path}: {result}")
                    failed_fetches += 1
                    continue
                
                if result and len(result) == 2:
                    result_path, file_content = result
                    if file_content:
                        file_contents[result_path] = file_content
                        successful_fetches += 1
                    else:
                        logger.warning(f"No content returned for {repo.full_name}/{file_path}")
                        failed_fetches += 1
                else:
                    logger.warning(f"Invalid result format for {repo.full_name}/{file_path}")
                    failed_fetches += 1
            
            logger.debug(f"Batch fetch completed for {repo.full_name}: {successful_fetches} successful, {failed_fetches} failed")
            return file_contents
            
        except (RepositoryNotFoundError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Parallel file content fetch failed for {repo.full_name}: {e}")
            raise wrap_exception(e, f"Parallel file content fetch failed for {repo.full_name}")
    
    async def _fetch_blob_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        repo: Repository,
        file_path: str,
        file_info: FileInfo
    ) -> Optional[tuple]:
        """Fetch a single blob with semaphore control and retry logic.
        
        Args:
            semaphore: Semaphore for controlling concurrency
            repo: Repository containing the file
            file_path: Path to the file
            file_info: File information from tree
            
        Returns:
            Tuple of (file_path, FileContent) or None if failed
        """
        async with semaphore:
            for attempt in range(self.config.retry_attempts + 1):
                try:
                    blob_content = await self.get_blob_content_async(repo, file_info.sha)
                    if blob_content:
                        file_content = FileContent(
                            content=blob_content,
                            sha=file_info.sha,
                            size=file_info.size
                        )
                        return (file_path, file_content)
                    else:
                        logger.debug(f"No blob content returned for {repo.full_name}/{file_path}")
                        return None
                        
                except RateLimitError as e:
                    if attempt < self.config.retry_attempts:
                        delay = self.config.retry_delay_base * (2 ** attempt)
                        logger.debug(f"Rate limited fetching {file_path}, retrying in {delay}s (attempt {attempt + 1})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.warning(f"Rate limit exceeded for {repo.full_name}/{file_path} after {attempt + 1} attempts")
                        raise
                        
                except (NetworkError, AuthenticationError) as e:
                    if attempt < self.config.retry_attempts:
                        delay = self.config.retry_delay_base * (2 ** attempt)
                        logger.debug(f"Network/auth error fetching {file_path}, retrying in {delay}s (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        logger.warning(f"Network/auth error for {repo.full_name}/{file_path} after {attempt + 1} attempts: {e}")
                        raise
                        
                except Exception as e:
                    logger.warning(f"Failed to get blob content for {repo.full_name}/{file_path}: {e}")
                    return None
            
            return None
    
    async def process_batch_requests(
        self,
        requests: List[BatchRequest],
        context: Optional[AsyncBatchContext] = None
    ) -> List[BatchResult]:
        """Process a batch of requests with parallel execution.
        
        Args:
            requests: List of batch requests to process
            context: Async batch context for coordination
            
        Returns:
            List of batch results
        """
        if not requests:
            return []
        
        if context is None:
            context = AsyncBatchContext(
                semaphore=asyncio.Semaphore(self.config.max_concurrent_requests)
            )
        
        # Create tasks for parallel processing
        tasks = []
        for request in requests:
            task = self._process_single_request_with_semaphore(request, context)
            tasks.append(task)
        
        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        batch_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                batch_result = BatchResult(
                    request=requests[i],
                    error=result,
                    processing_time=0.0
                )
            else:
                batch_result = result
            
            batch_results.append(batch_result)
        
        return batch_results
    
    async def _process_single_request_with_semaphore(
        self,
        request: BatchRequest,
        context: AsyncBatchContext
    ) -> BatchResult:
        """Process a single request with semaphore control and retry logic."""
        start_time = time.time()
        
        async with context.semaphore:
            for attempt in range(self.config.retry_attempts + 1):
                try:
                    # Get file content
                    response = await self.get_file_content_async(request.repo, request.file_path)
                    
                    processing_time = time.time() - start_time
                    
                    if response.data:
                        return BatchResult(
                            request=request,
                            content=response.data,
                            processing_time=processing_time
                        )
                    else:
                        return BatchResult(
                            request=request,
                            error=APIError(f"No content returned for {request.file_path}"),
                            processing_time=processing_time
                        )
                
                except RateLimitError as e:
                    # Handle rate limiting with exponential backoff
                    if attempt < self.config.retry_attempts:
                        delay = self.config.retry_delay_base * (2 ** attempt)
                        logger.debug(f"Rate limited, retrying in {delay}s (attempt {attempt + 1})")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return BatchResult(
                            request=request,
                            error=e,
                            processing_time=time.time() - start_time
                        )
                
                except Exception as e:
                    # Handle other errors
                    if attempt < self.config.retry_attempts:
                        delay = self.config.retry_delay_base * (2 ** attempt)
                        logger.debug(f"Request failed, retrying in {delay}s (attempt {attempt + 1}): {e}")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        return BatchResult(
                            request=request,
                            error=e,
                            processing_time=time.time() - start_time
                        )
        
        # This should never be reached, but just in case
        return BatchResult(
            request=request,
            error=APIError("Unexpected error in request processing"),
            processing_time=time.time() - start_time
        )
    
    async def stream_large_file_content(
        self,
        repo: Repository,
        file_path: str,
        chunk_size: int = 8192
    ) -> AsyncIterator[str]:
        """Stream large file content to prevent memory issues.
        
        This method streams file content in chunks to avoid loading large files
        entirely into memory. It uses the Contents API with streaming.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file
            chunk_size: Size of each chunk in bytes
            
        Yields:
            String chunks of file content
            
        Raises:
            RepositoryNotFoundError: If the repository doesn't exist
            NetworkError: If network operations fail
            AuthenticationError: If authentication fails
        """
        try:
            url = f"/repos/{quote(repo.full_name)}/contents/{quote(file_path, safe='/')}"
            
            # First, get file metadata to check size
            response = await self._make_request("GET", url)
            
            if not response.data:
                logger.debug(f"No file data for {repo.full_name}/{file_path}")
                return
            
            file_data = response.data
            
            # Handle directory responses
            if isinstance(file_data, list):
                logger.warning(f"Path {file_path} in {repo.full_name} is a directory, not a file")
                return
            
            # Check if file is large enough to warrant streaming
            file_size = file_data.get("size", 0)
            if file_size < self.config.stream_large_files_threshold:
                # For small files, just return content directly
                content_b64 = file_data.get("content", "")
                try:
                    content = base64.b64decode(content_b64).decode("utf-8")
                    yield content
                    return
                except (ValueError, UnicodeDecodeError) as e:
                    logger.warning(f"Failed to decode small file content for {repo.full_name}/{file_path}: {e}")
                    return
            
            # For large files, use blob API with streaming
            sha = file_data.get("sha")
            if not sha:
                logger.warning(f"No SHA found for large file {repo.full_name}/{file_path}")
                return
            
            async for chunk in self._stream_blob_content(repo, sha, chunk_size):
                yield chunk
                
        except (RepositoryNotFoundError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Failed to stream file content for {repo.full_name}/{file_path}: {e}")
            raise wrap_exception(e, f"Failed to stream file content for {repo.full_name}/{file_path}")
    
    async def _stream_blob_content(
        self,
        repo: Repository,
        sha: str,
        chunk_size: int = 8192
    ) -> AsyncIterator[str]:
        """Stream blob content in chunks.
        
        Args:
            repo: Repository containing the blob
            sha: SHA hash of the blob
            chunk_size: Size of each chunk in bytes
            
        Yields:
            String chunks of blob content
        """
        try:
            url = f"/repos/{quote(repo.full_name)}/git/blobs/{sha}"
            session = await self._get_session()
            
            async with session.stream("GET", url) as response:
                # Handle HTTP errors
                if response.status_code == 403:
                    error_message = await response.aread()
                    error_text = error_message.decode('utf-8', errors='replace').lower()
                    if "rate limit exceeded" in error_text:
                        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
                        raise RateLimitError(
                            f"GitHub API rate limit exceeded. Resets at {datetime.fromtimestamp(reset_time)}",
                            reset_time=reset_time
                        )
                    elif "forbidden" in error_text:
                        raise AuthenticationError("Access forbidden. Check token permissions for this resource.")
                    else:
                        raise APIError(f"Forbidden: {error_text}", status_code=403)
                
                response.raise_for_status()
                
                # Read and parse the JSON response in chunks
                content_buffer = b""
                async for chunk in response.aiter_bytes(chunk_size):
                    content_buffer += chunk
                
                # Parse the complete JSON response
                try:
                    blob_data = json.loads(content_buffer.decode('utf-8'))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse blob JSON for SHA {sha}: {e}")
                    return
                
                # Get the base64 content
                content_b64 = blob_data.get('content', '')
                encoding = blob_data.get('encoding', 'base64')
                
                if not content_b64:
                    logger.debug(f"Empty content for blob {sha}")
                    return
                
                if encoding == 'base64':
                    try:
                        # Decode base64 content
                        decoded_bytes = base64.b64decode(content_b64)
                        
                        # Stream the decoded content in chunks
                        for i in range(0, len(decoded_bytes), chunk_size):
                            chunk_bytes = decoded_bytes[i:i + chunk_size]
                            try:
                                chunk_str = chunk_bytes.decode('utf-8')
                                yield chunk_str
                            except UnicodeDecodeError:
                                # Handle partial UTF-8 sequences at chunk boundaries
                                # Try to find a safe boundary
                                safe_end = i + chunk_size
                                while safe_end > i and (decoded_bytes[safe_end - 1] & 0x80):
                                    safe_end -= 1
                                
                                if safe_end > i:
                                    safe_chunk = decoded_bytes[i:safe_end]
                                    try:
                                        chunk_str = safe_chunk.decode('utf-8')
                                        yield chunk_str
                                        # Adjust the next iteration to start from safe_end
                                        i = safe_end - chunk_size
                                    except UnicodeDecodeError:
                                        # If we still can't decode, use replacement characters
                                        chunk_str = chunk_bytes.decode('utf-8', errors='replace')
                                        yield chunk_str
                                else:
                                    # Fallback to replacement characters
                                    chunk_str = chunk_bytes.decode('utf-8', errors='replace')
                                    yield chunk_str
                    except (ValueError, UnicodeDecodeError) as e:
                        logger.warning(f"Failed to decode blob {sha}: {e}")
                        return
                else:
                    # Assume it's already text, stream it in chunks
                    for i in range(0, len(content_b64), chunk_size):
                        yield content_b64[i:i + chunk_size]
                        
        except (RateLimitError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Failed to stream blob content for SHA {sha}: {e}")
            raise wrap_exception(e, f"Failed to stream blob content for SHA {sha}")
    
    async def get_file_content_chunked(
        self,
        repo: Repository,
        file_path: str,
        max_size: Optional[int] = None
    ) -> Optional[FileContent]:
        """Get file content with chunked processing for large files.
        
        This method automatically determines whether to use regular or streaming
        approach based on file size and configuration.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file
            max_size: Maximum file size to process (uses config default if None)
            
        Returns:
            FileContent object or None if file is too large or doesn't exist
            
        Raises:
            RepositoryNotFoundError: If the repository doesn't exist
            NetworkError: If network operations fail
        """
        max_size = max_size or self.config.max_memory_usage_mb * 1024 * 1024  # Convert MB to bytes
        
        try:
            # First get file metadata
            url = f"/repos/{quote(repo.full_name)}/contents/{quote(file_path, safe='/')}"
            response = await self._make_request("GET", url)
            
            if not response.data:
                return None
            
            file_data = response.data
            
            # Handle directory responses
            if isinstance(file_data, list):
                logger.warning(f"Path {file_path} in {repo.full_name} is a directory, not a file")
                return None
            
            file_size = file_data.get("size", 0)
            
            # Check if file is too large
            if file_size > max_size:
                logger.warning(f"File {repo.full_name}/{file_path} is too large ({file_size} bytes > {max_size} bytes)")
                return None
            
            # For small files, use regular method
            if file_size < self.config.stream_large_files_threshold:
                return (await self.get_file_content_async(repo, file_path)).data
            
            # For large files, use streaming and accumulate content
            content_chunks = []
            total_size = 0
            
            async for chunk in self.stream_large_file_content(repo, file_path):
                content_chunks.append(chunk)
                total_size += len(chunk.encode('utf-8'))
                
                # Safety check to prevent memory issues
                if total_size > max_size:
                    logger.warning(f"File {repo.full_name}/{file_path} exceeded size limit during streaming")
                    return None
            
            # Combine chunks
            full_content = ''.join(content_chunks)
            
            return FileContent(
                content=full_content,
                sha=file_data.get("sha", ""),
                size=file_size
            )
            
        except (RepositoryNotFoundError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            logger.error(f"Failed to get chunked file content for {repo.full_name}/{file_path}: {e}")
            raise wrap_exception(e, f"Failed to get chunked file content for {repo.full_name}/{file_path}")
    
    async def get_cross_repo_file_contents(
        self,
        repo_files: Dict[str, tuple[Repository, List[str]]],
        max_concurrent: Optional[int] = None
    ) -> Dict[str, Dict[str, FileContent]]:
        """Get file contents across multiple repositories with batch processing.
        
        This method optimizes requests across multiple repositories by processing
        them in parallel while respecting rate limits and concurrency constraints.
        
        Args:
            repo_files: Dictionary mapping repo names to (Repository, file_paths) tuples
            max_concurrent: Maximum concurrent requests (uses config default if None)
            
        Returns:
            Dictionary mapping repository full names to file content dictionaries
            
        Raises:
            NetworkError: If network operations fail
            AuthenticationError: If authentication fails
        """
        if not repo_files:
            return {}
        
        max_concurrent = max_concurrent or self.config.max_concurrent_repos
        semaphore = asyncio.Semaphore(max_concurrent)
        
        try:
            logger.debug(f"Processing files across {len(repo_files)} repositories with {max_concurrent} concurrent repos")
            
            # Create tasks for each repository
            tasks = []
            for repo_name, (repo, file_paths) in repo_files.items():
                if file_paths:  # Only process repos with files
                    task = self._process_repo_files_with_semaphore(
                        semaphore, repo, file_paths
                    )
                    tasks.append(task)
            
            if not tasks:
                logger.debug("No repositories with files to process")
                return {}
            
            # Execute all repository tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            cross_repo_contents = {}
            successful_repos = 0
            failed_repos = 0
            
            repo_names = list(repo_files.keys())
            for i, result in enumerate(results):
                repo_name = repo_names[i]
                
                if isinstance(result, Exception):
                    logger.warning(f"Failed to process repository {repo_name}: {result}")
                    failed_repos += 1
                    cross_repo_contents[repo_name] = {}
                    continue
                
                if result and len(result) == 2:
                    result_repo_name, file_contents = result
                    cross_repo_contents[result_repo_name] = file_contents
                    successful_repos += 1
                else:
                    logger.warning(f"Invalid result format for repository {repo_name}")
                    failed_repos += 1
                    cross_repo_contents[repo_name] = {}
            
            logger.debug(f"Cross-repo batch completed: {successful_repos} successful, {failed_repos} failed")
            return cross_repo_contents
            
        except Exception as e:
            logger.error(f"Cross-repository batch processing failed: {e}")
            raise wrap_exception(e, "Cross-repository batch processing failed")
    
    async def _process_repo_files_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        repo: Repository,
        file_paths: List[str]
    ) -> Optional[tuple]:
        """Process files for a single repository with semaphore control.
        
        Args:
            semaphore: Semaphore for controlling repository concurrency
            repo: Repository to process
            file_paths: List of file paths to fetch
            
        Returns:
            Tuple of (repo_name, file_contents) or None if failed
        """
        async with semaphore:
            try:
                logger.debug(f"Processing {len(file_paths)} files for repository {repo.full_name}")
                
                # Use the existing parallel file content method
                file_contents = await self.get_multiple_file_contents_parallel(
                    repo, file_paths, max_concurrent=self.config.max_concurrent_requests
                )
                
                return (repo.full_name, file_contents)
                
            except Exception as e:
                logger.warning(f"Failed to process files for repository {repo.full_name}: {e}")
                return None
    
    async def process_cross_repo_batch_requests(
        self,
        requests: List[BatchRequest],
        context: Optional[AsyncBatchContext] = None
    ) -> Dict[str, List[BatchResult]]:
        """Process batch requests grouped by repository.
        
        This method groups requests by repository and processes them efficiently
        to minimize API calls and optimize performance across multiple repositories.
        
        Args:
            requests: List of batch requests to process
            context: Async batch context for coordination
            
        Returns:
            Dictionary mapping repository names to lists of batch results
        """
        if not requests:
            return {}
        
        if context is None:
            context = AsyncBatchContext(
                semaphore=asyncio.Semaphore(self.config.max_concurrent_repos)
            )
        
        try:
            # Group requests by repository
            repo_requests = {}
            for request in requests:
                repo_name = request.repo.full_name
                if repo_name not in repo_requests:
                    repo_requests[repo_name] = []
                repo_requests[repo_name].append(request)
            
            logger.debug(f"Processing {len(requests)} requests across {len(repo_requests)} repositories")
            
            # Create tasks for each repository
            tasks = []
            for repo_name, repo_request_list in repo_requests.items():
                task = self._process_repo_batch_requests_with_semaphore(
                    context.semaphore, repo_request_list
                )
                tasks.append(task)
            
            # Execute all repository tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            cross_repo_results = {}
            for i, result in enumerate(results):
                repo_name = list(repo_requests.keys())[i]
                
                if isinstance(result, Exception):
                    logger.warning(f"Failed to process batch requests for repository {repo_name}: {result}")
                    # Create error results for all requests in this repo
                    error_results = []
                    for request in repo_requests[repo_name]:
                        error_results.append(BatchResult(
                            request=request,
                            error=result,
                            processing_time=0.0
                        ))
                    cross_repo_results[repo_name] = error_results
                else:
                    cross_repo_results[repo_name] = result or []
            
            return cross_repo_results
            
        except Exception as e:
            logger.error(f"Cross-repository batch request processing failed: {e}")
            raise wrap_exception(e, "Cross-repository batch request processing failed")
    
    async def _process_repo_batch_requests_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        requests: List[BatchRequest]
    ) -> List[BatchResult]:
        """Process batch requests for a single repository with semaphore control.
        
        Args:
            semaphore: Semaphore for controlling repository concurrency
            requests: List of batch requests for this repository
            
        Returns:
            List of batch results
        """
        from .batch_models import BatchResult
        
        async with semaphore:
            try:
                # Use the existing batch processing method
                return await self.process_batch_requests(requests)
                
            except Exception as e:
                logger.warning(f"Failed to process batch requests: {e}")
                # Return error results for all requests
                error_results = []
                for request in requests:
                    error_results.append(BatchResult(
                        request=request,
                        error=e,
                        processing_time=0.0
                    ))
                return error_results
    
    async def get_optimized_cross_repo_batches(
        self,
        repo_files: Dict[Repository, List[str]],
        batch_size: Optional[int] = None
    ) -> Dict[str, Dict[str, FileContent]]:
        """Get file contents with optimized cross-repository batching.
        
        This method analyzes the requested files across repositories and optimizes
        the batching strategy to minimize API calls and maximize throughput.
        
        Args:
            repo_files: Dictionary mapping repositories to lists of file paths
            batch_size: Batch size for processing (uses config default if None)
            
        Returns:
            Dictionary mapping repository full names to file content dictionaries
        """
        if not repo_files:
            return {}
        
        batch_size = batch_size or self.config.default_batch_size
        
        try:
            # Analyze file patterns across repositories
            file_patterns = self._analyze_cross_repo_patterns(repo_files)
            
            # Group repositories by similar file patterns for optimized processing
            repo_groups = self._group_repos_by_patterns(repo_files, file_patterns)
            
            logger.debug(f"Optimized cross-repo processing: {len(repo_groups)} groups for {len(repo_files)} repositories")
            
            # Process each group with optimized batching
            all_results = {}
            for group_repos in repo_groups:
                group_repo_files = {repo: repo_files[repo] for repo in group_repos if repo in repo_files}
                
                if group_repo_files:
                    group_results = await self.get_cross_repo_file_contents(
                        group_repo_files,
                        max_concurrent=min(len(group_repo_files), self.config.max_concurrent_repos)
                    )
                    all_results.update(group_results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Optimized cross-repository batch processing failed: {e}")
            raise wrap_exception(e, "Optimized cross-repository batch processing failed")
    
    def _analyze_cross_repo_patterns(self, repo_files: Dict[Repository, List[str]]) -> Dict[str, int]:
        """Analyze file patterns across repositories to identify optimization opportunities.
        
        Args:
            repo_files: Dictionary mapping repositories to lists of file paths
            
        Returns:
            Dictionary mapping file patterns to frequency counts
        """
        file_patterns = {}
        
        for repo, file_paths in repo_files.items():
            for file_path in file_paths:
                # Extract file pattern (filename only for now)
                filename = file_path.split('/')[-1]
                file_patterns[filename] = file_patterns.get(filename, 0) + 1
        
        return file_patterns
    
    def _group_repos_by_patterns(
        self,
        repo_files: Dict[Repository, List[str]],
        file_patterns: Dict[str, int]
    ) -> List[List[Repository]]:
        """Group repositories by similar file patterns for optimized processing.
        
        Args:
            repo_files: Dictionary mapping repositories to lists of file paths
            file_patterns: File pattern frequency analysis
            
        Returns:
            List of repository groups for optimized processing
        """
        # For now, use a simple grouping strategy
        # In the future, this could be enhanced with more sophisticated algorithms
        
        # Group repositories by the number of files they have
        size_groups = {}
        for repo, file_paths in repo_files.items():
            file_count = len(file_paths)
            size_key = min(file_count // 5, 10)  # Group by file count ranges
            
            if size_key not in size_groups:
                size_groups[size_key] = []
            size_groups[size_key].append(repo)
        
        # Return groups as a list
        return list(size_groups.values())
    
    async def close(self) -> None:
        """Close the async HTTP client."""
        if self.client and not self.client.is_closed:
            await self.client.aclose()
    
    async def __aenter__(self) -> "AsyncGitHubClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()