"""Integration tests for the GitHub IOC Scanner.

This module contains comprehensive integration tests that verify the complete
scanning workflows, cache behavior, error handling, and performance characteristics
of the GitHub IOC Scanner across different scanning modes.
"""

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

import pytest

from github_ioc_scanner.scanner import GitHubIOCScanner
from github_ioc_scanner.github_client import GitHubClient
from github_ioc_scanner.cache import CacheManager
from github_ioc_scanner.ioc_loader import IOCLoader
from github_ioc_scanner.cli import CLIInterface
from github_ioc_scanner.models import (
    ScanConfig, Repository, FileInfo, APIResponse, ScanResults, CacheStats,
    FileContent, PackageDependency, IOCMatch, IOCDefinition
)
from github_ioc_scanner.exceptions import (
    ScanError, AuthenticationError, RateLimitError, IOCLoaderError
)


class TestEndToEndScanning:
    """End-to-end integration tests for complete scanning workflows."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.sqlite3"
            yield str(cache_path)

    @pytest.fixture
    def temp_issues_dir(self):
        """Create a temporary issues directory with test IOC files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            issues_dir = Path(temp_dir) / "issues"
            issues_dir.mkdir()
            
            # Create test IOC file
            ioc_file = issues_dir / "test_ioc.py"
            ioc_content = '''
IOC_PACKAGES = {
    "malicious-package": ["1.0.0", "1.0.1"],
    "always-bad": None,  # Any version
    "specific-vuln": ["2.1.0"]
}
'''
            ioc_file.write_text(ioc_content)
            
            yield str(issues_dir)

    @pytest.fixture
    def mock_github_responses(self):
        """Create comprehensive mock GitHub API responses."""
        return {
            "repositories": [
                Repository(
                    name="frontend-app",
                    full_name="test-org/frontend-app",
                    archived=False,
                    default_branch="main",
                    updated_at=datetime.now(timezone.utc)
                ),
                Repository(
                    name="backend-api",
                    full_name="test-org/backend-api",
                    archived=False,
                    default_branch="main",
                    updated_at=datetime.now(timezone.utc)
                ),
                Repository(
                    name="old-project",
                    full_name="test-org/old-project",
                    archived=True,
                    default_branch="master",
                    updated_at=datetime.now(timezone.utc)
                )
            ],
            "files": {
                "test-org/frontend-app": [
                    FileInfo(path="package.json", sha="abc123", size=1024),
                    FileInfo(path="yarn.lock", sha="def456", size=2048)
                ],
                "test-org/backend-api": [
                    FileInfo(path="requirements.txt", sha="ghi789", size=512),
                    FileInfo(path="poetry.lock", sha="jkl012", size=1536)
                ]
            },
            "file_contents": {
                ("test-org/frontend-app", "package.json"): FileContent(
                    content=json.dumps({
                        "name": "frontend-app",
                        "dependencies": {
                            "react": "^18.0.0",
                            "malicious-package": "1.0.0",
                            "lodash": "^4.17.21"
                        },
                        "devDependencies": {
                            "jest": "^27.0.0"
                        }
                    }),
                    sha="abc123",
                    size=1024
                ),
                ("test-org/frontend-app", "yarn.lock"): FileContent(
                    content='''# yarn lockfile v1

always-bad@^2.0.0:
  version "2.5.1"
  resolved "https://registry.yarnpkg.com/always-bad/-/always-bad-2.5.1.tgz"

react@^18.0.0:
  version "18.2.0"
  resolved "https://registry.yarnpkg.com/react/-/react-18.2.0.tgz"
''',
                    sha="def456",
                    size=2048
                ),
                ("test-org/backend-api", "requirements.txt"): FileContent(
                    content='''django==4.1.0
requests>=2.28.0
specific-vuln==2.1.0
pytest==7.1.0
''',
                    sha="ghi789",
                    size=512
                ),
                ("test-org/backend-api", "poetry.lock"): FileContent(
                    content='''[[package]]
name = "django"
version = "4.1.0"
description = "A high-level Python Web framework."

[[package]]
name = "safe-package"
version = "1.0.0"
description = "A safe package"
''',
                    sha="jkl012",
                    size=1536
                )
            }
        }

    def test_organization_scan_complete_workflow(self, temp_cache_dir, temp_issues_dir, mock_github_responses):
        """Test complete organization scanning workflow with IOC detection."""
        # Setup configuration
        config = ScanConfig(
            org="test-org",
            team=None,
            repo=None,
            fast_mode=False,
            include_archived=False,
            issues_dir=temp_issues_dir
        )
        
        # Setup cache manager
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        
        # Setup IOC loader
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        
        # Setup mock GitHub client
        github_client = Mock(spec=GitHubClient)
        
        # Mock repository discovery
        github_client.get_organization_repos.return_value = APIResponse(
            data=mock_github_responses["repositories"],
            etag='"org-etag"',
            not_modified=False
        )
        
        # Mock file discovery
        def mock_search_files(repo, patterns, fast_mode=False):
            return mock_github_responses["files"].get(repo.full_name, [])
        
        github_client.search_files.side_effect = mock_search_files
        
        # Mock file content fetching
        def mock_get_file_content(repo, path, etag=None):
            key = (repo.full_name, path)
            if key in mock_github_responses["file_contents"]:
                return APIResponse(
                    data=mock_github_responses["file_contents"][key],
                    etag=f'"{key[1]}-etag"',
                    not_modified=False
                )
            return APIResponse(data=None, etag=None, not_modified=False)
        
        github_client.get_file_content.side_effect = mock_get_file_content
        
        # Create scanner and run scan
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Verify results
        assert isinstance(results, ScanResults)
        assert results.repositories_scanned == 2  # Only non-archived repos
        assert results.files_scanned == 4  # 2 files per repo
        
        # Verify IOC matches
        assert len(results.matches) == 3  # Should find 3 IOC matches
        
        # Check specific matches
        match_details = [(m.repo, m.file_path, m.package_name, m.version) for m in results.matches]
        expected_matches = [
            ("test-org/frontend-app", "package.json", "malicious-package", "1.0.0"),
            ("test-org/frontend-app", "yarn.lock", "always-bad", "2.5.1"),
            ("test-org/backend-api", "requirements.txt", "specific-vuln", "2.1.0")
        ]
        
        for expected in expected_matches:
            assert expected in match_details, f"Expected match {expected} not found in {match_details}"
        
        # Verify cache statistics
        assert isinstance(results.cache_stats, CacheStats)
        assert results.cache_stats.misses > 0  # First scan should have cache misses

    def test_team_scan_workflow(self, temp_cache_dir, temp_issues_dir, mock_github_responses):
        """Test team-specific scanning workflow."""
        config = ScanConfig(
            org="test-org",
            team="security-team",
            repo=None,
            fast_mode=False,
            include_archived=True,  # Include archived for team scans
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock team repository discovery
        github_client.get_team_repos.return_value = APIResponse(
            data=mock_github_responses["repositories"],
            etag='"team-etag"',
            not_modified=False
        )
        
        # Mock file discovery and content (simplified for team test)
        github_client.search_files.return_value = []
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Verify team scan includes archived repositories
        assert results.repositories_scanned == 3  # All repos including archived
        
        # Verify team API was called
        github_client.get_team_repos.assert_called_once_with("test-org", "security-team", etag=None)

    def test_single_repository_scan_workflow(self, temp_cache_dir, temp_issues_dir, mock_github_responses):
        """Test single repository scanning workflow."""
        config = ScanConfig(
            org="test-org",
            team=None,
            repo="frontend-app",
            fast_mode=False,
            include_archived=False,
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock file discovery for single repo
        github_client.search_files.return_value = mock_github_responses["files"]["test-org/frontend-app"]
        
        # Mock file content fetching
        def mock_get_file_content(repo, path, etag=None):
            key = (repo.full_name, path)
            if key in mock_github_responses["file_contents"]:
                return APIResponse(
                    data=mock_github_responses["file_contents"][key],
                    etag=f'"{path}-etag"',
                    not_modified=False
                )
            return APIResponse(data=None, etag=None, not_modified=False)
        
        github_client.get_file_content.side_effect = mock_get_file_content
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Verify single repository scan
        assert results.repositories_scanned == 1
        assert results.files_scanned == 2  # package.json and yarn.lock
        
        # Should find IOC matches in the single repository
        assert len(results.matches) >= 1

    def test_fast_mode_scanning(self, temp_cache_dir, temp_issues_dir, mock_github_responses):
        """Test fast mode scanning behavior."""
        config = ScanConfig(
            org="test-org",
            team=None,
            repo=None,
            fast_mode=True,  # Enable fast mode
            include_archived=False,
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock repository discovery
        github_client.get_organization_repos.return_value = APIResponse(
            data=mock_github_responses["repositories"][:1],  # Only one repo for fast test
            etag='"org-etag"'
        )
        
        # Mock file discovery - fast mode should be passed
        github_client.search_files.return_value = [mock_github_responses["files"]["test-org/frontend-app"][0]]  # Only package.json
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Verify fast mode was used in file search
        github_client.search_files.assert_called_with(
            mock_github_responses["repositories"][0],
            scanner.LOCKFILE_PATTERNS,
            fast_mode=True
        )


class TestCacheBehaviorIntegration:
    """Integration tests for cache behavior across multiple scan sessions."""

    @pytest.fixture
    def persistent_cache_dir(self):
        """Create a persistent cache directory for multi-session testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.sqlite3"
            yield str(cache_path)

    @pytest.fixture
    def temp_issues_dir(self):
        """Create a temporary issues directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            issues_dir = Path(temp_dir) / "issues"
            issues_dir.mkdir()
            
            ioc_file = issues_dir / "test_ioc.py"
            ioc_content = 'IOC_PACKAGES = {"test-package": ["1.0.0"]}'
            ioc_file.write_text(ioc_content)
            
            yield str(issues_dir)

    def test_cache_persistence_across_scans(self, persistent_cache_dir, temp_issues_dir):
        """Test that cache persists and improves performance across multiple scans."""
        config = ScanConfig(
            org="test-org",
            repo="test-repo",
            issues_dir=temp_issues_dir
        )
        
        # Mock data for consistent responses
        mock_repo = Repository(
            name="test-repo",
            full_name="test-org/test-repo",
            archived=False,
            default_branch="main",
            updated_at=datetime.now(timezone.utc)
        )
        
        mock_file = FileInfo(path="package.json", sha="abc123", size=1024)
        mock_content = FileContent(
            content='{"dependencies": {"test-package": "1.0.0"}}',
            sha="abc123",
            size=1024
        )
        
        # First scan - should populate cache
        cache_manager1 = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader1 = IOCLoader(issues_dir=temp_issues_dir)
        github_client1 = Mock(spec=GitHubClient)
        
        github_client1.search_files.return_value = [mock_file]
        github_client1.get_file_content.return_value = APIResponse(
            data=mock_content,
            etag='"file-etag"'
        )
        
        scanner1 = GitHubIOCScanner(config, github_client1, cache_manager1, ioc_loader1)
        
        start_time = time.time()
        results1 = scanner1.scan()
        first_scan_time = time.time() - start_time
        
        # Verify first scan results
        assert results1.files_scanned == 1
        assert results1.cache_stats.misses > 0
        assert results1.cache_stats.hits == 0  # First scan should have no hits
        
        # Second scan - should use cache extensively
        cache_manager2 = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader2 = IOCLoader(issues_dir=temp_issues_dir)
        github_client2 = Mock(spec=GitHubClient)
        
        # Mock GitHub client to return 304 Not Modified for cached content
        github_client2.search_files.return_value = [mock_file]
        github_client2.get_file_content.return_value = APIResponse(
            data=None,  # No new data
            etag='"file-etag"',
            not_modified=True  # Content not modified
        )
        
        scanner2 = GitHubIOCScanner(config, github_client2, cache_manager2, ioc_loader2)
        
        start_time = time.time()
        results2 = scanner2.scan()
        second_scan_time = time.time() - start_time
        
        # Verify second scan used cache
        assert results2.files_scanned == 1
        assert results2.cache_stats.hits > 0  # Should have cache hits
        assert results2.cache_stats.time_saved > 0
        
        # Second scan should be faster due to caching
        assert second_scan_time < first_scan_time

    def test_cache_invalidation_on_ioc_changes(self, persistent_cache_dir, temp_issues_dir):
        """Test that cache is properly invalidated when IOC definitions change."""
        config = ScanConfig(
            org="test-org",
            repo="test-repo",
            issues_dir=temp_issues_dir
        )
        
        mock_repo = Repository(
            name="test-repo",
            full_name="test-org/test-repo",
            archived=False,
            default_branch="main",
            updated_at=datetime.now(timezone.utc)
        )
        
        mock_file = FileInfo(path="package.json", sha="abc123", size=1024)
        mock_content = FileContent(
            content='{"dependencies": {"new-malicious": "1.0.0"}}',
            sha="abc123",
            size=1024
        )
        
        # First scan with initial IOC definitions
        cache_manager = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        github_client.search_files.return_value = [mock_file]
        github_client.get_file_content.return_value = APIResponse(
            data=mock_content,
            etag='"file-etag"'
        )
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results1 = scanner.scan()
        
        # Should find no matches with initial IOC definitions
        assert len(results1.matches) == 0
        
        # Update IOC definitions to include the new package
        ioc_file = Path(temp_issues_dir) / "test_ioc.py"
        new_ioc_content = '''
IOC_PACKAGES = {
    "test-package": ["1.0.0"],
    "new-malicious": ["1.0.0"]  # Add new IOC
}
'''
        ioc_file.write_text(new_ioc_content)
        
        # Second scan with updated IOC definitions
        cache_manager2 = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader2 = IOCLoader(issues_dir=temp_issues_dir)
        github_client2 = Mock(spec=GitHubClient)
        
        # File content hasn't changed, so return 304 Not Modified
        github_client2.search_files.return_value = [mock_file]
        github_client2.get_file_content.return_value = APIResponse(
            data=None,
            etag='"file-etag"',
            not_modified=True
        )
        
        scanner2 = GitHubIOCScanner(config, github_client2, cache_manager2, ioc_loader2)
        results2 = scanner2.scan()
        
        # Should find matches with updated IOC definitions
        assert len(results2.matches) == 1
        assert results2.matches[0].package_name == "new-malicious"

    def test_etag_based_conditional_requests(self, persistent_cache_dir, temp_issues_dir):
        """Test ETag-based conditional requests for efficient API usage."""
        config = ScanConfig(
            org="test-org",
            issues_dir=temp_issues_dir
        )
        
        mock_repos = [
            Repository(
                name="test-repo",
                full_name="test-org/test-repo",
                archived=False,
                default_branch="main",
                updated_at=datetime.now(timezone.utc)
            )
        ]
        
        # First scan - populate cache with ETag
        cache_manager1 = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader1 = IOCLoader(issues_dir=temp_issues_dir)
        github_client1 = Mock(spec=GitHubClient)
        
        github_client1.get_organization_repos.return_value = APIResponse(
            data=mock_repos,
            etag='"repos-etag-v1"'
        )
        github_client1.search_files.return_value = []
        
        scanner1 = GitHubIOCScanner(config, github_client1, cache_manager1, ioc_loader1)
        results1 = scanner1.scan()
        
        # Second scan - should use ETag for conditional request
        cache_manager2 = CacheManager(cache_path=persistent_cache_dir)
        ioc_loader2 = IOCLoader(issues_dir=temp_issues_dir)
        github_client2 = Mock(spec=GitHubClient)
        
        # Return 304 Not Modified for repository list
        github_client2.get_organization_repos.return_value = APIResponse(
            data=None,
            etag='"repos-etag-v1"',
            not_modified=True
        )
        
        scanner2 = GitHubIOCScanner(config, github_client2, cache_manager2, ioc_loader2)
        results2 = scanner2.scan()
        
        # Verify conditional request was made with ETag
        github_client2.get_organization_repos.assert_called_once_with(
            "test-org",
            include_archived=False,
            etag='"repos-etag-v1"'
        )


class TestErrorHandlingIntegration:
    """Integration tests for error handling and recovery scenarios."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.sqlite3"
            yield str(cache_path)

    @pytest.fixture
    def temp_issues_dir(self):
        """Create a temporary issues directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            issues_dir = Path(temp_dir) / "issues"
            issues_dir.mkdir()
            
            ioc_file = issues_dir / "test_ioc.py"
            ioc_content = 'IOC_PACKAGES = {"test-package": ["1.0.0"]}'
            ioc_file.write_text(ioc_content)
            
            yield str(issues_dir)

    def test_authentication_error_handling(self, temp_cache_dir, temp_issues_dir):
        """Test handling of GitHub authentication errors."""
        config = ScanConfig(
            org="test-org",
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock authentication error
        github_client.get_organization_repos.side_effect = AuthenticationError("Invalid token")
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        
        # Should propagate authentication error
        with pytest.raises(AuthenticationError, match="Invalid token"):
            scanner.scan()

    def test_rate_limit_handling(self, temp_cache_dir, temp_issues_dir):
        """Test handling of GitHub rate limit errors."""
        config = ScanConfig(
            org="test-org",
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock rate limit error followed by successful response
        github_client.get_organization_repos.side_effect = [
            RateLimitError("Rate limit exceeded", reset_time=int(time.time()) + 1),
            APIResponse(data=[], etag='"empty-etag"')
        ]
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        
        # Should handle rate limit and retry
        results = scanner.scan()
        assert isinstance(results, ScanResults)
        
        # Verify retry occurred
        assert github_client.get_organization_repos.call_count == 2

    def test_ioc_loader_error_handling(self, temp_cache_dir):
        """Test handling of IOC loader errors."""
        config = ScanConfig(
            org="test-org",
            issues_dir="/nonexistent/directory"  # Invalid directory
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        github_client = Mock(spec=GitHubClient)
        
        # IOC loader should fail with invalid directory
        ioc_loader = IOCLoader(issues_dir="/nonexistent/directory")
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        
        # Should raise IOC loader error
        with pytest.raises(IOCLoaderError):
            scanner.scan()

    def test_partial_failure_recovery(self, temp_cache_dir, temp_issues_dir):
        """Test recovery from partial failures during scanning."""
        config = ScanConfig(
            org="test-org",
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock repositories
        mock_repos = [
            Repository(
                name="working-repo",
                full_name="test-org/working-repo",
                archived=False,
                default_branch="main",
                updated_at=datetime.now(timezone.utc)
            ),
            Repository(
                name="failing-repo",
                full_name="test-org/failing-repo",
                archived=False,
                default_branch="main",
                updated_at=datetime.now(timezone.utc)
            )
        ]
        
        github_client.get_organization_repos.return_value = APIResponse(
            data=mock_repos,
            etag='"repos-etag"'
        )
        
        # Mock file discovery - one repo works, one fails
        def mock_search_files(repo, patterns, fast_mode=False):
            if repo.name == "working-repo":
                return [FileInfo(path="package.json", sha="abc123", size=1024)]
            else:
                raise Exception("Network error")
        
        github_client.search_files.side_effect = mock_search_files
        
        # Mock file content for working repo
        github_client.get_file_content.return_value = APIResponse(
            data=FileContent(
                content='{"dependencies": {}}',
                sha="abc123",
                size=1024
            ),
            etag='"file-etag"'
        )
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Should complete scan despite partial failures
        assert isinstance(results, ScanResults)
        assert results.repositories_scanned == 2  # Both repos attempted
        assert results.files_scanned == 1  # Only working repo succeeded

    def test_malformed_file_handling(self, temp_cache_dir, temp_issues_dir):
        """Test handling of malformed package files."""
        config = ScanConfig(
            org="test-org",
            repo="test-repo",
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Mock file with malformed JSON content
        github_client.search_files.return_value = [
            FileInfo(path="package.json", sha="abc123", size=1024)
        ]
        
        github_client.get_file_content.return_value = APIResponse(
            data=FileContent(
                content='{"dependencies": invalid json}',  # Malformed JSON
                sha="abc123",
                size=1024
            ),
            etag='"file-etag"'
        )
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        results = scanner.scan()
        
        # Should handle malformed files gracefully
        assert isinstance(results, ScanResults)
        assert results.files_scanned == 1
        assert len(results.matches) == 0  # No matches due to parsing failure


class TestPerformanceIntegration:
    """Performance tests for large repository scanning scenarios."""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.sqlite3"
            yield str(cache_path)

    @pytest.fixture
    def temp_issues_dir(self):
        """Create a temporary issues directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            issues_dir = Path(temp_dir) / "issues"
            issues_dir.mkdir()
            
            ioc_file = issues_dir / "test_ioc.py"
            ioc_content = 'IOC_PACKAGES = {"test-package": ["1.0.0"]}'
            ioc_file.write_text(ioc_content)
            
            yield str(issues_dir)

    def test_large_organization_scanning_performance(self, temp_cache_dir, temp_issues_dir):
        """Test performance with large number of repositories."""
        config = ScanConfig(
            org="large-org",
            issues_dir=temp_issues_dir
        )
        
        cache_manager = CacheManager(cache_path=temp_cache_dir)
        ioc_loader = IOCLoader(issues_dir=temp_issues_dir)
        github_client = Mock(spec=GitHubClient)
        
        # Create large number of mock repositories
        num_repos = 100
        mock_repos = []
        for i in range(num_repos):
            mock_repos.append(Repository(
                name=f"repo-{i:03d}",
                full_name=f"large-org/repo-{i:03d}",
                archived=False,
                default_branch="main",
                updated_at=datetime.now(timezone.utc)
            ))
        
        github_client.get_organization_repos.return_value = APIResponse(
            data=mock_repos,
            etag='"large-org-etag"'
        )
        
        # Mock file discovery - each repo has 1-3 files
        def mock_search_files(repo, patterns, fast_mode=False):
            repo_num = int(repo.name.split('-')[1])
            num_files = (repo_num % 3) + 1  # 1-3 files per repo
            files = []
            for j in range(num_files):
                files.append(FileInfo(
                    path=f"file-{j}.json",
                    sha=f"sha-{repo_num}-{j}",
                    size=1024
                ))
            return files
        
        github_client.search_files.side_effect = mock_search_files
        
        # Mock file content
        github_client.get_file_content.return_value = APIResponse(
            data=FileContent(
                content='{"dependencies": {}}',
                sha="mock-sha",
                size=1024
            ),
            etag='"mock-etag"'
        )
        
        scanner = GitHubIOCScanner(config, github_client, cache_manager, ioc_loader)
        
        # Measure scan time
        start_time = time.time()
        results = scanner.scan()
        scan_time = time.time() - start_time
        
        # Verify results
        assert results.repositories_scanned == num_repos
        assert results.files_scanned > num_repos  # At least 1 file per repo
        
        # Performance assertion - should complete within reasonable time
        # This is a rough benchmark and may need adjustment based on system performance
        assert scan_time < 30.0, f"Large organization scan took {scan_time:.2f}s, expected < 30s"
        
        # Verify cache was used effectively
        assert results.cache_stats.misses > 0
        assert results.cache_stats.cache_size > 0

    def test_cache_performance_improvement(self, temp_cache_dir, temp_issues_dir):
        """Test that cache provides significant performance improvement."""
        config = ScanConfig(
            org="test-org",
            issues_dir=temp_issues_dir
        )
        
        # Create moderate number of repositories for performance test
        num_repos = 20
        mock_repos = []
        for i in range(num_repos):
            mock_repos.append(Repository(
                name=f"repo-{i:02d}",
                full_name=f"test-org/repo-{i:02d}",
                archived=False,
                default_branch="main",
                updated_at=datetime.now(timezone.utc)
            ))
        
        # First scan - populate cache
        cache_manager1 = CacheManager(cache_path=temp_cache_dir)
        ioc_loader1 = IOCLoader(issues_dir=temp_issues_dir)
        github_client1 = Mock(spec=GitHubClient)
        
        github_client1.get_organization_repos.return_value = APIResponse(
            data=mock_repos,
            etag='"org-etag"'
        )
        
        github_client1.search_files.return_value = [
            FileInfo(path="package.json", sha="abc123", size=1024)
        ]
        
        github_client1.get_file_content.return_value = APIResponse(
            data=FileContent(
                content='{"dependencies": {}}',
                sha="abc123",
                size=1024
            ),
            etag='"file-etag"'
        )
        
        scanner1 = GitHubIOCScanner(config, github_client1, cache_manager1, ioc_loader1)
        
        start_time = time.time()
        results1 = scanner1.scan()
        first_scan_time = time.time() - start_time
        
        # Second scan - use cache
        cache_manager2 = CacheManager(cache_path=temp_cache_dir)
        ioc_loader2 = IOCLoader(issues_dir=temp_issues_dir)
        github_client2 = Mock(spec=GitHubClient)
        
        # Return 304 Not Modified for all requests
        github_client2.get_organization_repos.return_value = APIResponse(
            data=None,
            etag='"org-etag"',
            not_modified=True
        )
        
        github_client2.search_files.return_value = [
            FileInfo(path="package.json", sha="abc123", size=1024)
        ]
        
        github_client2.get_file_content.return_value = APIResponse(
            data=None,
            etag='"file-etag"',
            not_modified=True
        )
        
        scanner2 = GitHubIOCScanner(config, github_client2, cache_manager2, ioc_loader2)
        
        start_time = time.time()
        results2 = scanner2.scan()
        second_scan_time = time.time() - start_time
        
        # Verify cache provided significant performance improvement
        performance_improvement = (first_scan_time - second_scan_time) / first_scan_time
        assert performance_improvement > 0.3, f"Cache only improved performance by {performance_improvement:.1%}, expected > 30%"
        
        # Verify cache statistics show improvement
        assert results2.cache_stats.hits > 0
        assert results2.cache_stats.time_saved > 0


class TestCLIIntegration:
    """Integration tests for CLI interface with complete workflows."""

    @pytest.fixture
    def temp_issues_dir(self):
        """Create a temporary issues directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            issues_dir = Path(temp_dir) / "issues"
            issues_dir.mkdir()
            
            ioc_file = issues_dir / "test_ioc.py"
            ioc_content = 'IOC_PACKAGES = {"malicious-package": ["1.0.0"]}'
            ioc_file.write_text(ioc_content)
            
            yield str(issues_dir)

    def test_cli_end_to_end_workflow(self, temp_issues_dir):
        """Test complete CLI workflow from argument parsing to result display."""
        # Test argument parsing
        cli = CLIInterface()
        config = cli.parse_arguments([
            "--org", "test-org",
            "--repo", "test-repo",
            "--issues-dir", temp_issues_dir
        ])
        
        # Validate configuration
        assert cli.validate_arguments(config) is True
        
        # Test result display
        matches = [
            IOCMatch(
                repo="test-org/test-repo",
                file_path="package.json",
                package_name="malicious-package",
                version="1.0.0",
                ioc_source="test_ioc.py"
            )
        ]
        
        # Capture output
        import io
        import sys
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            cli.display_results(matches)
            output = captured_output.getvalue()
            
            # Verify output format
            assert "test-org/test-repo | package.json | malicious-package | 1.0.0" in output
        finally:
            sys.stdout = sys.__stdout__

    def test_cli_error_scenarios(self):
        """Test CLI error handling scenarios."""
        cli = CLIInterface()
        
        # Test invalid arguments
        import io
        import sys
        
        captured_stderr = io.StringIO()
        sys.stderr = captured_stderr
        
        try:
            # Missing organization
            config = cli.parse_arguments(["--team", "security"])
            result = cli.validate_arguments(config)
            assert result is False
            
            error_output = captured_stderr.getvalue()
            assert "--team requires --org" in error_output
        finally:
            sys.stderr = sys.__stderr__