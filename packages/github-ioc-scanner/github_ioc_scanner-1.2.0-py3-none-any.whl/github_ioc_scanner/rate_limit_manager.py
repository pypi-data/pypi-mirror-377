"""Rate limit manager for intelligent concurrency adjustment."""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimitInfo:
    """Information about GitHub API rate limits."""
    remaining: int
    limit: int
    reset_time: int
    used: int = field(init=False)
    
    def __post_init__(self):
        """Calculate used rate limit."""
        self.used = self.limit - self.remaining
    
    @property
    def usage_percentage(self) -> float:
        """Calculate rate limit usage as percentage."""
        if self.limit == 0:
            return 0.0
        return (self.used / self.limit) * 100
    
    @property
    def time_until_reset(self) -> float:
        """Calculate seconds until rate limit reset."""
        return max(0, self.reset_time - time.time())
    
    @property
    def is_exhausted(self) -> bool:
        """Check if rate limit is exhausted."""
        return self.remaining <= 0
    
    def is_low(self, threshold: float = 0.2) -> bool:
        """Check if rate limit is low (below threshold)."""
        return (self.remaining / self.limit) < threshold if self.limit > 0 else True


@dataclass
class ConcurrencyAdjustment:
    """Represents a concurrency adjustment decision."""
    old_concurrency: int
    new_concurrency: int
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def change_percentage(self) -> float:
        """Calculate percentage change in concurrency."""
        if self.old_concurrency == 0:
            return 0.0
        return ((self.new_concurrency - self.old_concurrency) / self.old_concurrency) * 100


