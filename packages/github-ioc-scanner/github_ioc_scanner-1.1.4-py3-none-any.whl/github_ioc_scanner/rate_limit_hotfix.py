"""
Rate Limit Hotfix

This module provides emergency rate limit handling to prevent crashes
when rate limits are exceeded during scanning.
"""

import time
from datetime import datetime
from typing import Optional

from .exceptions import RateLimitError
from .logging_config import get_logger

logger = get_logger(__name__)


def handle_rate_limit_gracefully(func):
    """Decorator to handle rate limit errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitError as e:
            logger.warning(f"🚨 Rate limit exceeded in {func.__name__}: {e}")
            
            # Calculate wait time
            reset_time = getattr(e, 'reset_time', None)
            if reset_time:
                current_time = int(time.time())
                wait_time = max(reset_time - current_time, 60)  # At least 1 minute
                
                logger.warning(f"💤 Waiting {wait_time}s until rate limit resets at {datetime.fromtimestamp(reset_time)}")
                
                try:
                    time.sleep(wait_time)
                    logger.info("✅ Rate limit wait completed, resuming operations")
                    
                    # Retry the operation once
                    return func(*args, **kwargs)
                except KeyboardInterrupt:
                    logger.info("⚠️  Rate limit wait interrupted by user")
                    raise
                except RateLimitError:
                    logger.error("🚨 Rate limit still exceeded after waiting, skipping operation")
                    return [] if 'search' in func.__name__ or 'discover' in func.__name__ else None
            else:
                # No reset time available, wait a default amount
                logger.warning("💤 No reset time available, waiting 5 minutes")
                time.sleep(300)  # 5 minutes
                
            return [] if 'search' in func.__name__ or 'discover' in func.__name__ else None
        except Exception as e:
            logger.error(f"❌ Unexpected error in {func.__name__}: {e}")
            return [] if 'search' in func.__name__ or 'discover' in func.__name__ else None
    
    return wrapper


def emergency_rate_limit_handler(reset_time: Optional[int] = None) -> None:
    """Emergency rate limit handler for critical situations."""
    if reset_time:
        current_time = int(time.time())
        wait_time = max(reset_time - current_time, 60)
        
        logger.error(f"🚨 EMERGENCY RATE LIMIT HIT! Waiting {wait_time}s until {datetime.fromtimestamp(reset_time)}")
        
        # Show progress during wait
        for remaining in range(wait_time, 0, -30):
            if remaining > 30:
                logger.info(f"⏳ Rate limit wait: {remaining}s remaining...")
                time.sleep(30)
            else:
                time.sleep(remaining)
                break
        
        logger.info("✅ Emergency rate limit wait completed")
    else:
        logger.error("🚨 EMERGENCY RATE LIMIT HIT! No reset time available, waiting 10 minutes")
        time.sleep(600)  # 10 minutes


def patch_github_client_methods():
    """Patch GitHub client methods with rate limit handling."""
    from . import github_client
    
    # Patch search_files method
    original_search_files = github_client.GitHubClient.search_files
    github_client.GitHubClient.search_files = handle_rate_limit_gracefully(original_search_files)
    
    # Patch get_tree method
    original_get_tree = github_client.GitHubClient.get_tree
    github_client.GitHubClient.get_tree = handle_rate_limit_gracefully(original_get_tree)
    
    # Patch _search_files_tree_api method
    original_tree_api = github_client.GitHubClient._search_files_tree_api
    github_client.GitHubClient._search_files_tree_api = handle_rate_limit_gracefully(original_tree_api)
    
    logger.info("🔧 Rate limit hotfix patches applied to GitHub client")


def apply_emergency_rate_limiting():
    """Apply emergency rate limiting patches."""
    try:
        patch_github_client_methods()
        logger.info("✅ Emergency rate limiting activated")
    except Exception as e:
        logger.error(f"❌ Failed to apply emergency rate limiting: {e}")


# Auto-apply patches when module is imported
apply_emergency_rate_limiting()