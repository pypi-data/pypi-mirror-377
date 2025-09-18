"""GitHub API client with authentication and rate limiting."""

import asyncio
import base64
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
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
from .batch_models import BatchRequest, BatchResult, BatchConfig

logger = get_logger(__name__)


class GitHubClient:
    """Client for interacting with the GitHub API with rate limiting and ETag support."""

    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None, config: Optional[BatchConfig] = None) -> None:
        """Initialize the GitHub client with authentication token.
        
        Args:
            token: GitHub personal access token. If None, will attempt auto-discovery.
            config: Batch processing configuration
        """
        self.token = token or self._discover_token()
        self.config = config or BatchConfig()
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "github-ioc-scanner/0.1.0",
            },
            timeout=30.0,
        )
        # Async client for batch operations
        self._async_client: Optional[httpx.AsyncClient] = None
        self._async_client_lock = asyncio.Lock()
        
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
    
    def _make_request(
        self, 
        method: str, 
        url: str, 
        etag: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> APIResponse:
        """Make a request to the GitHub API with rate limiting and ETag support."""
        headers = kwargs.pop("headers", {})
        
        # Add ETag for conditional requests
        if etag:
            headers["If-None-Match"] = etag
            
        try:
            response = self.client.request(method, url, headers=headers, params=params, **kwargs)
            
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
    
    def _handle_rate_limit(self, reset_time: int) -> None:
        """Handle rate limiting with exponential backoff."""
        current_time = int(time.time())
        wait_time = max(reset_time - current_time, 60)  # Wait at least 1 minute
        
        logger.warning(f"Rate limit exceeded. Waiting {wait_time} seconds until {datetime.fromtimestamp(reset_time)}")
        
        # Use exponential backoff with jitter for additional requests
        base_wait = min(wait_time, 300)  # Cap at 5 minutes
        jitter = base_wait * 0.1  # 10% jitter
        actual_wait = base_wait + (jitter * (0.5 - hash(str(time.time())) % 100 / 100))
        
        try:
            time.sleep(actual_wait)
        except KeyboardInterrupt:
            logger.info("Rate limit wait interrupted by user")
            raise

    def get_organization_repos(
        self, org: str, include_archived: bool = False, etag: Optional[str] = None
    ) -> APIResponse:
        """Get all repositories for an organization.
        
        Args:
            org: Organization name
            include_archived: Whether to include archived repositories
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing list of Repository objects
            
        Raises:
            OrganizationNotFoundError: If the organization doesn't exist or is inaccessible
            AuthenticationError: If authentication fails
            NetworkError: If network operations fail
        """
        try:
            url = f"/orgs/{quote(org)}/repos"
            params = {
                "type": "all",
                "per_page": 100,
                "sort": "updated",
            }
            
            all_repos = []
            page = 1
            
            while True:
                params["page"] = page
                response = self._make_request("GET", url, etag=etag if page == 1 else None, params=params)
                
                if response.not_modified and page == 1:
                    return response
                    
                if not response.data:
                    # Empty response could mean organization not found or no repos
                    if page == 1:
                        raise OrganizationNotFoundError(org)
                    break
                    
                repos_data = response.data
                if not repos_data:
                    break
                    
                try:
                    for repo_data in repos_data:
                        if not include_archived and repo_data.get("archived", False):
                            continue
                            
                        repo = Repository(
                            name=repo_data["name"],
                            full_name=repo_data["full_name"],
                            archived=repo_data.get("archived", False),
                            default_branch=repo_data.get("default_branch", "main"),
                            updated_at=datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00")),
                        )
                        all_repos.append(repo)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Malformed repository data in organization {org}: {e}")
                    continue
                
                # Check if there are more pages
                if len(repos_data) < params["per_page"]:
                    break
                    
                page += 1
            
            logger.info(f"Retrieved {len(all_repos)} repositories for organization {org}")
            
            return APIResponse(
                data=all_repos,
                etag=response.etag,
                not_modified=False,
                rate_limit_remaining=response.rate_limit_remaining,
                rate_limit_reset=response.rate_limit_reset,
            )
            
        except (OrganizationNotFoundError, AuthenticationError, NetworkError):
            raise
        except Exception as e:
            log_exception(logger, f"Failed to get repositories for organization {org}", e)
            raise wrap_exception(e, f"Failed to get repositories for organization {org}")

    def get_team_repos(
        self, org: str, team: str, etag: Optional[str] = None
    ) -> APIResponse:
        """Get repositories for a specific team.
        
        Args:
            org: Organization name
            team: Team slug
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing list of Repository objects
            
        Raises:
            TeamNotFoundError: If the team doesn't exist or is inaccessible
            OrganizationNotFoundError: If the organization doesn't exist
            AuthenticationError: If authentication fails
            NetworkError: If network operations fail
        """
        try:
            url = f"/orgs/{quote(org)}/teams/{quote(team)}/repos"
            params = {"per_page": 100}
            
            all_repos = []
            page = 1
            
            while True:
                params["page"] = page
                response = self._make_request("GET", url, etag=etag if page == 1 else None, params=params)
                
                if response.not_modified and page == 1:
                    return response
                    
                if not response.data:
                    # Empty response could mean team not found or no repos
                    if page == 1:
                        raise TeamNotFoundError(org, team)
                    break
                    
                repos_data = response.data
                if not repos_data:
                    break
                    
                try:
                    for repo_data in repos_data:
                        repo = Repository(
                            name=repo_data["name"],
                            full_name=repo_data["full_name"],
                            archived=repo_data.get("archived", False),
                            default_branch=repo_data.get("default_branch", "main"),
                            updated_at=datetime.fromisoformat(repo_data["updated_at"].replace("Z", "+00:00")),
                        )
                        all_repos.append(repo)
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Malformed repository data for team {org}/{team}: {e}")
                    continue
                
                # Check if there are more pages
                if len(repos_data) < params["per_page"]:
                    break
                    
                page += 1
            
            logger.info(f"Retrieved {len(all_repos)} repositories for team {org}/{team}")
            
            return APIResponse(
                data=all_repos,
                etag=response.etag,
                not_modified=False,
                rate_limit_remaining=response.rate_limit_remaining,
                rate_limit_reset=response.rate_limit_reset,
            )
            
        except (TeamNotFoundError, OrganizationNotFoundError, AuthenticationError, NetworkError):
            raise
        except Exception as e:
            log_exception(logger, f"Failed to get repositories for team {org}/{team}", e)
            raise wrap_exception(e, f"Failed to get repositories for team {org}/{team}")

    def search_files(self, repo: Repository, patterns: List[str], fast_mode: bool = False) -> List[FileInfo]:
        """Search for files matching patterns in a repository using Code Search API with Tree API fallback.
        
        Args:
            repo: Repository to search in
            patterns: List of filename patterns to search for
            fast_mode: If True, only search root-level files
            
        Returns:
            List of FileInfo objects for matching files
            
        Raises:
            RepositoryNotFoundError: If the repository doesn't exist or is inaccessible
            NetworkError: If network operations fail
        """
        try:
            files = []
            
            # Try Code Search API first
            try:
                files = self._search_files_code_api(repo, patterns)
                if files:
                    logger.debug(f"Found {len(files)} files using Code Search API in {repo.full_name}")
                    return files
            except (NetworkError, AuthenticationError):
                raise
            except Exception as e:
                logger.warning(f"Code Search API failed for {repo.full_name}: {e}")
            
            # Fallback to Tree API if Code Search fails or returns no results
            logger.debug(f"Falling back to Tree API for {repo.full_name}")
            return self._search_files_tree_api(repo, patterns, fast_mode)
            
        except (RepositoryNotFoundError, NetworkError, AuthenticationError):
            raise
        except Exception as e:
            log_exception(logger, f"Failed to search files in repository {repo.full_name}", e)
            raise wrap_exception(e, f"Failed to search files in repository {repo.full_name}")

    def _search_files_code_api(self, repo: Repository, patterns: List[str]) -> List[FileInfo]:
        """Search for files using GitHub Code Search API."""
        files = []
        
        try:
            for pattern in patterns:
                # Use GitHub Code Search API
                url = "/search/code"
                params = {
                    "q": f"filename:{pattern} repo:{repo.full_name}",
                    "per_page": 100,
                }
                
                page = 1
                while True:
                    params["page"] = page
                    response = self._make_request("GET", url, params=params)
                    
                    if not response.data:
                        break
                        
                    search_data = response.data
                    items = search_data.get("items", [])
                    
                    if not items:
                        break
                        
                    try:
                        for item in items:
                            file_info = FileInfo(
                                path=item["path"],
                                sha=item["sha"],
                                size=item.get("size", 0),
                            )
                            files.append(file_info)
                    except (KeyError, TypeError) as e:
                        logger.warning(f"Malformed search result for pattern {pattern} in {repo.full_name}: {e}")
                        continue
                    
                    # Check if there are more pages
                    if len(items) < params["per_page"]:
                        break
                        
                    page += 1
            
            return files
            
        except RateLimitError as e:
            # Rate limit errors are expected and handled gracefully
            logger.warning(f"Code Search API failed for {repo.full_name}: {e}")
            raise
        except Exception as e:
            log_exception(logger, f"Code Search API error for {repo.full_name}", e)
            raise

    def _search_files_tree_api(self, repo: Repository, patterns: List[str], fast_mode: bool = False) -> List[FileInfo]:
        """Search for files using GitHub Tree API as fallback."""
        try:
            # Get the complete tree
            tree_response = self.get_tree(repo)
            if not tree_response.data:
                logger.debug(f"No tree data available for {repo.full_name}")
                return []
            
            all_files = tree_response.data
            matching_files = []
            
            for file_info in all_files:
                try:
                    # In fast mode, only check root-level files
                    if fast_mode and "/" in file_info.path:
                        continue
                        
                    # Check if file matches any pattern
                    filename = file_info.path.split("/")[-1]  # Get just the filename
                    for pattern in patterns:
                        if self._matches_pattern(filename, pattern):
                            matching_files.append(file_info)
                            break
                except (AttributeError, TypeError) as e:
                    logger.warning(f"Invalid file info in tree for {repo.full_name}: {e}")
                    continue
            
            return matching_files
            
        except Exception as e:
            log_exception(logger, f"Tree API error for {repo.full_name}", e)
            raise

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if a filename matches a pattern."""
        # Simple pattern matching - can be enhanced with glob patterns later
        if "*" in pattern:
            # Basic wildcard support
            import fnmatch
            return fnmatch.fnmatch(filename, pattern)
        else:
            # Exact match
            return filename == pattern

    def get_file_content(
        self, repo: Repository, path: str, etag: Optional[str] = None
    ) -> APIResponse:
        """Get the content of a specific file.
        
        Args:
            repo: Repository containing the file
            path: Path to the file
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing FileContent object
            
        Raises:
            RepositoryNotFoundError: If the repository doesn't exist
            NetworkError: If network operations fail
        """
        try:
            url = f"/repos/{quote(repo.full_name)}/contents/{quote(path, safe='/')}"
            response = self._make_request("GET", url, etag=etag)
            
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

    def get_multiple_file_contents(self, repo: Repository, file_paths: List[str]) -> Dict[str, 'FileContent']:
        """Get content for multiple files using GitHub's Tree API for better performance.
        
        This method uses the Git Tree API to get multiple files in fewer API calls,
        which is much more efficient than individual file content requests.
        
        Args:
            repo: Repository containing the files
            file_paths: List of file paths to fetch
            
        Returns:
            Dictionary mapping file paths to FileContent objects
        """
        if not file_paths:
            return {}
        
        try:
            # Get the repository tree
            tree_response = self.get_tree(repo)
            if not tree_response.data:
                return {}
            
            tree_files = tree_response.data
            
            # Create a mapping of path to tree entry
            tree_map = {file_info.path: file_info for file_info in tree_files}
            
            # Batch file content requests using Git Blob API
            file_contents = {}
            
            for file_path in file_paths:
                if file_path in tree_map:
                    file_info = tree_map[file_path]
                    try:
                        # Use Git Blob API to get file content by SHA
                        blob_content = self._get_blob_content(repo, file_info.sha)
                        if blob_content:
                            file_contents[file_path] = FileContent(
                                content=blob_content,
                                sha=file_info.sha,
                                size=file_info.size
                            )
                    except Exception as e:
                        logger.warning(f"Failed to get blob content for {repo.full_name}/{file_path}: {e}")
                        continue
            
            return file_contents
            
        except Exception as e:
            logger.warning(f"Batch file content fetch failed for {repo.full_name}: {e}")
            return {}
    
    def _get_blob_content(self, repo: Repository, sha: str) -> Optional[str]:
        """Get blob content by SHA using Git Blob API."""
        try:
            url = f"/repos/{quote(repo.full_name)}/git/blobs/{sha}"
            response = self._make_request("GET", url)
            
            if not response.data:
                return None
            
            blob_data = response.data
            content = blob_data.get('content', '')
            encoding = blob_data.get('encoding', 'base64')
            
            if encoding == 'base64':
                import base64
                try:
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    return decoded_content
                except (UnicodeDecodeError, ValueError) as e:
                    logger.warning(f"Failed to decode blob {sha}: {e}")
                    return None
            else:
                # Assume it's already text
                return content
                
        except Exception as e:
            logger.warning(f"Failed to get blob content for SHA {sha}: {e}")
            return None

    def get_tree(self, repo: Repository, etag: Optional[str] = None) -> APIResponse:
        """Get the Git tree for a repository.
        
        Args:
            repo: Repository to get tree for
            etag: ETag for conditional requests
            
        Returns:
            APIResponse containing list of FileInfo objects
        """
        url = f"/repos/{quote(repo.full_name)}/git/trees/{repo.default_branch}"
        params = {"recursive": "1"}
        
        response = self._make_request("GET", url, etag=etag, params=params)
        
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
    
    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        async with self._async_client_lock:
            if self._async_client is None or self._async_client.is_closed:
                self._async_client = httpx.AsyncClient(
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
            return self._async_client

    async def get_multiple_file_contents_async(
        self,
        repo: Repository,
        file_paths: List[str],
        max_concurrent: Optional[int] = None
    ) -> Dict[str, FileContent]:
        """Get multiple file contents with async parallel processing.
        
        Args:
            repo: Repository containing the files
            file_paths: List of file paths to fetch
            max_concurrent: Maximum concurrent requests
            
        Returns:
            Dictionary mapping file paths to FileContent objects
        """
        if not file_paths:
            return {}
        
        max_concurrent = max_concurrent or self.config.max_concurrent_requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        try:
            # Get the repository tree first
            tree_response = await self.get_tree_async(repo)
            if not tree_response.data:
                return {}
            
            tree_files = tree_response.data
            
            # Create a mapping of path to tree entry
            tree_map = {file_info.path: file_info for file_info in tree_files}
            
            # Create tasks for parallel blob fetching
            tasks = []
            for file_path in file_paths:
                if file_path in tree_map:
                    file_info = tree_map[file_path]
                    task = self._fetch_blob_async_with_semaphore(
                        semaphore, repo, file_path, file_info
                    )
                    tasks.append(task)
            
            # Execute all tasks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            file_contents = {}
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch file content: {result}")
                    continue
                
                if result and len(result) == 2:
                    file_path, file_content = result
                    if file_content:
                        file_contents[file_path] = file_content
            
            return file_contents
            
        except Exception as e:
            logger.warning(f"Async parallel file content fetch failed for {repo.full_name}: {e}")
            return {}

    async def _fetch_blob_async_with_semaphore(
        self,
        semaphore: asyncio.Semaphore,
        repo: Repository,
        file_path: str,
        file_info: FileInfo
    ) -> Optional[tuple]:
        """Fetch a single blob with semaphore control."""
        async with semaphore:
            try:
                blob_content = await self._get_blob_content_async(repo, file_info.sha)
                if blob_content:
                    file_content = FileContent(
                        content=blob_content,
                        sha=file_info.sha,
                        size=file_info.size
                    )
                    return (file_path, file_content)
                return None
            except Exception as e:
                logger.warning(f"Failed to get blob content for {repo.full_name}/{file_path}: {e}")
                return None

    async def _get_blob_content_async(self, repo: Repository, sha: str) -> Optional[str]:
        """Get blob content by SHA using Git Blob API asynchronously."""
        try:
            url = f"/repos/{quote(repo.full_name)}/git/blobs/{sha}"
            response = await self._make_async_request("GET", url)
            
            if not response.data:
                return None
            
            blob_data = response.data
            content = blob_data.get('content', '')
            encoding = blob_data.get('encoding', 'base64')
            
            if encoding == 'base64':
                try:
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    return decoded_content
                except (UnicodeDecodeError, ValueError) as e:
                    logger.warning(f"Failed to decode blob {sha}: {e}")
                    return None
            else:
                # Assume it's already text
                return content
                
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
        
        response = await self._make_async_request("GET", url, etag=etag, params=params)
        
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

    async def _make_async_request(
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
            client = await self._get_async_client()
            response = await client.request(method, url, headers=headers, params=params, **kwargs)
            
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
            log_exception(logger, f"Unexpected error making async request to {url}", e)
            raise wrap_exception(e, f"Unexpected error making async request to {url}")

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    async def aclose(self) -> None:
        """Close the async HTTP client."""
        if self._async_client and not self._async_client.is_closed:
            await self._async_client.aclose()
    
    def __enter__(self) -> "GitHubClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "GitHubClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()