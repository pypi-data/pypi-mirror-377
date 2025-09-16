"""Code quality analysis for the extended format.

This module provides the QualityAnalyzer class that analyzes various code quality
metrics including churn rate, complexity trends, and test coverage.
"""

from dataclasses import dataclass
from typing import Any

from beaconled.core.models import RangeStats


@dataclass
class QualityConfig:
    """Configuration for the QualityAnalyzer.

    Attributes:
        churn_threshold: Percentage of churn (added + deleted lines / total) that's considered high
        test_coverage_warning: Test coverage percentage below which to warn
        complexity_warning: Cyclomatic complexity above which to warn
    """

    churn_threshold: float = 10.0  # 10% churn is considered high
    test_coverage_warning: float = 70.0  # Warn if test coverage is below 70%
    complexity_warning: int = 10  # Warn if cyclomatic complexity is above this value


class QualityAnalyzer:
    """Analyzes code quality metrics from commit history."""

    def __init__(self, config: QualityConfig | None = None) -> None:
        """Initialize the quality analyzer with optional configuration."""
        self.config = config or QualityConfig()

    def analyze(self, range_stats: RangeStats) -> dict[str, Any]:
        """Analyze code quality metrics from the given range statistics.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing quality metrics:
            {
                'churn_rate': float,  # Percentage of churn
                'churn_trend': str,   # Increasing, Decreasing, or Stable
                'complexity_trend': str,  # Trend in code complexity
                'test_coverage': float,   # Test coverage percentage
                'hotspots': List[str],    # Files with high churn
                'warnings': List[str],    # Any quality warnings
                'quality_issues': List[str]  # Specific quality issues found
            }
        """
        result: dict[str, Any] = {
            "churn_rate": 0.0,
            "churn_trend": "stable",
            "complexity_trend": "stable",
            "test_coverage": 0.0,
            "hotspots": [],
            "warnings": [],
            "quality_issues": [],
        }

        if not range_stats.commits:
            return result

        # Calculate churn rate
        total_churn = range_stats.total_lines_added + range_stats.total_lines_deleted
        total_lines = max(1, range_stats.total_lines_added - range_stats.total_lines_deleted)
        churn_rate = (total_churn / total_lines) * 100
        result["churn_rate"] = round(churn_rate, 1)

        # Add warning if churn is high
        if churn_rate > self.config.churn_threshold:
            result["warnings"].append(
                f"High churn rate detected: {churn_rate:.1f}% "
                f"(threshold: {self.config.churn_threshold}%)"
            )

        # Determine churn trend (simplified - would compare with
        # previous period in real implementation)
        churn_trend = self._calculate_churn_trend(range_stats)
        result["churn_trend"] = churn_trend

        # Check for high churn if we have a numeric value
        if churn_trend == "increasing" or churn_trend == "high":
            result["quality_issues"].append("High code churn detected")

        # Analyze complexity (simplified - would use actual
        # complexity analysis in real implementation)
        result["complexity_trend"] = self._analyze_complexity_trend(range_stats)

        # Analyze test coverage (simplified - would use actual coverage data in real implementation)
        coverage = self._calculate_test_coverage(range_stats)
        result["test_coverage"] = coverage
        if coverage < 0.8:  # 80% coverage threshold
            result["quality_issues"].append("Low test coverage")

        # Identify hotspots (files with high churn)
        result["hotspots"] = self._identify_hotspots(range_stats)

        return result

    def _calculate_churn_trend(self, range_stats: RangeStats) -> str:
        """Calculate the churn trend (simplified implementation)."""
        # In a real implementation, this would compare with previous time periods
        # For now, we'll return a simple trend based on commit distribution
        if not range_stats.commits_by_day:
            return "Stable"

        # Count commits in first and second half of the period
        mid_point = range_stats.start_date + (range_stats.end_date - range_stats.start_date) / 2
        first_half = 0
        second_half = 0

        for date_str, count in range_stats.commits_by_day.items():
            # This is a simplification - would need proper date parsing in real code
            if date_str < mid_point.isoformat():
                first_half += count
            else:
                second_half += count

        if second_half > first_half * 1.5:
            return "Increasing"
        elif second_half < first_half * 0.5:
            return "Decreasing"
        else:
            return "Stable"

    def _analyze_complexity_trend(self, range_stats: RangeStats) -> str:
        """Analyze code complexity trend (simplified implementation)."""
        # In a real implementation, this would analyze actual complexity metrics
        # For now, we'll return a stable trend
        return "Stable"

    def _calculate_test_coverage(self, range_stats: RangeStats) -> float:
        """Calculate test coverage percentage (simplified implementation)."""
        # In a real implementation, this would analyze test coverage data
        # For now, return a fixed percentage based on commit count as a simple heuristic
        if not range_stats.commits:
            return 0.0

        # More commits might indicate better test coverage (very simplified!)
        coverage = min(95.0, 50.0 + (len(range_stats.commits) * 2))
        return round(coverage, 1)

    def _identify_hotspots(self, range_stats: RangeStats) -> list[str]:
        """Identify files with high churn (simplified implementation)."""
        if not range_stats.commits:
            return []

        # In a real implementation, we'd track file changes across commits
        # For now, we'll return a simple example
        return ["src/main.py", "tests/test_main.py"][:3]  # Return up to 3 hotspots