class RateLimitManager:
    """Manages GitHub API rate limits and adjusts concurrency accordingly."""
    
    def __init__(
        self,
        initial_concurrency: int = 10,
        max_concurrency: int = 20,
        min_concurrency: int = 1,
        buffer_percentage: float = 0.8,
        adjustment_interval: float = 30.0
    ):
        """Initialize rate limit manager.
        
        Args:
            initial_concurrency: Initial concurrency level
            max_concurrency: Maximum allowed concurrency
            min_concurrency: Minimum allowed concurrency
            buffer_percentage: Percentage of rate limit to use as buffer
            adjustment_interval: Minimum seconds between adjustments
        """
        self.initial_concurrency = initial_concurrency
        self.max_concurrency = max_concurrency
        self.min_concurrency = min_concurrency
        self.buffer_percentage = buffer_percentage
        self.adjustment_interval = adjustment_interval
        
        # Current state
        self.current_concurrency = initial_concurrency
        self.rate_limit_info: Optional[RateLimitInfo] = None
        self.last_adjustment_time = 0.0
        
        # History tracking
        self.adjustment_history: List[ConcurrencyAdjustment] = []
        self.rate_limit_history: List[RateLimitInfo] = []
        self.performance_metrics: Dict[str, float] = {}
        
        # Locks for thread safety
        self._adjustment_lock = asyncio.Lock()
        self._history_lock = asyncio.Lock()
    
    async def update_rate_limit_info(
        self,
        remaining: int,
        limit: int,
        reset_time: int
    ) -> Optional[int]:
        """Update rate limit information and potentially adjust concurrency.
        
        Args:
            remaining: Remaining rate limit
            limit: Total rate limit
            reset_time: Reset timestamp
            
        Returns:
            New concurrency level if adjusted, None otherwise
        """
        # Create new rate limit info
        new_info = RateLimitInfo(
            remaining=remaining,
            limit=limit,
            reset_time=reset_time
        )
        
        # Store in history
        async with self._history_lock:
            self.rate_limit_info = new_info
            self.rate_limit_history.append(new_info)
            
            # Keep only recent history (last 100 entries)
            if len(self.rate_limit_history) > 100:
                self.rate_limit_history = self.rate_limit_history[-100:]
        
        # Check if adjustment is needed
        return await self._evaluate_concurrency_adjustment(new_info)
    
    async def _evaluate_concurrency_adjustment(
        self,
        rate_limit_info: RateLimitInfo
    ) -> Optional[int]:
        """Evaluate whether concurrency adjustment is needed.
        
        Args:
            rate_limit_info: Current rate limit information
            
        Returns:
            New concurrency level if adjustment needed, None otherwise
        """
        async with self._adjustment_lock:
            current_time = time.time()
            
            # Check if enough time has passed since last adjustment
            if current_time - self.last_adjustment_time < self.adjustment_interval:
                return None
            
            old_concurrency = self.current_concurrency
            new_concurrency = await self._calculate_optimal_concurrency(rate_limit_info)
            
            # Only adjust if there's a significant change
            if abs(new_concurrency - old_concurrency) >= 1:
                reason = self._determine_adjustment_reason(rate_limit_info, old_concurrency, new_concurrency)
                
                adjustment = ConcurrencyAdjustment(
                    old_concurrency=old_concurrency,
                    new_concurrency=new_concurrency,
                    reason=reason
                )
                
                self.adjustment_history.append(adjustment)
                self.current_concurrency = new_concurrency
                self.last_adjustment_time = current_time
                
                logger.info(
                    f"Concurrency adjusted: {old_concurrency} -> {new_concurrency} "
                    f"({adjustment.change_percentage:+.1f}%) - {reason}"
                )
                
                return new_concurrency
            
            return None
    
    async def _calculate_optimal_concurrency(
        self,
        rate_limit_info: RateLimitInfo
    ) -> int:
        """Calculate optimal concurrency based on rate limit information.
        
        Args:
            rate_limit_info: Current rate limit information
            
        Returns:
            Optimal concurrency level
        """
        # Base calculation on remaining rate limit
        remaining_ratio = rate_limit_info.remaining / rate_limit_info.limit if rate_limit_info.limit > 0 else 0
        
        # Calculate time-based factor
        time_factor = await self._calculate_time_factor(rate_limit_info)
        
        # Calculate performance-based factor
        performance_factor = await self._calculate_performance_factor()
        
        # Calculate trend-based factor
        trend_factor = await self._calculate_trend_factor()
        
        # Combine factors to determine optimal concurrency
        base_concurrency = self.max_concurrency * remaining_ratio * self.buffer_percentage
        adjusted_concurrency = base_concurrency * time_factor * performance_factor * trend_factor
        
        # Apply bounds
        optimal_concurrency = max(
            self.min_concurrency,
            min(self.max_concurrency, int(adjusted_concurrency))
        )
        
        logger.debug(
            f"Concurrency calculation: remaining_ratio={remaining_ratio:.3f}, "
            f"time_factor={time_factor:.3f}, performance_factor={performance_factor:.3f}, "
            f"trend_factor={trend_factor:.3f}, optimal={optimal_concurrency}"
        )
        
        return optimal_concurrency
    
    async def _calculate_time_factor(self, rate_limit_info: RateLimitInfo) -> float:
        """Calculate time-based adjustment factor.
        
        Args:
            rate_limit_info: Current rate limit information
            
        Returns:
            Time-based factor (0.5 to 2.0)
        """
        time_until_reset = rate_limit_info.time_until_reset
        
        if time_until_reset <= 0:
            # Rate limit has reset, can be more aggressive
            return 1.5
        elif time_until_reset < 300:  # Less than 5 minutes
            # Close to reset, be conservative
            return 0.7
        elif time_until_reset < 1800:  # Less than 30 minutes
            # Moderate time remaining
            return 1.0
        else:
            # Plenty of time, can be more aggressive
            return 1.2
    
    async def _calculate_performance_factor(self) -> float:
        """Calculate performance-based adjustment factor.
        
        Returns:
            Performance-based factor (0.5 to 1.5)
        """
        # Return neutral factor if no metrics available
        if not self.performance_metrics:
            return 1.0
        
        # Check recent error rates
        recent_error_rate = self.performance_metrics.get('error_rate', 0.0)
        recent_success_rate = self.performance_metrics.get('success_rate', 0.0)
        
        if recent_error_rate > 10.0:  # High error rate (percentage)
            return 0.6
        elif recent_success_rate > 95.0:  # High success rate (percentage)
            return 1.2
        else:
            return 1.0
    
    async def _calculate_trend_factor(self) -> float:
        """Calculate trend-based adjustment factor.
        
        Returns:
            Trend-based factor (0.7 to 1.3)
        """
        async with self._history_lock:
            if len(self.rate_limit_history) < 3:
                return 1.0
            
            # Analyze recent rate limit consumption trend
            recent_info = self.rate_limit_history[-3:]
            consumption_rates = []
            
            for i in range(1, len(recent_info)):
                prev_info = recent_info[i-1]
                curr_info = recent_info[i]
                
                # Calculate consumption rate (requests per second)
                time_diff = curr_info.reset_time - prev_info.reset_time
                if time_diff > 0:
                    requests_made = prev_info.remaining - curr_info.remaining
                    consumption_rate = requests_made / time_diff
                    consumption_rates.append(consumption_rate)
            
            if not consumption_rates:
                return 1.0
            
            avg_consumption_rate = sum(consumption_rates) / len(consumption_rates)
            
            # Adjust based on consumption trend
            if avg_consumption_rate > 10:  # High consumption rate
                return 0.8
            elif avg_consumption_rate < 2:  # Low consumption rate
                return 1.2
            else:
                return 1.0
    
    def _determine_adjustment_reason(
        self,
        rate_limit_info: RateLimitInfo,
        old_concurrency: int,
        new_concurrency: int
    ) -> str:
        """Determine the reason for concurrency adjustment.
        
        Args:
            rate_limit_info: Current rate limit information
            old_concurrency: Previous concurrency level
            new_concurrency: New concurrency level
            
        Returns:
            Human-readable reason for adjustment
        """
        if new_concurrency > old_concurrency:
            if rate_limit_info.remaining > rate_limit_info.limit * 0.8:
                return "High rate limit availability"
            elif rate_limit_info.time_until_reset < 300:
                return "Rate limit reset approaching"
            else:
                return "Performance optimization"
        else:
            if rate_limit_info.is_exhausted:
                return "Rate limit exhausted"
            elif rate_limit_info.is_low():
                return "Low rate limit remaining"
            elif self.performance_metrics.get('error_rate', 0) > 0.1:
                return "High error rate detected"
            else:
                return "Conservative adjustment"
    
    async def handle_rate_limit_exceeded(self) -> Tuple[int, float]:
        """Handle rate limit exceeded scenario.
        
        Returns:
            Tuple of (new_concurrency, wait_time_seconds)
        """
        async with self._adjustment_lock:
            # Drastically reduce concurrency
            old_concurrency = self.current_concurrency
            new_concurrency = max(1, self.current_concurrency // 4)
            
            wait_time = 0.0
            if self.rate_limit_info:
                wait_time = self.rate_limit_info.time_until_reset
            
            # Record adjustment
            adjustment = ConcurrencyAdjustment(
                old_concurrency=old_concurrency,
                new_concurrency=new_concurrency,
                reason="Rate limit exceeded"
            )
            
            self.adjustment_history.append(adjustment)
            self.current_concurrency = new_concurrency
            self.last_adjustment_time = time.time()
            
            logger.warning(
                f"Rate limit exceeded! Concurrency reduced: {old_concurrency} -> {new_concurrency}, "
                f"waiting {wait_time:.1f}s"
            )
            
            return new_concurrency, wait_time
    
    async def update_performance_metrics(
        self,
        success_rate: float,
        error_rate: float,
        avg_response_time: float
    ) -> None:
        """Update performance metrics for adjustment calculations.
        
        Args:
            success_rate: Success rate percentage (0-100)
            error_rate: Error rate percentage (0-100)
            avg_response_time: Average response time in seconds
        """
        self.performance_metrics.update({
            'success_rate': success_rate,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'last_updated': time.time()
        })
        
        logger.debug(
            f"Performance metrics updated: success_rate={success_rate:.1f}%, "
            f"error_rate={error_rate:.1f}%, avg_response_time={avg_response_time:.3f}s"
        )
    
    def get_current_concurrency(self) -> int:
        """Get current concurrency level.
        
        Returns:
            Current concurrency level
        """
        return self.current_concurrency
    
    def get_rate_limit_status(self) -> Optional[RateLimitInfo]:
        """Get current rate limit status.
        
        Returns:
            Current rate limit information or None if not available
        """
        return self.rate_limit_info
    
    def get_adjustment_history(self, limit: int = 10) -> List[ConcurrencyAdjustment]:
        """Get recent concurrency adjustment history.
        
        Args:
            limit: Maximum number of adjustments to return
            
        Returns:
            List of recent concurrency adjustments
        """
        return self.adjustment_history[-limit:] if self.adjustment_history else []
    
    def reset_to_initial(self) -> None:
        """Reset concurrency to initial level."""
        old_concurrency = self.current_concurrency
        self.current_concurrency = self.initial_concurrency
        
        if old_concurrency != self.initial_concurrency:
            adjustment = ConcurrencyAdjustment(
                old_concurrency=old_concurrency,
                new_concurrency=self.initial_concurrency,
                reason="Manual reset"
            )
            self.adjustment_history.append(adjustment)
            
            logger.info(f"Concurrency reset to initial level: {old_concurrency} -> {self.initial_concurrency}")
    
    def get_statistics(self) -> Dict[str, any]:
        """Get comprehensive statistics about rate limit management.
        
        Returns:
            Dictionary containing various statistics
        """
        stats = {
            'current_concurrency': self.current_concurrency,
            'initial_concurrency': self.initial_concurrency,
            'max_concurrency': self.max_concurrency,
            'min_concurrency': self.min_concurrency,
            'total_adjustments': len(self.adjustment_history),
            'performance_metrics': self.performance_metrics.copy()
        }
        
        if self.rate_limit_info:
            stats.update({
                'rate_limit_remaining': self.rate_limit_info.remaining,
                'rate_limit_limit': self.rate_limit_info.limit,
                'rate_limit_usage_percentage': self.rate_limit_info.usage_percentage,
                'time_until_reset': self.rate_limit_info.time_until_reset
            })
        
        if self.adjustment_history:
            recent_adjustments = self.adjustment_history[-5:]
            stats['recent_adjustments'] = [
                {
                    'old': adj.old_concurrency,
                    'new': adj.new_concurrency,
                    'change_pct': adj.change_percentage,
                    'reason': adj.reason,
                    'timestamp': adj.timestamp.isoformat()
                }
                for adj in recent_adjustments
            ]
        
        return stats