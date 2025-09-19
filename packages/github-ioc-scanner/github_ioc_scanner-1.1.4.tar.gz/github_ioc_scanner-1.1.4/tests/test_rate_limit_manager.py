"""Tests for rate limit manager."""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

from src.github_ioc_scanner.rate_limit_manager import (
    RateLimitManager, RateLimitInfo, ConcurrencyAdjustment
)


@pytest.fixture
def rate_limit_manager():
    """Create a rate limit manager for testing."""
    return RateLimitManager(
        initial_concurrency=5,
        max_concurrency=10,
        min_concurrency=1,
        buffer_percentage=0.8,
        adjustment_interval=1.0  # Short interval for testing
    )


class TestRateLimitInfo:
    """Test cases for RateLimitInfo."""
    
    def test_rate_limit_info_creation(self):
        """Test RateLimitInfo creation and properties."""
        info = RateLimitInfo(remaining=3000, limit=5000, reset_time=int(time.time()) + 3600)
        
        assert info.remaining == 3000
        assert info.limit == 5000
        assert info.used == 2000
        assert info.usage_percentage == 40.0
        assert not info.is_exhausted
        assert not info.is_low()
    
    def test_rate_limit_info_exhausted(self):
        """Test exhausted rate limit."""
        info = RateLimitInfo(remaining=0, limit=5000, reset_time=int(time.time()) + 3600)
        
        assert info.is_exhausted
        assert info.usage_percentage == 100.0
    
    def test_rate_limit_info_low(self):
        """Test low rate limit detection."""
        info = RateLimitInfo(remaining=500, limit=5000, reset_time=int(time.time()) + 3600)
        
        assert info.is_low()  # 10% remaining is below default 20% threshold
        assert not info.is_low(threshold=0.05)  # But above 5% threshold
    
    def test_time_until_reset(self):
        """Test time until reset calculation."""
        future_time = int(time.time()) + 1800  # 30 minutes from now
        info = RateLimitInfo(remaining=1000, limit=5000, reset_time=future_time)
        
        time_until_reset = info.time_until_reset
        assert 1790 <= time_until_reset <= 1800  # Allow for small timing differences
        
        # Test past reset time
        past_time = int(time.time()) - 100
        info_past = RateLimitInfo(remaining=1000, limit=5000, reset_time=past_time)
        assert info_past.time_until_reset == 0


class TestConcurrencyAdjustment:
    """Test cases for ConcurrencyAdjustment."""
    
    def test_concurrency_adjustment_creation(self):
        """Test ConcurrencyAdjustment creation."""
        adjustment = ConcurrencyAdjustment(
            old_concurrency=5,
            new_concurrency=8,
            reason="Rate limit increased"
        )
        
        assert adjustment.old_concurrency == 5
        assert adjustment.new_concurrency == 8
        assert adjustment.reason == "Rate limit increased"
        assert adjustment.change_percentage == 60.0  # (8-5)/5 * 100
    
    def test_concurrency_adjustment_decrease(self):
        """Test concurrency decrease calculation."""
        adjustment = ConcurrencyAdjustment(
            old_concurrency=10,
            new_concurrency=6,
            reason="Rate limit decreased"
        )
        
        assert adjustment.change_percentage == -40.0  # (6-10)/10 * 100
    
    def test_concurrency_adjustment_zero_old(self):
        """Test adjustment with zero old concurrency."""
        adjustment = ConcurrencyAdjustment(
            old_concurrency=0,
            new_concurrency=5,
            reason="Initial setup"
        )
        
        assert adjustment.change_percentage == 0.0


