"""Command-line interface for the GitHub IOC Scanner."""

import argparse
import sys
import time
from datetime import datetime
from typing import List, Optional

from .exceptions import (
    GitHubIOCScannerError,
    ValidationError,
    format_error_message
)
from .logging_config import get_logger, setup_logging
from .models import IOCMatch, ScanConfig, CacheStats

logger = get_logger(__name__)


class CLIInterface:
    """Handles command-line argument parsing and output formatting."""

    def parse_arguments(self, args: Optional[List[str]] = None) -> ScanConfig:
        """Parse command-line arguments and return a ScanConfig.
        
        Args:
            args: Optional list of arguments to parse (for testing)
        """
        parser = argparse.ArgumentParser(
            prog="github-ioc-scan",
            description="Scan GitHub repositories for Indicators of Compromise (IOCs)",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Scan all repositories in an organization
  github-ioc-scan --org myorg

  # Scan repositories belonging to a specific team
  github-ioc-scan --org myorg --team security-team

  # Scan a specific repository
  github-ioc-scan --org myorg --repo myrepo

  # Fast scan (root-level files only)
  github-ioc-scan --org myorg --fast

  # Include archived repositories
  github-ioc-scan --org myorg --include-archived

  # Use custom IOC definitions directory
  github-ioc-scan --org myorg --issues-dir /path/to/iocs

  # Verbose mode with detailed logging
  github-ioc-scan --org myorg --verbose

  # Quiet mode (only show threats and errors)
  github-ioc-scan --org myorg --quiet

  # Custom log file location
  github-ioc-scan --org myorg --log-file /path/to/scan.log

Cache Management:
  # Display cache information
  github-ioc-scan --cache-info

  # Clear all cache data
  github-ioc-scan --clear-cache

  # Clear specific cache type
  github-ioc-scan --clear-cache-type file

  # Refresh cache for specific repository
  github-ioc-scan --refresh-repo myorg/myrepo

  # Clean up cache entries older than 30 days
  github-ioc-scan --cleanup-cache 30

Batch Processing:
  # Use custom batch size
  github-ioc-scan --org myorg --batch-size 20

  # Limit concurrent requests
  github-ioc-scan --org myorg --max-concurrent 5

  # Use aggressive batching strategy
  github-ioc-scan --org myorg --batch-strategy aggressive

  # Enable cross-repository batching
  github-ioc-scan --org myorg --enable-cross-repo-batching

  # Use batch configuration file
  github-ioc-scan --org myorg --batch-config batch-config.json

Scan Modes:
  Organization Mode: Scan all repositories in an organization
    Usage: --org ORGANIZATION [--include-archived]
    
  Team Mode: Scan repositories belonging to a specific team
    Usage: --org ORGANIZATION --team TEAM_NAME
    
  Repository Mode: Scan a specific repository
    Usage: --org ORGANIZATION --repo REPOSITORY_NAME

Authentication:
  Set GITHUB_TOKEN environment variable or use 'gh auth token' command
            """,
        )

        parser.add_argument(
            "--org",
            type=str,
            metavar="ORGANIZATION",
            help="GitHub organization name to scan (required)",
        )

        parser.add_argument(
            "--team",
            type=str,
            metavar="TEAM_NAME",
            help="GitHub team name to scan (requires --org)",
        )

        parser.add_argument(
            "--repo",
            type=str,
            metavar="REPOSITORY",
            help="Specific repository name to scan (requires --org)",
        )

        parser.add_argument(
            "--fast",
            action="store_true",
            help="Fast mode: only scan root-level lockfiles (faster but less comprehensive)",
        )

        parser.add_argument(
            "--include-archived",
            action="store_true",
            help="Include archived repositories in the scan (default: skip archived repos)",
        )

        parser.add_argument(
            "--issues-dir",
            type=str,
            default=None,
            metavar="DIRECTORY",
            help="Directory containing IOC definition files (default: built-in IOCs)",
        )

        # Cache management options
        cache_group = parser.add_argument_group("cache management")
        
        cache_group.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear all cached data before scanning",
        )

        cache_group.add_argument(
            "--clear-cache-type",
            type=str,
            choices=["file", "packages", "results", "repos", "etags"],
            metavar="TYPE",
            help="Clear specific type of cached data (file, packages, results, repos, etags)",
        )

        cache_group.add_argument(
            "--refresh-repo",
            type=str,
            metavar="REPOSITORY",
            help="Refresh cached data for specific repository (format: org/repo)",
        )

        cache_group.add_argument(
            "--cache-info",
            action="store_true",
            help="Display detailed cache information and exit",
        )

        cache_group.add_argument(
            "--cleanup-cache",
            type=int,
            metavar="DAYS",
            help="Remove cache entries older than specified days",
        )

        # Output and logging options
        output_group = parser.add_argument_group("output and logging")
        
        output_group.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output (show detailed logging information)",
        )

        output_group.add_argument(
            "--log-file",
            type=str,
            metavar="FILE",
            help="Write detailed logs to specified file (default: github-ioc-scan.log)",
        )

        output_group.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress all output except IOC matches and errors",
        )

        # Batch processing options
        batch_group = parser.add_argument_group("batch processing")
        
        batch_group.add_argument(
            "--batch-size",
            type=int,
            metavar="SIZE",
            help="Number of files to process in each batch (default: auto-calculated)",
        )

        batch_group.add_argument(
            "--max-concurrent",
            type=int,
            metavar="COUNT",
            help="Maximum number of concurrent requests (default: 10)",
        )

        batch_group.add_argument(
            "--batch-strategy",
            type=str,
            choices=["sequential", "parallel", "adaptive", "aggressive", "conservative"],
            metavar="STRATEGY",
            help="Batch processing strategy (default: adaptive)",
        )

        batch_group.add_argument(
            "--enable-cross-repo-batching",
            action="store_true",
            help="Enable cross-repository batching optimizations",
        )

        batch_group.add_argument(
            "--disable-cross-repo-batching",
            action="store_true",
            help="Disable cross-repository batching optimizations",
        )

        batch_group.add_argument(
            "--batch-config",
            type=str,
            metavar="FILE",
            help="Path to batch configuration file (JSON format)",
        )

        # Parse arguments (use provided args for testing, otherwise parse from sys.argv)
        parsed_args = parser.parse_args(args)

        # Handle cross-repo batching flags
        enable_cross_repo = None
        if parsed_args.enable_cross_repo_batching:
            enable_cross_repo = True
        elif parsed_args.disable_cross_repo_batching:
            enable_cross_repo = False

        return ScanConfig(
            org=parsed_args.org,
            team=parsed_args.team,
            repo=parsed_args.repo,
            fast_mode=parsed_args.fast,
            include_archived=parsed_args.include_archived,
            issues_dir=parsed_args.issues_dir,
            clear_cache=parsed_args.clear_cache,
            clear_cache_type=parsed_args.clear_cache_type,
            refresh_repo=parsed_args.refresh_repo,
            cache_info=parsed_args.cache_info,
            cleanup_cache=parsed_args.cleanup_cache,
            verbose=getattr(parsed_args, 'verbose', False),
            log_file=getattr(parsed_args, 'log_file', None),
            quiet=getattr(parsed_args, 'quiet', False),
            batch_size=getattr(parsed_args, 'batch_size', None),
            max_concurrent=getattr(parsed_args, 'max_concurrent', None),
            batch_strategy=getattr(parsed_args, 'batch_strategy', None),
            enable_cross_repo_batching=enable_cross_repo,
            batch_config_file=getattr(parsed_args, 'batch_config', None),
        )

    def validate_arguments(self, config: ScanConfig) -> bool:
        """Validate the parsed arguments and return True if valid.
        
        Prints detailed error messages for invalid configurations.
        
        Raises:
            ValidationError: If validation fails with specific field information
        """
        errors = []

        # Check if this is a cache-only operation
        is_cache_only = any([
            config.cache_info,
            config.clear_cache,
            config.clear_cache_type is not None,
            config.refresh_repo is not None,
            config.cleanup_cache is not None
        ])
        
        # Organization is required for all scan modes (but not cache-only operations)
        if not config.org and not is_cache_only:
            errors.append(ValidationError("--org is required for all scan modes", field="org"))

        # Team requires organization
        if config.team and not config.org:
            errors.append(ValidationError("--team requires --org to be specified", field="team"))

        # Repository requires organization  
        if config.repo and not config.org:
            errors.append(ValidationError("--repo requires --org to be specified", field="repo"))

        # Team and repo are mutually exclusive
        if config.team and config.repo:
            errors.append(ValidationError("--team and --repo cannot be used together (choose one scan mode)", field="team"))

        # Validate organization name format (basic validation)
        if config.org and not self._is_valid_github_name(config.org):
            errors.append(ValidationError(
                f"Invalid organization name '{config.org}' (must contain only alphanumeric characters, hyphens, and underscores)",
                field="org"
            ))

        # Validate team name format
        if config.team and not self._is_valid_github_name(config.team):
            errors.append(ValidationError(
                f"Invalid team name '{config.team}' (must contain only alphanumeric characters, hyphens, and underscores)",
                field="team"
            ))

        # Validate repository name format
        if config.repo and not self._is_valid_github_name(config.repo):
            errors.append(ValidationError(
                f"Invalid repository name '{config.repo}' (must contain only alphanumeric characters, hyphens, underscores, and dots)",
                field="repo"
            ))

        # Validate issues directory path
        if config.issues_dir and not config.issues_dir.strip():
            errors.append(ValidationError("Issues directory path cannot be empty", field="issues_dir"))

        if errors:
            self.display_error("Invalid arguments:")
            for error in errors:
                print(f"  - {error.message}", file=sys.stderr)
            print("\nUse --help for usage examples", file=sys.stderr)
            return False

        # Validate cache management arguments
        if not self.validate_cache_arguments(config):
            return False

        # Validate batch processing arguments
        if not self.validate_batch_arguments(config):
            return False

        return True

    def _is_valid_github_name(self, name: str) -> bool:
        """Validate GitHub organization/team/repository name format."""
        if not name:
            return False
        
        # Basic validation: alphanumeric, hyphens, underscores, dots
        # GitHub names can't start or end with hyphens
        if name.startswith('-') or name.endswith('-'):
            return False
            
        # Check for valid characters
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')
        return all(c in valid_chars for c in name) and len(name) <= 100

    def validate_batch_arguments(self, config: ScanConfig) -> bool:
        """Validate batch processing arguments."""
        errors = []

        # Validate batch size
        if config.batch_size is not None:
            if config.batch_size < 1:
                errors.append(ValidationError("Batch size must be at least 1", field="batch_size"))
            elif config.batch_size > 200:
                errors.append(ValidationError("Batch size cannot exceed 200", field="batch_size"))

        # Validate max concurrent
        if config.max_concurrent is not None:
            if config.max_concurrent < 1:
                errors.append(ValidationError("Max concurrent requests must be at least 1", field="max_concurrent"))
            elif config.max_concurrent > 100:
                errors.append(ValidationError("Max concurrent requests cannot exceed 100", field="max_concurrent"))

        # Validate batch strategy
        valid_strategies = ["sequential", "parallel", "adaptive", "aggressive", "conservative"]
        if config.batch_strategy is not None and config.batch_strategy not in valid_strategies:
            errors.append(ValidationError(
                f"Invalid batch strategy '{config.batch_strategy}'. Must be one of: {', '.join(valid_strategies)}",
                field="batch_strategy"
            ))

        # Validate batch config file
        if config.batch_config_file is not None:
            import os
            if not os.path.isfile(config.batch_config_file):
                errors.append(ValidationError(
                    f"Batch configuration file '{config.batch_config_file}' does not exist",
                    field="batch_config_file"
                ))
            elif not config.batch_config_file.endswith(('.json', '.yaml', '.yml')):
                errors.append(ValidationError(
                    "Batch configuration file must be JSON or YAML format",
                    field="batch_config_file"
                ))

        if errors:
            self.display_error("Invalid batch processing arguments:")
            for error in errors:
                print(f"  - {error.message}", file=sys.stderr)
            return False

        return True

    def load_batch_config_from_file(self, config_file: str) -> dict:
        """Load batch configuration from a file.
        
        Args:
            config_file: Path to the configuration file (JSON or YAML)
            
        Returns:
            Dictionary containing batch configuration
            
        Raises:
            ValidationError: If the file cannot be loaded or is invalid
        """
        import json
        import os
        
        if not os.path.isfile(config_file):
            raise ValidationError(f"Configuration file '{config_file}' does not exist")
        
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    config_data = json.load(f)
                elif config_file.endswith(('.yaml', '.yml')):
                    try:
                        import yaml
                        config_data = yaml.safe_load(f)
                    except ImportError:
                        raise ValidationError("PyYAML is required to load YAML configuration files")
                else:
                    raise ValidationError("Configuration file must be JSON or YAML format")
            
            # Validate the configuration structure
            if not isinstance(config_data, dict):
                raise ValidationError("Configuration file must contain a JSON object or YAML mapping")
            
            # Validate known configuration keys
            valid_keys = {
                'max_concurrent_requests', 'max_concurrent_repos', 'default_batch_size',
                'max_batch_size', 'min_batch_size', 'rate_limit_buffer', 'retry_attempts',
                'retry_delay_base', 'max_memory_usage_mb', 'stream_large_files_threshold',
                'default_strategy', 'enable_cross_repo_batching', 'enable_file_prioritization',
                'enable_performance_monitoring', 'log_batch_metrics'
            }
            
            unknown_keys = set(config_data.keys()) - valid_keys
            if unknown_keys:
                logger.warning(f"Unknown configuration keys in {config_file}: {', '.join(unknown_keys)}")
            
            return config_data
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValidationError(f"Error loading configuration file: {e}")

    def create_batch_config_from_scan_config(self, scan_config: ScanConfig) -> 'BatchConfig':
        """Create a BatchConfig from CLI arguments and optional config file.
        
        Args:
            scan_config: The parsed scan configuration
            
        Returns:
            BatchConfig instance with merged settings
        """
        from .batch_models import BatchConfig, BatchStrategy
        
        # Start with default configuration
        batch_config = BatchConfig()
        
        # Load from file if specified
        if scan_config.batch_config_file:
            try:
                file_config = self.load_batch_config_from_file(scan_config.batch_config_file)
                
                # Apply file configuration
                for key, value in file_config.items():
                    if hasattr(batch_config, key):
                        # Handle strategy enum conversion
                        if key == 'default_strategy' and isinstance(value, str):
                            try:
                                value = BatchStrategy(value.lower())
                            except ValueError:
                                logger.warning(f"Invalid strategy '{value}' in config file, using default")
                                continue
                        
                        setattr(batch_config, key, value)
                    else:
                        logger.warning(f"Unknown batch configuration key: {key}")
                        
            except ValidationError as e:
                logger.error(f"Failed to load batch configuration file: {e}")
                # Continue with default configuration
        
        # Override with CLI arguments (CLI takes precedence)
        if scan_config.batch_size is not None:
            batch_config.default_batch_size = scan_config.batch_size
            batch_config.max_batch_size = max(batch_config.max_batch_size, scan_config.batch_size)
        
        if scan_config.max_concurrent is not None:
            batch_config.max_concurrent_requests = scan_config.max_concurrent
        
        if scan_config.batch_strategy is not None:
            try:
                batch_config.default_strategy = BatchStrategy(scan_config.batch_strategy.lower())
            except ValueError:
                logger.warning(f"Invalid strategy '{scan_config.batch_strategy}', using default")
        
        if scan_config.enable_cross_repo_batching is not None:
            batch_config.enable_cross_repo_batching = scan_config.enable_cross_repo_batching
        
        # Validate the final configuration
        validation_errors = batch_config.validate()
        if validation_errors:
            error_msg = "Invalid batch configuration: " + "; ".join(validation_errors)
            raise ValidationError(error_msg)
        
        return batch_config

    def display_results(self, results: List[IOCMatch]) -> None:
        """Display scan results in the specified format: {org}/{repo} | {file} | {package} | {version}"""
        if not results:
            print("Keine Treffer gefunden.")
            return

        # Sort results for consistent output
        sorted_results = sorted(results, key=lambda x: (x.repo, x.file_path, x.package_name))
        
        for match in sorted_results:
            print(f"{match.repo} | {match.file_path} | {match.package_name} | {match.version}")

    def display_results_with_header(self, results: List[IOCMatch]) -> None:
        """Display scan results with a header for better readability."""
        if not results:
            print("Keine Treffer gefunden.")
            return

        print(f"Found {len(results)} IOC match{'es' if len(results) != 1 else ''}:")
        print("Repository | File | Package | Version")
        print("-" * 60)
        
        # Sort results for consistent output
        sorted_results = sorted(results, key=lambda x: (x.repo, x.file_path, x.package_name))
        
        for match in sorted_results:
            print(f"{match.repo} | {match.file_path} | {match.package_name} | {match.version}")

    def display_cache_stats(self, stats: CacheStats) -> None:
        """Display cache statistics with hits, misses, and time saved."""
        print(f"\nCache Statistics:")
        print(f"  Hits: {stats.hits}")
        print(f"  Misses: {stats.misses}")
        
        total_operations = stats.hits + stats.misses
        if total_operations > 0:
            hit_rate = (stats.hits / total_operations) * 100
            print(f"  Hit rate: {hit_rate:.1f}%")
            
        print(f"  Time saved: {stats.time_saved:.2f}s")
        print(f"  Cache size: {stats.cache_size} entries")
        
        # Add performance insight
        if stats.time_saved > 0:
            print(f"  Performance: Cache saved {stats.time_saved:.1f} seconds of API calls")
        elif total_operations > 0 and stats.hits == 0:
            print(f"  Performance: First scan - building cache for future runs")

    def display_error(self, message: str) -> None:
        """Display an error message to stderr."""
        print(f"Error: {message}", file=sys.stderr)

    def display_warning(self, message: str) -> None:
        """Display a warning message."""
        print(f"Warning: {message}", file=sys.stderr)

    def display_scan_summary(self, repositories_scanned: int, files_scanned: int) -> None:
        """Display a summary of the scan operation."""
        print(f"\nScan Summary:")
        print(f"  Repositories scanned: {repositories_scanned}")
        print(f"  Files scanned: {files_scanned}")

    def display_progress(self, message: str) -> None:
        """Display a progress message."""
        print(f"[INFO] {message}")

    def display_scan_start(self, config: ScanConfig) -> None:
        """Display scan start information."""
        if config.quiet:
            return
            
        if config.repo:
            print(f"🔍 Scanning repository: {config.org}/{config.repo}")
        elif config.team:
            print(f"🔍 Scanning team repositories: {config.org}/{config.team}")
        else:
            print(f"🔍 Scanning organization: {config.org}")
            
        scan_mode = []
        if config.fast_mode:
            scan_mode.append("fast mode")
        if config.include_archived:
            scan_mode.append("including archived")
        
        if scan_mode:
            print(f"📋 Scan mode: {', '.join(scan_mode)}")
        
        if config.verbose:
            print(f"📁 IOC definitions directory: {config.issues_dir}")
        print()

    def display_professional_scan_start(self, config: ScanConfig, total_iocs: int) -> None:
        """Display professional scan start information for security analysts."""
        if config.quiet:
            return
            
        print("=" * 60)
        print("GitHub IOC Scanner - Security Analysis Report")
        print("=" * 60)
        
        # Scan target
        if config.repo:
            print(f"Target: Repository {config.org}/{config.repo}")
        elif config.team:
            print(f"Target: Team '{config.team}' in organization '{config.org}'")
        else:
            print(f"Target: Organization '{config.org}'")
        
        # Scan configuration
        scan_config = []
        if config.fast_mode:
            scan_config.append("Fast mode (root-level files only)")
        else:
            scan_config.append("Comprehensive mode (all files)")
        
        if config.include_archived:
            scan_config.append("Including archived repositories")
        else:
            scan_config.append("Excluding archived repositories")
        
        print(f"Configuration: {', '.join(scan_config)}")
        print(f"IOC Database: {total_iocs:,} threat indicators loaded (incl. Heise-reported npm attacks)")
        print(f"Scan initiated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

    def display_professional_results(self, results: List[IOCMatch], config: ScanConfig) -> None:
        """Display results in a professional format for security analysts."""
        if not results:
            if not config.quiet:
                print("✅ SCAN COMPLETE - No threats detected")
                print("   All scanned packages are clean")
            return

        # Security alert header
        print("🚨 SECURITY ALERT - THREATS DETECTED")
        print("=" * 60)
        print(f"Found {len(results)} indicators of compromise:")
        print()

        # Group results by repository for better readability
        repo_groups = {}
        for match in results:
            if match.repo not in repo_groups:
                repo_groups[match.repo] = []
            repo_groups[match.repo].append(match)

        # Display results grouped by repository
        for repo, matches in sorted(repo_groups.items()):
            print(f"📦 Repository: {repo}")
            print(f"   Threats found: {len(matches)}")
            
            for match in sorted(matches, key=lambda x: (x.file_path, x.package_name)):
                print(f"   ⚠️  {match.file_path} | {match.package_name} | {match.version}")
            print()

        # Summary
        total_repos = len(repo_groups)
        print("-" * 60)
        print(f"SUMMARY: {len(results)} threats across {total_repos} repositories")
        print("ACTION REQUIRED: Review and remediate identified threats")

    def display_professional_summary(self, repos_scanned: int, files_scanned: int, 
                                   cache_stats: 'CacheStats', config: ScanConfig) -> None:
        """Display professional scan summary."""
        if config.quiet:
            return
            
        print("-" * 60)
        print("SCAN STATISTICS:")
        print(f"  Repositories scanned: {repos_scanned:,}")
        print(f"  Files analyzed: {files_scanned:,}")
        
        if cache_stats.hits + cache_stats.misses > 0:
            hit_rate = (cache_stats.hits / (cache_stats.hits + cache_stats.misses)) * 100
            print(f"  Cache efficiency: {hit_rate:.1f}% ({cache_stats.hits:,} hits, {cache_stats.misses:,} misses)")
            
            if cache_stats.time_saved > 0:
                print(f"  Time saved by caching: {cache_stats.time_saved:.1f}s")
        
        print(f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

    def display_progress(self, current: int, total: int, repo_name: str, config: ScanConfig, 
                        start_time: float = None) -> None:
        """Display scan progress for repositories."""
        if config.quiet:
            return
            
        # Calculate progress percentage
        percentage = (current / total) * 100 if total > 0 else 0
        
        # Create progress bar
        bar_length = 30  # Shorter bar to make room for ETA
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        # Calculate ETA if start_time is provided
        eta_str = ""
        if start_time and current > 0:
            elapsed = time.time() - start_time
            avg_time_per_repo = elapsed / current
            remaining_repos = total - current
            eta_seconds = remaining_repos * avg_time_per_repo
            
            if eta_seconds > 60:
                eta_str = f" | ETA: {int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
            elif eta_seconds > 0:
                eta_str = f" | ETA: {int(eta_seconds)}s"
        
        # Display progress
        if config.verbose:
            print(f"[{current:3d}/{total:3d}] [{bar}] {percentage:5.1f}%{eta_str} | Scanning: {repo_name}")
        else:
            # Compact progress for normal mode
            repo_display = repo_name[:35] if len(repo_name) > 35 else repo_name
            print(f"\r[{current:3d}/{total:3d}] [{bar}] {percentage:5.1f}%{eta_str} | {repo_display:<35}", end='', flush=True)
    
    def clear_progress_line(self, config: ScanConfig) -> None:
        """Clear the progress line after completion."""
        if not config.quiet and not config.verbose:
            print("\r" + " " * 80 + "\r", end='', flush=True)

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"

    def display_cache_info(self, cache_info: dict) -> None:
        """Display detailed cache information."""
        print("Cache Information:")
        print(f"  Location: {cache_info.get('cache_path', 'Unknown')}")
        print(f"  Database size: {self.format_file_size(cache_info.get('db_size_bytes', 0))}")
        print()
        
        print("Cache Contents:")
        print(f"  File content entries: {cache_info.get('file_cache', 0):,}")
        print(f"  Parsed packages entries: {cache_info.get('parsed_packages', 0):,}")
        print(f"  Scan results entries: {cache_info.get('scan_results', 0):,}")
        print(f"  Repository metadata entries: {cache_info.get('repo_metadata', 0):,}")
        print(f"  ETag entries: {cache_info.get('etag_cache', 0):,}")
        
        total_entries = sum([
            cache_info.get('file_cache', 0),
            cache_info.get('parsed_packages', 0),
            cache_info.get('scan_results', 0),
            cache_info.get('repo_metadata', 0),
            cache_info.get('etag_cache', 0)
        ])
        print(f"  Total entries: {total_entries:,}")
        
        # Display top repositories if available
        if 'top_repositories' in cache_info and cache_info['top_repositories']:
            print()
            print("Top Cached Repositories:")
            for repo_info in cache_info['top_repositories']:
                print(f"  {repo_info['repo']}: {repo_info['files']:,} files")
        
        # Display cache age information if available
        if 'cache_age' in cache_info:
            age_info = cache_info['cache_age']
            print()
            print("Cache Age:")
            if age_info.get('oldest_entry'):
                print(f"  Oldest entry: {age_info['oldest_entry']}")
            if age_info.get('newest_entry'):
                print(f"  Newest entry: {age_info['newest_entry']}")
            if age_info.get('average_age_days') is not None:
                print(f"  Average age: {age_info['average_age_days']:.1f} days")

    def display_cache_operation_result(self, operation: str, count: int = 0, cache_type: str = None) -> None:
        """Display the result of a cache operation."""
        if operation == "clear":
            if cache_type:
                print(f"Cleared {cache_type} cache")
            else:
                print("Cleared all cache data")
        elif operation == "refresh":
            print(f"Refreshed repository cache: removed {count:,} entries")
        elif operation == "cleanup":
            print(f"Cleaned up old cache entries: removed {count:,} entries")

    def validate_cache_arguments(self, config: ScanConfig) -> bool:
        """Validate cache management arguments."""
        errors = []
        
        # Validate refresh-repo format
        if config.refresh_repo:
            if '/' not in config.refresh_repo:
                errors.append(ValidationError(
                    f"Invalid repository format '{config.refresh_repo}' (expected: org/repo)",
                    field="refresh_repo"
                ))
            else:
                org, repo = config.refresh_repo.split('/', 1)
                if not self._is_valid_github_name(org) or not self._is_valid_github_name(repo):
                    errors.append(ValidationError(
                        f"Invalid repository name '{config.refresh_repo}'",
                        field="refresh_repo"
                    ))
        
        # Validate cleanup-cache value
        if config.cleanup_cache is not None:
            if config.cleanup_cache < 1:
                errors.append(ValidationError(
                    "Cleanup days must be a positive integer",
                    field="cleanup_cache"
                ))
        
        # Check for conflicting cache operations
        cache_operations = [
            config.clear_cache,
            config.clear_cache_type is not None,
            config.refresh_repo is not None,
            config.cache_info,
            config.cleanup_cache is not None
        ]
        
        if sum(cache_operations) > 1:
            errors.append(ValidationError(
                "Only one cache management operation can be specified at a time",
                field="cache"
            ))
        
        if errors:
            self.display_error("Invalid cache management arguments:")
            for error in errors:
                print(f"  - {error.message}", file=sys.stderr)
            return False
        
        return True


def main() -> None:
    """Main entry point for the CLI application."""
    try:
        cli = CLIInterface()
        config = cli.parse_arguments()
        
        if not cli.validate_arguments(config):
            sys.exit(1)
        
        # Configure logging based on user preferences
        log_file = config.log_file or "github-ioc-scan.log"
        
        if config.verbose:
            # Verbose mode: show detailed logs on console
            setup_logging(level="INFO", log_file=log_file)
        elif config.quiet:
            # Quiet mode: only critical errors on console, everything to file
            setup_logging(level="CRITICAL", log_file=log_file)
            # Set file handler to capture all logs
            import logging
            file_logger = logging.getLogger()
            for handler in file_logger.handlers:
                if hasattr(handler, 'baseFilename'):  # FileHandler
                    handler.setLevel(logging.DEBUG)
        else:
            # Normal mode: minimal console output, detailed file logging
            setup_logging(level="ERROR", log_file=log_file)
            # Set file handler to capture all logs
            import logging
            file_logger = logging.getLogger()
            for handler in file_logger.handlers:
                if hasattr(handler, 'baseFilename'):  # FileHandler
                    handler.setLevel(logging.INFO)
        
        # Import here to avoid circular imports
        from .cache import CacheManager
        from .github_client import GitHubClient
        from .ioc_loader import IOCLoader
        from .scanner import GitHubIOCScanner
        
        # Handle cache-only operations first
        if config.cache_info or config.clear_cache or config.clear_cache_type or config.refresh_repo or config.cleanup_cache:
            cache_manager = CacheManager()
            
            if config.cache_info:
                if not config.quiet:
                    print("📊 Cache Information")
                    print("=" * 40)
                cache_info = cache_manager.get_cache_info()
                cli.display_cache_info(cache_info)
                return
            
            if config.clear_cache:
                if not config.quiet:
                    print("🧹 Clearing all cache data...")
                cache_manager.clear_cache()
                if not config.quiet:
                    print("✅ Cache cleared successfully")
                return
            
            if config.clear_cache_type:
                if not config.quiet:
                    print(f"🧹 Clearing {config.clear_cache_type} cache...")
                cache_manager.clear_cache(config.clear_cache_type)
                if not config.quiet:
                    print(f"✅ {config.clear_cache_type.title()} cache cleared successfully")
                return
            
            if config.refresh_repo:
                if not config.quiet:
                    print(f"🔄 Refreshing cache for {config.refresh_repo}...")
                count = cache_manager.refresh_repository_cache(config.refresh_repo)
                if not config.quiet:
                    print(f"✅ Refreshed repository cache: removed {count:,} entries")
                return
            
            if config.cleanup_cache:
                if not config.quiet:
                    print(f"🧹 Cleaning up cache entries older than {config.cleanup_cache} days...")
                count = cache_manager.cleanup_old_entries(config.cleanup_cache)
                if not config.quiet:
                    print(f"✅ Cleaned up old cache entries: removed {count:,} entries")
                return
        
        # Initialize components for scanning
        try:
            # Load IOC definitions
            ioc_loader = IOCLoader(config.issues_dir)
            iocs = ioc_loader.load_iocs()
            
            if not iocs:
                cli.display_error(f"No IOC definitions found in '{config.issues_dir}' directory")
                sys.exit(1)
            
            # Count total IOC packages
            total_ioc_packages = sum(len(ioc_def.packages) for ioc_def in iocs.values())
            
            if config.verbose:
                logger.info(f"Loaded {len(iocs)} IOC files with {total_ioc_packages} total packages")
            
            # Initialize GitHub client
            github_client = GitHubClient()
            
            # Initialize cache manager
            cache_manager = CacheManager()
            
            # Create progress callback
            def progress_callback(current: int, total: int, repo_name: str, start_time: float = None):
                cli.display_progress(current, total, repo_name, config, start_time)
            
            # Initialize scanner with progress callback
            scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader, progress_callback)
            
            # Display professional scan start information
            cli.display_professional_scan_start(config, total_ioc_packages)
            
            # Run the scan
            results = scanner.scan()
            
            # Clear progress line after completion
            cli.clear_progress_line(config)
            
            # Display results in professional format
            cli.display_professional_results(results.matches, config)
            
            # Close cache connection for cleanup
            try:
                cache_manager.close()
            except Exception as e:
                logger.debug(f"Error closing cache: {e}")
            
            # Display professional summary
            cli.display_professional_summary(
                results.repositories_scanned, 
                results.files_scanned, 
                results.cache_stats, 
                config
            )
            
        except Exception as e:
            cli.display_error(f"Failed to initialize scanner: {e}")
            logger.error(f"Scanner initialization failed: {e}", exc_info=True)
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard exit code for SIGINT
    except GitHubIOCScannerError as e:
        error_msg = format_error_message(e, include_cause=False)
        print(f"Error: {error_msg}", file=sys.stderr)
        logger.debug(f"Full error details: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()