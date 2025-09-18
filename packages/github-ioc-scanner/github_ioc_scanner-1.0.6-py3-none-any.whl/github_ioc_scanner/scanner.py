"""Core scanning engine for the GitHub IOC Scanner."""

import asyncio
from typing import Any, Dict, List, Optional

from .async_github_client import AsyncGitHubClient
from .batch_coordinator import BatchCoordinator
from .batch_models import BatchConfig, BatchStrategy
from .cache import CacheManager
from .exceptions import (
    AuthenticationError,
    IOCLoaderError,
    ScanError,
    ConfigurationError,
    UnsupportedFileFormatError,
    ParsingError,
    wrap_exception,
    get_error_context
)
from .github_client import GitHubClient
from .ioc_loader import IOCLoader
from .logging_config import get_logger, log_exception, log_performance
from .models import ScanConfig, ScanResults, Repository, IOCMatch, CacheStats, FileContent, FileInfo
from .parsers.factory import get_parser, parse_file_safely
# Import parsers module to ensure all parsers are registered
from . import parsers

logger = get_logger(__name__)


class GitHubIOCScanner:
    """Main scanner class that orchestrates the scanning workflow."""

    # Common lockfile patterns to search for
    # Base lockfile patterns
    _BASE_LOCKFILE_PATTERNS = [
        "package.json",
        "package-lock.json", 
        "yarn.lock",
        "pnpm-lock.yaml",
        "bun.lockb",
        "requirements.txt",
        "Pipfile.lock",
        "poetry.lock",
        "pyproject.toml",
        "Gemfile.lock",
        "composer.lock",
        "go.mod",
        "go.sum",
        "Cargo.lock",
    ]
    
    # Common subdirectories to check
    _COMMON_SUBDIRS = ['', 'frontend/', 'backend/', 'client/', 'server/', 'web/', 'api/', 'app/', 'src/', 'cdk/']
    
    # Generate full list of patterns including subdirectories
    LOCKFILE_PATTERNS = []
    for subdir in _COMMON_SUBDIRS:
        for pattern in _BASE_LOCKFILE_PATTERNS:
            LOCKFILE_PATTERNS.append(subdir + pattern)

    def __init__(self, config: ScanConfig, github_client: GitHubClient, cache_manager: CacheManager, ioc_loader: Optional[IOCLoader] = None, progress_callback: Optional[callable] = None, batch_config: Optional[BatchConfig] = None, enable_batch_processing: bool = True) -> None:
        """Initialize the scanner with configuration and dependencies."""
        self.config = config
        self.github_client = github_client
        self.cache_manager = cache_manager
        self.ioc_loader = ioc_loader or IOCLoader(config.issues_dir)
        self.progress_callback = progress_callback
        self.enable_batch_processing = enable_batch_processing
        
        # Initialize batch processing components if enabled
        self.batch_coordinator: Optional[BatchCoordinator] = None
        self.async_github_client: Optional[AsyncGitHubClient] = None
        
        if self.enable_batch_processing:
            # Create async GitHub client for batch operations
            self.async_github_client = AsyncGitHubClient(
                token=github_client.token,
                config=batch_config or BatchConfig()
            )
            
            # Initialize batch coordinator with progress callback integration
            self.batch_coordinator = BatchCoordinator(
                github_client=self.async_github_client,
                cache_manager=cache_manager,
                config=batch_config or BatchConfig()
            )
            
            # Configure progress monitoring if callback is provided
            if self.progress_callback:
                self._setup_batch_progress_monitoring()

    def scan(self) -> ScanResults:
        """Execute the scan based on the configuration."""
        # Use batch processing if enabled and multiple repositories
        if self.enable_batch_processing and self.batch_coordinator:
            return asyncio.run(self._scan_with_batch_processing())
        else:
            return self._scan_sequential()
    
    async def _scan_with_batch_processing(self) -> ScanResults:
        """Execute scan using batch processing for improved performance."""
        import time
        start_time = time.time()
        
        try:
            # Validate configuration
            self._validate_scan_config()
            
            # Load IOC definitions
            logger.info("Loading IOC definitions...")
            try:
                ioc_definitions = self.ioc_loader.load_iocs()
                ioc_hash = self.ioc_loader.get_ioc_hash()
                logger.info(f"Loaded IOC definitions from {len(ioc_definitions)} files")
            except IOCLoaderError:
                raise
            except Exception as e:
                log_exception(logger, "Failed to load IOC definitions", e)
                raise wrap_exception(e, "Failed to load IOC definitions", IOCLoaderError)
            
            # Start batch coordinator
            await self.batch_coordinator.start()
            
            try:
                # Discover repositories to scan
                repositories = await self._discover_repositories_batch()
                logger.info(f"Found {len(repositories)} repositories to scan")
                
                if not repositories:
                    return ScanResults(
                        matches=[],
                        cache_stats=self.cache_manager.get_cache_stats(),
                        repositories_scanned=0,
                        files_scanned=0
                    )
                
                # Execute batch scanning workflow with progress monitoring
                batch_results = await self.batch_coordinator.process_repositories_batch(
                    repositories, 
                    strategy=self._select_batch_strategy(repositories),
                    file_patterns=self.LOCKFILE_PATTERNS
                )
                
                # Convert batch results to IOC matches
                all_matches = []
                successful_repos = len(batch_results)  # All repositories that were processed
                total_files_scanned = 0
                
                for repo_name, matches in batch_results.items():
                    if matches:
                        all_matches.extend(matches)
                
                # Get actual number of files processed from batch coordinator
                total_files_scanned = self.batch_coordinator.get_total_files_processed() if self.batch_coordinator else len(batch_results)

                
                scan_duration = time.time() - start_time
                log_performance(
                    logger, "batch_scan", scan_duration,
                    repositories=len(repositories),
                    successful=successful_repos,
                    failed=len(repositories) - successful_repos,
                    matches=len(all_matches),
                    files=total_files_scanned
                )
                
                # Get batch metrics for additional insights
                batch_metrics = await self.batch_coordinator.get_batch_metrics()
                logger.info(f"Batch scan completed: {len(all_matches)} matches, "
                          f"{batch_metrics.cache_hit_rate:.1f}% cache hit rate, "
                          f"{batch_metrics.parallel_efficiency:.2f} parallel efficiency")
                
                return ScanResults(
                    matches=all_matches,
                    cache_stats=self.cache_manager.get_cache_stats(),
                    repositories_scanned=successful_repos,
                    files_scanned=total_files_scanned
                )
                
            finally:
                # Always stop batch coordinator
                await self.batch_coordinator.stop()
                
        except (AuthenticationError, IOCLoaderError, ConfigurationError, ScanError):
            raise
        except Exception as e:
            log_exception(logger, "Unexpected error during batch scan", e)
            raise wrap_exception(e, "Unexpected error during batch scan", ScanError)
    
    def _scan_sequential(self) -> ScanResults:
        """Execute scan using sequential processing (original implementation)."""
        import time
        start_time = time.time()
        
        try:
            # Validate configuration
            self._validate_scan_config()
            
            # Load IOC definitions
            logger.info("Loading IOC definitions...")
            try:
                ioc_definitions = self.ioc_loader.load_iocs()
                ioc_hash = self.ioc_loader.get_ioc_hash()
                logger.info(f"Loaded IOC definitions from {len(ioc_definitions)} files")
            except IOCLoaderError:
                raise
            except Exception as e:
                log_exception(logger, "Failed to load IOC definitions", e)
                raise wrap_exception(e, "Failed to load IOC definitions", IOCLoaderError)
            
            # Discover repositories to scan
            repositories = []
            try:
                if self.config.org and self.config.team:
                    # Scan team repositories
                    repositories = self.discover_team_repositories(self.config.org, self.config.team)
                elif self.config.org and self.config.repo:
                    # Scan specific repository
                    repo = Repository(
                        name=self.config.repo,
                        full_name=f"{self.config.org}/{self.config.repo}",
                        archived=False,  # We'll fetch actual data if needed
                        default_branch="main",  # Will be updated when we fetch repo data
                        updated_at=None
                    )
                    repositories = [repo]
                elif self.config.org:
                    # Scan organization repositories
                    repositories = self.discover_organization_repositories(self.config.org)
                else:
                    raise ConfigurationError("Must specify at least --org parameter")
                    
                logger.info(f"Found {len(repositories)} repositories to scan")
                
            except (AuthenticationError, IOCLoaderError, ConfigurationError):
                raise
            except Exception as e:
                log_exception(logger, "Failed to discover repositories", e)
                raise wrap_exception(e, "Failed to discover repositories", ScanError)
            
            # Scan repositories for IOCs
            all_matches = []
            total_files_scanned = 0
            successful_repos = 0
            failed_repos = 0
            total_repos = len(repositories)
            scan_start_time = start_time  # Use the same start time for ETA calculation
            
            for i, repo in enumerate(repositories, 1):
                try:
                    # Update progress
                    if self.progress_callback:
                        self.progress_callback(i, total_repos, repo.full_name, scan_start_time)
                    
                    logger.info(f"Scanning repository: {repo.full_name}")
                    repo_matches, files_scanned = self.scan_repository_for_iocs(repo, ioc_hash)
                    all_matches.extend(repo_matches)
                    total_files_scanned += files_scanned
                    successful_repos += 1
                    
                    if repo_matches:
                        logger.info(f"Found {len(repo_matches)} IOC matches in {repo.full_name}")
                    else:
                        logger.debug(f"No IOC matches found in {repo.full_name}")
                        
                except Exception as e:
                    failed_repos += 1
                    logger.error(f"Failed to scan repository {repo.full_name}: {e}")
                    # Continue with other repositories instead of failing completely
                    continue
            
            scan_duration = time.time() - start_time
            log_performance(
                logger, "sequential_scan", scan_duration,
                repositories=len(repositories),
                successful=successful_repos,
                failed=failed_repos,
                matches=len(all_matches),
                files=total_files_scanned
            )
            
            if failed_repos > 0:
                logger.warning(f"Scan completed with {failed_repos} failed repositories out of {len(repositories)} total")
            else:
                logger.info(f"Scan completed successfully: {len(all_matches)} total matches found across {total_files_scanned} files")
            
            return ScanResults(
                matches=all_matches,
                cache_stats=self.cache_manager.get_cache_stats(),
                repositories_scanned=successful_repos,
                files_scanned=total_files_scanned
            )
            
        except (AuthenticationError, IOCLoaderError, ConfigurationError, ScanError):
            raise
        except Exception as e:
            log_exception(logger, "Unexpected error during scan", e)
            raise wrap_exception(e, "Unexpected error during scan", ScanError)

    def _validate_scan_config(self) -> None:
        """Validate scan configuration parameters."""
        # Team requires organization context
        if self.config.team and not self.config.org:
            raise ConfigurationError("Team scanning requires organization context. Use --org parameter with --team.")
        
        # Repository requires organization context
        if self.config.repo and not self.config.org:
            raise ConfigurationError("Repository scanning requires organization context. Use --org parameter with --repo.")
        
        # Validate issues directory (None means use built-in IOCs)
        if self.config.issues_dir is not None and not self.config.issues_dir.strip():
            raise ConfigurationError("Issues directory path cannot be empty")

    def discover_organization_repositories(self, org: str) -> List[Repository]:
        """Discover all repositories in an organization with caching."""
        logger.info(f"Discovering repositories for organization: {org}")
        
        # Check cache first
        cached_data = self.cache_manager.get_repository_metadata(org)
        etag = None
        
        if cached_data:
            repositories, etag = cached_data
            logger.debug(f"Found {len(repositories)} cached repositories for {org}")
        
        # Make API request with ETag for conditional request
        response = self.github_client.get_organization_repos(
            org, 
            include_archived=self.config.include_archived,
            etag=etag
        )
        
        if response.not_modified and cached_data:
            # Use cached data
            repositories, _ = cached_data
            logger.debug(f"Repository list for {org} not modified, using cache")
        elif response.data:
            # Update cache with new data
            repositories = response.data
            self.cache_manager.store_repository_metadata(org, repositories, response.etag)
            logger.info(f"Discovered {len(repositories)} repositories for {org}")
        else:
            logger.warning(f"No repositories found for organization {org}")
            return []
        
        # Filter archived repositories if not included
        if not self.config.include_archived:
            repositories = [repo for repo in repositories if not repo.archived]
            logger.debug(f"Filtered to {len(repositories)} non-archived repositories")
        
        return repositories
    
    async def discover_organization_repositories_batch(self, org: str) -> List[Repository]:
        """Discover all repositories in an organization using batch processing."""
        logger.info(f"Batch discovering repositories for organization: {org}")
        
        if not self.batch_coordinator:
            # Fallback to sequential discovery
            return self.discover_organization_repositories(org)
        
        try:
            # Use batch coordinator's organization discovery
            repositories = await self.batch_coordinator._discover_organization_repositories(
                org, repository_filter=None, max_repositories=None
            )
            
            # Filter archived repositories if not included
            if not self.config.include_archived:
                repositories = [repo for repo in repositories if not repo.archived]
                logger.debug(f"Filtered to {len(repositories)} non-archived repositories")
            
            logger.info(f"Batch discovered {len(repositories)} repositories for {org}")
            return repositories
            
        except Exception as e:
            logger.warning(f"Batch repository discovery failed, falling back to sequential: {e}")
            return self.discover_organization_repositories(org)

    def discover_team_repositories(self, org: str, team: str) -> List[Repository]:
        """Discover repositories belonging to a specific team with caching."""
        logger.info(f"Discovering repositories for team: {org}/{team}")
        
        # Check cache first
        cached_data = self.cache_manager.get_repository_metadata(org, team)
        etag = None
        
        if cached_data:
            repositories, etag = cached_data
            logger.debug(f"Found {len(repositories)} cached repositories for team {org}/{team}")
        
        # Make API request with ETag for conditional request
        response = self.github_client.get_team_repos(org, team, etag=etag)
        
        if response.not_modified and cached_data:
            # Use cached data
            repositories, _ = cached_data
            logger.debug(f"Repository list for team {org}/{team} not modified, using cache")
        elif response.data:
            # Update cache with new data
            repositories = response.data
            self.cache_manager.store_repository_metadata(org, repositories, response.etag, team)
            logger.info(f"Discovered {len(repositories)} repositories for team {org}/{team}")
        else:
            logger.warning(f"No repositories found for team {org}/{team}")
            return []
        
        return repositories
    
    async def discover_team_repositories_batch(self, org: str, team: str) -> List[Repository]:
        """Discover repositories belonging to a specific team using batch processing."""
        logger.info(f"🔍 Discovering repositories for team: {org}/{team}...")
        
        if not self.batch_coordinator or not self.async_github_client:
            # Fallback to sequential discovery
            return self.discover_team_repositories(org, team)
        
        try:
            # For now, use the async GitHub client directly for team repositories
            # In a full implementation, this would be optimized with batch processing
            repositories = await self._discover_team_repositories_async(org, team)
            
            logger.info(f"✅ Found {len(repositories)} repositories for team {org}/{team}")
            return repositories
            
        except Exception as e:
            logger.warning(f"Batch team repository discovery failed, falling back to sequential: {e}")
            return self.discover_team_repositories(org, team)
    
    async def _discover_team_repositories_async(self, org: str, team: str) -> List[Repository]:
        """Async helper for team repository discovery."""
        # This is a simplified implementation - in practice, this would use
        # the async GitHub client's team repository discovery methods
        # For now, we'll simulate with the existing sync method
        return self.discover_team_repositories(org, team)

    def discover_files_in_repository(self, repo: Repository) -> List[str]:
        """Discover relevant files in a repository using Code Search with Tree API fallback."""
        logger.debug(f"Discovering files in repository: {repo.full_name}")
        
        try:
            files = self.github_client.search_files(
                repo, 
                self.LOCKFILE_PATTERNS, 
                fast_mode=self.config.fast_mode
            )
            
            file_paths = [f.path for f in files]
            logger.debug(f"Found {len(file_paths)} relevant files in {repo.full_name}")
            
            return file_paths
            
        except Exception as e:
            logger.error(f"Failed to discover files in {repo.full_name}: {e}")
            return []
    
    async def discover_files_in_repository_batch(self, repo: Repository) -> List[str]:
        """Discover relevant files in a repository using batch processing."""
        logger.debug(f"Batch discovering files in repository: {repo.full_name}")
        
        if not self.batch_coordinator:
            # Fallback to sequential discovery
            return self.discover_files_in_repository(repo)
        
        try:
            # Use batch coordinator for file discovery (this uses the repaired Tree API logic)
            files = await self.batch_coordinator._discover_repository_files(repo, self.LOCKFILE_PATTERNS)
            
            logger.debug(f"Batch found {len(files)} relevant files in {repo.full_name}")
            
            return files
            
        except Exception as e:
            logger.warning(f"Batch file discovery failed, falling back to sequential: {e}")
            return self.discover_files_in_repository(repo)
    
    async def _discover_files_async(self, repo: Repository) -> List[FileInfo]:
        """Async helper for file discovery."""
        # This is a simplified implementation - in practice, this would use
        # the async GitHub client's file search methods
        # For now, we'll simulate with the existing sync method
        files = self.github_client.search_files(
            repo, 
            self.LOCKFILE_PATTERNS, 
            fast_mode=self.config.fast_mode
        )
        return files
    
    async def discover_files_in_repositories_batch(self, repositories: List[Repository]) -> Dict[str, List[str]]:
        """Discover relevant files across multiple repositories using batch processing."""
        logger.info(f"Batch discovering files across {len(repositories)} repositories")
        
        if not self.batch_coordinator:
            # Fallback to sequential discovery
            result = {}
            for repo in repositories:
                result[repo.full_name] = self.discover_files_in_repository(repo)
            return result
        
        try:
            # Use batch processing for file discovery across repositories
            result = {}
            
            # Process repositories in batches for optimal performance
            batch_size = min(5, len(repositories))  # Process up to 5 repos at once
            
            for i in range(0, len(repositories), batch_size):
                batch_repos = repositories[i:i + batch_size]
                
                # Discover files for this batch of repositories
                batch_tasks = [
                    self.discover_files_in_repository_batch(repo) 
                    for repo in batch_repos
                ]
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Process results
                for repo, files in zip(batch_repos, batch_results):
                    if isinstance(files, Exception):
                        logger.warning(f"Failed to discover files in {repo.full_name}: {files}")
                        result[repo.full_name] = []
                    else:
                        result[repo.full_name] = files
            
            total_files = sum(len(files) for files in result.values())
            logger.info(f"Batch discovered {total_files} total files across {len(repositories)} repositories")
            
            return result
            
        except Exception as e:
            logger.error(f"Batch file discovery across repositories failed: {e}")
            # Fallback to sequential processing
            result = {}
            for repo in repositories:
                result[repo.full_name] = self.discover_files_in_repository(repo)
            return result

    def scan_organization(self, org: str) -> List[Repository]:
        """Scan all repositories in an organization."""
        return self.discover_organization_repositories(org)

    def scan_team(self, org: str, team: str) -> List[Repository]:
        """Scan repositories belonging to a specific team."""
        return self.discover_team_repositories(org, team)

    def scan_repository_for_iocs(self, repo: Repository, ioc_hash: str) -> tuple[List[IOCMatch], int]:
        """Scan a repository for IOC matches.
        
        Args:
            repo: Repository to scan
            ioc_hash: Hash of IOC definitions for cache invalidation
            
        Returns:
            Tuple of (IOC matches found, number of files scanned)
        """
        try:
            # Discover relevant files in the repository
            file_paths = self.discover_files_in_repository(repo)
            
            if not file_paths:
                logger.debug(f"No relevant files found in {repo.full_name}")
                return [], 0
            
            logger.debug(f"Found {len(file_paths)} files to scan in {repo.full_name}")
            
            all_matches = []
            files_scanned = 0
            
            for file_path in file_paths:
                try:
                    matches = self.scan_file_for_iocs(repo, file_path, ioc_hash)
                    all_matches.extend(matches)
                    files_scanned += 1
                    
                    if matches:
                        logger.debug(f"Found {len(matches)} IOC matches in {repo.full_name}/{file_path}")
                        
                except Exception as e:
                    logger.warning(f"Failed to scan file {repo.full_name}/{file_path}: {e}")
                    continue
            
            return all_matches, files_scanned
            
        except Exception as e:
            logger.error(f"Failed to scan repository {repo.full_name}: {e}")
            return [], 0

    def scan_file_for_iocs(self, repo: Repository, file_path: str, ioc_hash: str) -> List[IOCMatch]:
        """Scan a single file for IOC matches with caching.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file within the repository
            ioc_hash: Hash of IOC definitions for cache invalidation
            
        Returns:
            List of IOC matches found in the file
        """
        try:
            # First, get file content with ETag conditional requests
            file_content = self.fetch_file_content_with_cache(repo, file_path)
            
            if not file_content:
                logger.debug(f"Could not fetch content for {repo.full_name}/{file_path}")
                return []
            
            # Check cache for scan results first
            cached_results = self.cache_manager.get_scan_results(
                repo.full_name, file_path, file_content.sha, ioc_hash
            )
            
            if cached_results is not None:
                logger.debug(f"Using cached scan results for {repo.full_name}/{file_path}")
                return cached_results
            
            # Parse packages from file content
            packages = self.parse_packages_with_cache(repo, file_path, file_content)
            
            if not packages:
                # Cache empty results to avoid re-parsing
                self.cache_manager.store_scan_results(
                    repo.full_name, file_path, file_content.sha, ioc_hash, []
                )
                return []
            
            # Match packages against IOC definitions
            matches = self.match_packages_against_iocs(repo, file_path, packages)
            
            # Cache the scan results
            self.cache_manager.store_scan_results(
                repo.full_name, file_path, file_content.sha, ioc_hash, matches
            )
            
            return matches
            
        except Exception as e:
            logger.warning(f"Error scanning file {repo.full_name}/{file_path}: {e}")
            return []

    def fetch_file_content_with_cache(self, repo: Repository, file_path: str) -> Optional[FileContent]:
        """Fetch file content with ETag conditional requests and caching.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file within the repository
            
        Returns:
            FileContent object if successful, None otherwise
        """
        try:
            # Check if we have cached content first
            # We need the SHA to check cache, so we'll get it from the API response
            
            # Get ETag from cache for conditional request
            etag_key = f"file:{repo.full_name}/{file_path}"
            cached_etag = self.cache_manager.get_etag(etag_key)
            
            # Make API request with conditional ETag
            response = self.github_client.get_file_content(repo, file_path, etag=cached_etag)
            
            if response.not_modified:
                # File hasn't changed, but we need to get cached content
                # Since we don't have SHA from 304 response, we need to handle this differently
                logger.debug(f"File {repo.full_name}/{file_path} not modified, but need cached content")
                # For now, we'll make a fresh request if we get 304 but don't have cached content
                # This is a limitation we can optimize later
                response = self.github_client.get_file_content(repo, file_path)
            
            if not response.data:
                return None
            
            file_content = response.data
            
            # Check cache for existing content with this SHA
            cached_content = self.cache_manager.get_file_content(
                repo.full_name, file_path, file_content.sha
            )
            
            if cached_content is None:
                # Store new content in cache
                self.cache_manager.store_file_content(
                    repo.full_name, file_path, file_content.sha, 
                    file_content.content, response.etag
                )
            
            # Store/update ETag for future conditional requests
            if response.etag:
                self.cache_manager.store_etag(etag_key, response.etag)
            
            return file_content
            
        except Exception as e:
            logger.warning(f"Failed to fetch content for {repo.full_name}/{file_path}: {e}")
            return None

    def parse_packages_with_cache(self, repo: Repository, file_path: str, file_content: FileContent) -> List:
        """Parse packages from file content with caching.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file within the repository
            file_content: Content of the file to parse
            
        Returns:
            List of PackageDependency objects
        """
        try:
            # Check cache for parsed packages
            cached_packages = self.cache_manager.get_parsed_packages(
                repo.full_name, file_path, file_content.sha
            )
            
            if cached_packages is not None:
                logger.debug(f"Using cached parsed packages for {repo.full_name}/{file_path}")
                return cached_packages
            
            # Parse packages using the safe parser
            try:
                packages = parse_file_safely(file_path, file_content.content)
                
                # Cache the parsed packages
                self.cache_manager.store_parsed_packages(
                    repo.full_name, file_path, file_content.sha, packages
                )
                
                logger.debug(f"Parsed {len(packages)} packages from {repo.full_name}/{file_path}")
                return packages
                
            except UnsupportedFileFormatError:
                # This is expected for unknown file formats - log as debug, not warning
                logger.debug(f"No parser available for {file_path}")
                return []
            except ParsingError as e:
                # Log parsing errors as warnings but continue
                logger.warning(f"Failed to parse {repo.full_name}/{file_path}: {e.message}")
                return []
            
        except Exception as e:
            log_exception(logger, f"Unexpected error parsing packages from {repo.full_name}/{file_path}", e)
            return []

    def match_packages_against_iocs(self, repo: Repository, file_path: str, packages: List) -> List[IOCMatch]:
        """Match parsed packages against IOC definitions.
        
        Args:
            repo: Repository containing the file
            file_path: Path to the file within the repository
            packages: List of PackageDependency objects to check
            
        Returns:
            List of IOCMatch objects for compromised packages found
        """
        matches = []
        
        try:
            # Get all IOC packages
            all_ioc_packages = self.ioc_loader.get_all_packages()
            
            for package in packages:
                if self.ioc_loader.is_package_compromised(package.name, package.version):
                    # Find which IOC definition matched
                    ioc_source = "unknown"
                    for source_file, ioc_def in self.ioc_loader._ioc_definitions.items():
                        if package.name in ioc_def.packages:
                            ioc_source = source_file
                            break
                    
                    match = IOCMatch(
                        repo=repo.full_name,
                        file_path=file_path,
                        package_name=package.name,
                        version=package.version,
                        ioc_source=ioc_source
                    )
                    matches.append(match)
                    
                    logger.debug(f"IOC match: {package.name}@{package.version} in {repo.full_name}/{file_path}")
            
        except Exception as e:
            logger.warning(f"Error matching packages against IOCs for {repo.full_name}/{file_path}: {e}")
        
        return matches

    async def _discover_repositories_batch(self) -> List[Repository]:
        """Discover repositories using batch-optimized methods."""
        repositories = []
        
        if self.config.org and self.config.team:
            # Scan team repositories using batch processing
            repositories = await self.discover_team_repositories_batch(self.config.org, self.config.team)
        elif self.config.org and self.config.repo:
            # Scan specific repository
            repo = Repository(
                name=self.config.repo,
                full_name=f"{self.config.org}/{self.config.repo}",
                archived=False,  # We'll fetch actual data if needed
                default_branch="main",  # Will be updated when we fetch repo data
                updated_at=None
            )
            repositories = [repo]
        elif self.config.org:
            # Use batch processing for organization discovery
            repositories = await self.discover_organization_repositories_batch(self.config.org)
        else:
            raise ConfigurationError("Must specify at least --org parameter")
        
        return repositories
    
    async def _scan_single_repository_batch(self, repo: Repository, ioc_hash: str) -> List[IOCMatch]:
        """Scan a single repository using batch processing for files."""
        try:
            # Discover files in the repository
            file_paths = self.discover_files_in_repository(repo)
            
            if not file_paths:
                logger.debug(f"No relevant files found in {repo.full_name}")
                return []
            
            # Use batch coordinator to process files
            batch_results = await self.batch_coordinator.process_files_batch(
                repo, file_paths, priority_files=self._get_priority_files(file_paths)
            )
            
            # Process batch results to find IOC matches
            all_matches = []
            for file_path, file_data in batch_results.items():
                if file_data and 'content' in file_data:
                    # Parse packages and check for IOCs
                    matches = await self._process_file_for_iocs_batch(
                        repo, file_path, file_data['content'], ioc_hash
                    )
                    all_matches.extend(matches)
            
            return all_matches
            
        except Exception as e:
            logger.error(f"Failed to batch scan repository {repo.full_name}: {e}")
            return []
    
    def _get_priority_files(self, file_paths: List[str]) -> List[str]:
        """Identify priority files from the list of file paths."""
        priority_patterns = [
            'package.json', 'requirements.txt', 'go.mod', 'Cargo.toml',
            'composer.json', 'Gemfile', 'pyproject.toml'
        ]
        
        priority_files = []
        for file_path in file_paths:
            file_name = file_path.split('/')[-1]  # Get filename from path
            if file_name in priority_patterns:
                priority_files.append(file_path)
        
        return priority_files
    
    async def _process_file_for_iocs_batch(
        self, 
        repo: Repository, 
        file_path: str, 
        content: str, 
        ioc_hash: str
    ) -> List[IOCMatch]:
        """Process a single file for IOC matches in batch context."""
        try:
            # Parse packages from file content
            packages = parse_file_safely(file_path, content)
            
            if not packages:
                return []
            
            # Match packages against IOC definitions
            matches = self.match_packages_against_iocs(repo, file_path, packages)
            return matches
            
        except Exception as e:
            logger.warning(f"Error processing file {repo.full_name}/{file_path} in batch: {e}")
            return []
    
    def _select_batch_strategy(self, repositories: List[Repository]) -> BatchStrategy:
        """Select appropriate batch strategy based on scan characteristics."""
        repo_count = len(repositories)
        
        # Use conservative strategy for team scans to avoid rate limiting issues
        if self.config.team and repo_count > 20:
            logger.info(f"Using conservative strategy for team scan with {repo_count} repositories")
            return BatchStrategy.CONSERVATIVE
        elif repo_count == 1:
            return BatchStrategy.PARALLEL  # Use parallel for single repo file processing
        elif repo_count <= 5:
            return BatchStrategy.ADAPTIVE  # Balanced approach for small sets
        elif repo_count <= 20:
            return BatchStrategy.PARALLEL  # Parallel processing for medium sets
        else:
            return BatchStrategy.AGGRESSIVE  # Aggressive batching for large sets
    
    async def execute_end_to_end_batch_scan(
        self, 
        workflow_config: Optional[Dict[str, Any]] = None
    ) -> ScanResults:
        """Execute a complete end-to-end batch scanning workflow.
        
        Args:
            workflow_config: Optional workflow configuration
            
        Returns:
            Complete scan results with batch processing metrics
        """
        import time
        start_time = time.time()
        
        workflow_config = workflow_config or {}
        
        try:
            # Validate configuration
            self._validate_scan_config()
            
            # Load IOC definitions
            logger.info("Loading IOC definitions for batch workflow...")
            ioc_definitions = self.ioc_loader.load_iocs()
            ioc_hash = self.ioc_loader.get_ioc_hash()
            logger.info(f"Loaded IOC definitions from {len(ioc_definitions)} files")
            
            if not self.batch_coordinator:
                raise ConfigurationError("Batch coordinator not available for end-to-end workflow")
            
            # Start batch coordinator
            await self.batch_coordinator.start()
            
            try:
                # Phase 1: Repository Discovery with Batch Optimization
                logger.info("Phase 1: Batch repository discovery and optimization")
                repositories = await self._discover_repositories_batch()
                
                if not repositories:
                    logger.warning("No repositories found for batch scanning")
                    return ScanResults(
                        matches=[],
                        cache_stats=self.cache_manager.get_cache_stats(),
                        repositories_scanned=0,
                        files_scanned=0
                    )
                
                logger.info(f"Discovered {len(repositories)} repositories for batch processing")
                
                # Phase 2: File Discovery Across All Repositories
                logger.info("Phase 2: Batch file discovery across repositories")
                repository_files = await self.discover_files_in_repositories_batch(repositories)
                
                total_files = sum(len(files) for files in repository_files.values())
                logger.info(f"Discovered {total_files} total files across {len(repositories)} repositories")
                
                # Phase 3: Execute End-to-End Batch Workflow
                logger.info("Phase 3: Executing comprehensive batch workflow")
                
                # Configure workflow parameters
                workflow_params = {
                    'scan_pattern': workflow_config.get('scan_pattern', 'security_scan'),
                    'enable_progress_tracking': workflow_config.get('enable_progress_tracking', True),
                    'enable_performance_monitoring': workflow_config.get('enable_performance_monitoring', True),
                    'file_patterns': self.LOCKFILE_PATTERNS
                }
                
                # Execute the comprehensive batch workflow
                batch_results = await self.batch_coordinator.execute_end_to_end_batch_workflow(
                    repositories, workflow_params
                )
                
                # Phase 4: Process Results and Generate IOC Matches
                logger.info("Phase 4: Processing batch results and generating IOC matches")
                all_matches = await self._process_batch_results_for_iocs(
                    batch_results['processing_results'], ioc_hash
                )
                
                # Phase 5: Compile Comprehensive Results
                logger.info("Phase 5: Compiling comprehensive scan results")
                
                scan_duration = time.time() - start_time
                successful_repos = len([repo for repo, matches in batch_results['processing_results'].items() if matches])
                
                # Get comprehensive metrics
                batch_metrics = await self.batch_coordinator.get_batch_metrics()
                
                # Log comprehensive performance information
                log_performance(
                    logger, "end_to_end_batch_scan", scan_duration,
                    repositories=len(repositories),
                    successful=successful_repos,
                    failed=len(repositories) - successful_repos,
                    matches=len(all_matches),
                    files=total_files,
                    cache_hit_rate=batch_metrics.cache_hit_rate,
                    parallel_efficiency=batch_metrics.parallel_efficiency,
                    api_calls_saved=batch_metrics.api_calls_saved
                )
                
                logger.info(
                    f"End-to-end batch scan completed: {len(all_matches)} IOC matches found, "
                    f"{batch_metrics.cache_hit_rate:.1f}% cache hit rate, "
                    f"{batch_metrics.parallel_efficiency:.2f} parallel efficiency, "
                    f"{batch_metrics.api_calls_saved} API calls saved"
                )
                
                return ScanResults(
                    matches=all_matches,
                    cache_stats=self.cache_manager.get_cache_stats(),
                    repositories_scanned=successful_repos,
                    files_scanned=total_files
                )
                
            finally:
                # Always stop batch coordinator
                await self.batch_coordinator.stop()
                
        except Exception as e:
            log_exception(logger, "End-to-end batch scan failed", e)
            raise wrap_exception(e, "End-to-end batch scan failed", ScanError)
    
    async def _process_batch_results_for_iocs(
        self, 
        batch_results: Dict[str, List[IOCMatch]], 
        ioc_hash: str
    ) -> List[IOCMatch]:
        """Process batch results to extract and validate IOC matches.
        
        Args:
            batch_results: Results from batch processing
            ioc_hash: Hash of IOC definitions for validation
            
        Returns:
            List of validated IOC matches
        """
        all_matches = []
        
        for repo_name, matches in batch_results.items():
            if matches:
                # Validate and add matches
                for match in matches:
                    # Ensure match is properly formatted and valid
                    if isinstance(match, IOCMatch):
                        all_matches.append(match)
                    else:
                        logger.warning(f"Invalid match format in {repo_name}: {match}")
        
        logger.debug(f"Processed {len(all_matches)} total IOC matches from batch results")
        return all_matches
    
    async def execute_organization_batch_scan(
        self, 
        organization: str,
        scan_config: Optional[Dict[str, Any]] = None
    ) -> ScanResults:
        """Execute a complete batch scan for an entire organization.
        
        Args:
            organization: Organization name to scan
            scan_config: Optional scan configuration overrides
            
        Returns:
            Complete scan results for the organization
        """
        logger.info(f"Starting organization batch scan for: {organization}")
        
        # Update configuration for organization scan
        original_org = self.config.org
        self.config.org = organization
        
        try:
            # Configure workflow for organization scanning
            workflow_config = {
                'scan_pattern': 'organization_security_scan',
                'enable_progress_tracking': True,
                'enable_performance_monitoring': True,
                'repository_filter': scan_config.get('repository_filter') if scan_config else None,
                'max_repositories': scan_config.get('max_repositories') if scan_config else None
            }
            
            # Execute end-to-end batch scan
            results = await self.execute_end_to_end_batch_scan(workflow_config)
            
            logger.info(f"Organization batch scan completed for {organization}: "
                       f"{len(results.matches)} matches found across "
                       f"{results.repositories_scanned} repositories")
            
            return results
            
        finally:
            # Restore original configuration
            self.config.org = original_org
    
    async def execute_team_batch_scan(
        self, 
        organization: str, 
        team: str,
        scan_config: Optional[Dict[str, Any]] = None
    ) -> ScanResults:
        """Execute a complete batch scan for a specific team.
        
        Args:
            organization: Organization name
            team: Team name to scan
            scan_config: Optional scan configuration overrides
            
        Returns:
            Complete scan results for the team
        """
        logger.info(f"Starting team batch scan for: {organization}/{team}")
        
        # Store original configuration
        original_org = self.config.org
        original_team = self.config.team
        
        try:
            # Update configuration for team scan
            self.config.org = organization
            self.config.team = team
            
            # Configure workflow for team scanning
            workflow_config = {
                'scan_pattern': 'team_security_scan',
                'enable_progress_tracking': True,
                'enable_performance_monitoring': True
            }
            
            # Execute end-to-end batch scan
            results = await self.execute_end_to_end_batch_scan(workflow_config)
            
            logger.info(f"Team batch scan completed for {organization}/{team}: "
                       f"{len(results.matches)} matches found across "
                       f"{results.repositories_scanned} repositories")
            
            return results
            
        finally:
            # Restore original configuration
            self.config.org = original_org
            self.config.team = original_team
    
    async def execute_repository_batch_scan(
        self, 
        organization: str, 
        repository: str,
        scan_config: Optional[Dict[str, Any]] = None
    ) -> ScanResults:
        """Execute a complete batch scan for a specific repository.
        
        Args:
            organization: Organization name
            repository: Repository name to scan
            scan_config: Optional scan configuration overrides
            
        Returns:
            Complete scan results for the repository
        """
        logger.info(f"Starting repository batch scan for: {organization}/{repository}")
        
        # Store original configuration
        original_org = self.config.org
        original_repo = self.config.repo
        
        try:
            # Update configuration for repository scan
            self.config.org = organization
            self.config.repo = repository
            
            # Configure workflow for repository scanning
            workflow_config = {
                'scan_pattern': 'repository_security_scan',
                'enable_progress_tracking': True,
                'enable_performance_monitoring': True,
                'focus_on_priority_files': scan_config.get('focus_on_priority_files', True) if scan_config else True
            }
            
            # Execute end-to-end batch scan
            results = await self.execute_end_to_end_batch_scan(workflow_config)
            
            logger.info(f"Repository batch scan completed for {organization}/{repository}: "
                       f"{len(results.matches)} matches found across "
                       f"{results.files_scanned} files")
            
            return results
            
        finally:
            # Restore original configuration
            self.config.org = original_org
            self.config.repo = original_repo

    def scan_repository(self, org: str, repo: str) -> List[IOCMatch]:
        """Scan a specific repository for IOCs."""
        repo_obj = Repository(
            name=repo,
            full_name=f"{org}/{repo}",
            archived=False,
            default_branch="main",
            updated_at=None
        )
        
        try:
            # Load IOC definitions
            ioc_definitions = self.ioc_loader.load_iocs()
            ioc_hash = self.ioc_loader.get_ioc_hash()
            
            matches, _ = self.scan_repository_for_iocs(repo_obj, ioc_hash)
            return matches
            
        except Exception as e:
            logger.error(f"Failed to scan repository {org}/{repo}: {e}")
            return []
    
    def _setup_batch_progress_monitoring(self) -> None:
        """Setup batch progress monitoring to integrate with CLI progress callback."""
        if not self.batch_coordinator or not self.progress_callback:
            return
        
        # Create a wrapper function that converts batch progress to CLI progress format
        def batch_progress_callback(snapshot):
            """Convert batch progress snapshot to CLI progress callback format."""
            try:
                # Calculate progress information
                current = snapshot.completed_operations
                total = snapshot.total_operations
                
                # Create a repository name for display (use operation type if no specific repo)
                current_repo = getattr(snapshot, 'current_repository', 'batch_operation')
                
                # Get start time from the progress monitor and convert to timestamp
                start_time = self.batch_coordinator.progress_monitor.start_time
                start_timestamp = start_time.timestamp() if start_time else None
                
                # Call the original CLI progress callback
                self.progress_callback(current, total, current_repo, start_timestamp)
                
            except Exception as e:
                logger.warning(f"Error in batch progress callback: {e}")
        
        # Configure the batch coordinator's progress monitor with our callback
        self.batch_coordinator.progress_monitor.progress_callback = batch_progress_callback
        
        logger.debug("Batch progress monitoring configured with CLI integration")