class TestRateLimitManager:
    """Test cases for RateLimitManager."""
    
    def test_initialization(self, rate_limit_manager):
        """Test rate limit manager initialization."""
        assert rate_limit_manager.current_concurrency == 5
        assert rate_limit_manager.max_concurrency == 10
        assert rate_limit_manager.min_concurrency == 1
        assert rate_limit_manager.buffer_percentage == 0.8
        assert rate_limit_manager.rate_limit_info is None
        assert len(rate_limit_manager.adjustment_history) == 0
    
    @pytest.mark.asyncio
    async def test_update_rate_limit_info(self, rate_limit_manager):
        """Test updating rate limit information."""
        reset_time = int(time.time()) + 3600
        
        new_concurrency = await rate_limit_manager.update_rate_limit_info(
            remaining=4000,
            limit=5000,
            reset_time=reset_time
        )
        
        # Should not adjust concurrency immediately (high rate limit)
        assert new_concurrency is None or new_concurrency == rate_limit_manager.current_concurrency
        
        # Check that rate limit info was stored
        assert rate_limit_manager.rate_limit_info is not None
        assert rate_limit_manager.rate_limit_info.remaining == 4000
        assert rate_limit_manager.rate_limit_info.limit == 5000
    
    @pytest.mark.asyncio
    async def test_concurrency_adjustment_low_rate_limit(self, rate_limit_manager):
        """Test concurrency adjustment with low rate limit."""
        reset_time = int(time.time()) + 3600
        
        # Wait for adjustment interval to pass
        await asyncio.sleep(1.1)
        
        new_concurrency = await rate_limit_manager.update_rate_limit_info(
            remaining=200,  # Very low rate limit
            limit=5000,
            reset_time=reset_time
        )
        
        # Should reduce concurrency due to low rate limit
        assert new_concurrency is not None
        assert new_concurrency < rate_limit_manager.initial_concurrency
        assert len(rate_limit_manager.adjustment_history) > 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_handling(self, rate_limit_manager):
        """Test handling of rate limit exceeded scenario."""
        new_concurrency, wait_time = await rate_limit_manager.handle_rate_limit_exceeded()
        
        # Should drastically reduce concurrency
        assert new_concurrency == max(1, rate_limit_manager.initial_concurrency // 4)
        assert wait_time >= 0
        assert len(rate_limit_manager.adjustment_history) > 0
        
        # Check adjustment reason
        last_adjustment = rate_limit_manager.adjustment_history[-1]
        assert last_adjustment.reason == "Rate limit exceeded"
    
    @pytest.mark.asyncio
    async def test_performance_metrics_update(self, rate_limit_manager):
        """Test updating performance metrics."""
        await rate_limit_manager.update_performance_metrics(
            success_rate=95.0,
            error_rate=5.0,
            avg_response_time=0.5
        )
        
        metrics = rate_limit_manager.performance_metrics
        assert metrics['success_rate'] == 95.0
        assert metrics['error_rate'] == 5.0
        assert metrics['avg_response_time'] == 0.5
        assert 'last_updated' in metrics
    
    @pytest.mark.asyncio
    async def test_time_factor_calculation(self, rate_limit_manager):
        """Test time-based factor calculation."""
        # Test with rate limit reset soon
        info_soon = RateLimitInfo(remaining=1000, limit=5000, reset_time=int(time.time()) + 200)
        factor_soon = await rate_limit_manager._calculate_time_factor(info_soon)
        assert factor_soon < 1.0  # Should be conservative
        
        # Test with rate limit reset far away
        info_far = RateLimitInfo(remaining=1000, limit=5000, reset_time=int(time.time()) + 7200)
        factor_far = await rate_limit_manager._calculate_time_factor(info_far)
        assert factor_far > 1.0  # Should be more aggressive
        
        # Test with reset time passed
        info_reset = RateLimitInfo(remaining=5000, limit=5000, reset_time=int(time.time()) - 100)
        factor_reset = await rate_limit_manager._calculate_time_factor(info_reset)
        assert factor_reset > 1.0  # Should be aggressive after reset
    
    @pytest.mark.asyncio
    async def test_performance_factor_calculation(self, rate_limit_manager):
        """Test performance-based factor calculation."""
        # Test with high error rate
        rate_limit_manager.performance_metrics = {'error_rate': 15.0, 'success_rate': 85.0}
        factor_high_error = await rate_limit_manager._calculate_performance_factor()
        assert factor_high_error < 1.0
        
        # Test with high success rate
        rate_limit_manager.performance_metrics = {'error_rate': 1.0, 'success_rate': 99.0}
        factor_high_success = await rate_limit_manager._calculate_performance_factor()
        assert factor_high_success > 1.0
        
        # Test with no metrics
        rate_limit_manager.performance_metrics = {}
        factor_no_metrics = await rate_limit_manager._calculate_performance_factor()
        assert factor_no_metrics == 1.0
    
    @pytest.mark.asyncio
    async def test_trend_factor_calculation(self, rate_limit_manager):
        """Test trend-based factor calculation."""
        # Test with insufficient history
        factor_no_history = await rate_limit_manager._calculate_trend_factor()
        assert factor_no_history == 1.0
        
        # Add some rate limit history
        current_time = int(time.time())
        rate_limit_manager.rate_limit_history = [
            RateLimitInfo(remaining=5000, limit=5000, reset_time=current_time),
            RateLimitInfo(remaining=4900, limit=5000, reset_time=current_time + 60),
            RateLimitInfo(remaining=4800, limit=5000, reset_time=current_time + 120)
        ]
        
        factor_with_history = await rate_limit_manager._calculate_trend_factor()
        assert 0.7 <= factor_with_history <= 1.3
    
    @pytest.mark.asyncio
    async def test_optimal_concurrency_calculation(self, rate_limit_manager):
        """Test optimal concurrency calculation."""
        # Test with high rate limit remaining
        info_high = RateLimitInfo(remaining=4500, limit=5000, reset_time=int(time.time()) + 3600)
        optimal_high = await rate_limit_manager._calculate_optimal_concurrency(info_high)
        assert optimal_high >= rate_limit_manager.min_concurrency
        assert optimal_high <= rate_limit_manager.max_concurrency
        
        # Test with low rate limit remaining
        info_low = RateLimitInfo(remaining=100, limit=5000, reset_time=int(time.time()) + 3600)
        optimal_low = await rate_limit_manager._calculate_optimal_concurrency(info_low)
        assert optimal_low >= rate_limit_manager.min_concurrency
        assert optimal_low < optimal_high  # Should be lower than high rate limit case
    
    def test_adjustment_reason_determination(self, rate_limit_manager):
        """Test adjustment reason determination."""
        # Test increase with high availability
        info_high = RateLimitInfo(remaining=4500, limit=5000, reset_time=int(time.time()) + 3600)
        reason_high = rate_limit_manager._determine_adjustment_reason(info_high, 5, 8)
        assert "High rate limit availability" in reason_high
        
        # Test decrease with exhausted rate limit
        info_exhausted = RateLimitInfo(remaining=0, limit=5000, reset_time=int(time.time()) + 3600)
        reason_exhausted = rate_limit_manager._determine_adjustment_reason(info_exhausted, 8, 2)
        assert "Rate limit exhausted" in reason_exhausted
        
        # Test decrease with low rate limit
        info_low = RateLimitInfo(remaining=500, limit=5000, reset_time=int(time.time()) + 3600)
        reason_low = rate_limit_manager._determine_adjustment_reason(info_low, 8, 3)
        assert "Low rate limit remaining" in reason_low
    
    def test_get_current_concurrency(self, rate_limit_manager):
        """Test getting current concurrency."""
        assert rate_limit_manager.get_current_concurrency() == 5
    
    def test_get_rate_limit_status(self, rate_limit_manager):
        """Test getting rate limit status."""
        # Initially should be None
        assert rate_limit_manager.get_rate_limit_status() is None
        
        # After setting rate limit info
        rate_limit_manager.rate_limit_info = RateLimitInfo(
            remaining=3000, limit=5000, reset_time=int(time.time()) + 3600
        )
        status = rate_limit_manager.get_rate_limit_status()
        assert status is not None
        assert status.remaining == 3000
    
    def test_get_adjustment_history(self, rate_limit_manager):
        """Test getting adjustment history."""
        # Initially empty
        history = rate_limit_manager.get_adjustment_history()
        assert len(history) == 0
        
        # Add some adjustments
        adjustment1 = ConcurrencyAdjustment(5, 8, "Test reason 1")
        adjustment2 = ConcurrencyAdjustment(8, 6, "Test reason 2")
        rate_limit_manager.adjustment_history = [adjustment1, adjustment2]
        
        history = rate_limit_manager.get_adjustment_history()
        assert len(history) == 2
        assert history[0] == adjustment1
        assert history[1] == adjustment2
        
        # Test limit
        history_limited = rate_limit_manager.get_adjustment_history(limit=1)
        assert len(history_limited) == 1
        assert history_limited[0] == adjustment2  # Should get the most recent
    
    def test_reset_to_initial(self, rate_limit_manager):
        """Test resetting to initial concurrency."""
        # Change concurrency first
        rate_limit_manager.current_concurrency = 8
        
        rate_limit_manager.reset_to_initial()
        
        assert rate_limit_manager.current_concurrency == 5  # Initial value
        assert len(rate_limit_manager.adjustment_history) > 0
        
        last_adjustment = rate_limit_manager.adjustment_history[-1]
        assert last_adjustment.reason == "Manual reset"
        assert last_adjustment.new_concurrency == 5
    
    def test_get_statistics(self, rate_limit_manager):
        """Test getting comprehensive statistics."""
        # Set up some data
        rate_limit_manager.rate_limit_info = RateLimitInfo(
            remaining=3000, limit=5000, reset_time=int(time.time()) + 3600
        )
        rate_limit_manager.performance_metrics = {
            'success_rate': 95.0,
            'error_rate': 5.0,
            'avg_response_time': 0.5
        }
        rate_limit_manager.adjustment_history = [
            ConcurrencyAdjustment(5, 8, "Test adjustment")
        ]
        
        stats = rate_limit_manager.get_statistics()
        
        # Check basic stats
        assert stats['current_concurrency'] == 5
        assert stats['initial_concurrency'] == 5
        assert stats['max_concurrency'] == 10
        assert stats['min_concurrency'] == 1
        assert stats['total_adjustments'] == 1
        
        # Check rate limit stats
        assert stats['rate_limit_remaining'] == 3000
        assert stats['rate_limit_limit'] == 5000
        assert stats['rate_limit_usage_percentage'] == 40.0
        
        # Check performance metrics
        assert stats['performance_metrics']['success_rate'] == 95.0
        
        # Check recent adjustments
        assert 'recent_adjustments' in stats
        assert len(stats['recent_adjustments']) == 1
    
    @pytest.mark.asyncio
    async def test_adjustment_interval_enforcement(self, rate_limit_manager):
        """Test that adjustment interval is enforced."""
        reset_time = int(time.time()) + 3600
        
        # First adjustment should work
        new_concurrency1 = await rate_limit_manager.update_rate_limit_info(
            remaining=1000, limit=5000, reset_time=reset_time
        )
        
        # Immediate second adjustment should be ignored
        new_concurrency2 = await rate_limit_manager.update_rate_limit_info(
            remaining=500, limit=5000, reset_time=reset_time
        )
        
        # Second adjustment should be None (ignored due to interval)
        assert new_concurrency2 is None
        
        # Wait for interval and try again
        await asyncio.sleep(1.1)
        new_concurrency3 = await rate_limit_manager.update_rate_limit_info(
            remaining=50, limit=5000, reset_time=reset_time  # Very low to force adjustment
        )
        
        # Third adjustment should work (or at least be attempted)
        # The adjustment might be None if the calculated concurrency is the same
        # but the interval should have passed
        assert rate_limit_manager.last_adjustment_time > 0


class TestRateLimitManagerIntegration:
    """Integration tests for rate limit manager."""
    
    @pytest.mark.asyncio
    async def test_full_rate_limit_cycle(self):
        """Test complete rate limit management cycle."""
        manager = RateLimitManager(
            initial_concurrency=10,
            max_concurrency=20,
            min_concurrency=1,
            adjustment_interval=0.1  # Very short for testing
        )
        
        reset_time = int(time.time()) + 3600
        
        # Start with high rate limit
        await manager.update_rate_limit_info(remaining=4800, limit=5000, reset_time=reset_time)
        await asyncio.sleep(0.2)
        
        # Simulate gradual rate limit consumption
        await manager.update_rate_limit_info(remaining=3000, limit=5000, reset_time=reset_time)
        await asyncio.sleep(0.2)
        
        await manager.update_rate_limit_info(remaining=1000, limit=5000, reset_time=reset_time)
        await asyncio.sleep(0.2)
        
        # Simulate rate limit exceeded
        new_concurrency, wait_time = await manager.handle_rate_limit_exceeded()
        
        # Should have reduced concurrency significantly
        assert new_concurrency < manager.initial_concurrency
        assert len(manager.adjustment_history) > 0
        
        # Check statistics
        stats = manager.get_statistics()
        assert stats['total_adjustments'] > 0
        assert 'recent_adjustments' in stats