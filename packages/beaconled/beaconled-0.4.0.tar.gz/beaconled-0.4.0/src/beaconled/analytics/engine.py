"""Analytics engine for integrating all analytics components.

This module provides the AnalyticsEngine class that integrates all the
analytics components (time, team, quality, risk) into a unified system
for the extended format.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from beaconled.core.models import RangeStats

from .collaboration_analyzer import CollaborationAnalyzer, CollaborationConfig
from .quality_analyzer import QualityAnalyzer, QualityConfig
from .risk_analyzer import RiskAnalyzer, RiskConfig
from .time_analyzer import TimeAnalyzer, TimeAnalyzerConfig

if TYPE_CHECKING:
    from beaconled.formatters.base_formatter import BaseFormatter
    from beaconled.formatters.chart import ChartFormatter as ChartRenderer
    from beaconled.formatters.heatmap import HeatmapFormatter as HeatmapRenderer


@dataclass
class RangeStatsWithAnalytics(RangeStats):
    """Wrapper for RangeStats that includes analytics data."""

    analytics: dict | None = None


class AnalyticsEngine:
    """Integrated analytics engine for all analysis components.

    This engine coordinates the various analytics components to provide
    a comprehensive analysis of repository data.
    """

    def __init__(self) -> None:
        """Initialize the analytics engine with all component analyzers."""
        # Time-based analytics
        self.time_analyzer = TimeAnalyzer(TimeAnalyzerConfig())

        # Team collaboration analytics
        self.collaboration_analyzer = CollaborationAnalyzer(CollaborationConfig())

        # Code quality analytics
        self.quality_analyzer = QualityAnalyzer(QualityConfig())

        # Risk assessment analytics
        self.risk_analyzer = RiskAnalyzer(RiskConfig())

        # Caching for performance optimization
        self._cache: dict[Any, Any] = {}
        self._max_cache_size = 100  # Maximum number of results to cache

    def analyze(self, range_stats: RangeStats) -> dict[str, Any]:
        """Perform comprehensive analysis on range statistics.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing all analytics results with the following structure:
            {
                'time': {...},  # Time-based analytics
                'collaboration': {...},  # Team collaboration analytics
                'quality': {...},  # Code quality metrics
                'risk': {...}  # Risk assessment
            }
        """
        # Create a cache key based on the range stats
        cache_key = self._get_cache_key(range_stats)

        # Check if we have cached results
        if cache_key in self._cache:
            return cast("dict[str, Any]", self._cache[cache_key])

        # Perform all analyses in parallel (could be optimized with threads/async)
        time_analytics = self.time_analyzer.analyze(range_stats)
        collaboration_analytics = self.collaboration_analyzer.analyze(range_stats)
        quality_analytics = self.quality_analyzer.analyze(range_stats)
        risk_analytics = self.risk_analyzer.analyze(range_stats)

        # Combine all results
        result = {
            "time": time_analytics,
            "collaboration": collaboration_analytics,
            "quality": quality_analytics,
            "risk": risk_analytics,
        }

        # Cache the result
        self._cache_result(cache_key, result)

        return result

    def _get_cache_key(self, range_stats: RangeStats) -> tuple:
        """Generate a cache key for the given range stats."""
        return (
            range_stats.total_commits,
            range_stats.start_date.isoformat(),
            range_stats.end_date.isoformat(),
            # Include any other relevant attributes for cache key
            tuple(sorted(range_stats.authors.items())) if range_stats.authors else (),
        )

    def _cache_result(self, key: Any, result: dict[str, Any]) -> None:
        """Cache the result and ensure cache doesn't exceed max size."""
        self._cache[key] = result

        # Remove oldest entries if cache is too large
        while len(self._cache) > self._max_cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]


class ExtendedFormatSystem:
    """Integrated system for the extended format.

    This system integrates all analytics, visualization, and formatting
    components into a cohesive pipeline for the extended format.
    """

    def __init__(self) -> None:
        """Initialize the extended format system."""
        # Analytics pipeline
        self.analytics_engine = AnalyticsEngine()

        # Visualization pipeline
        self.chart_renderer: ChartRenderer | None = None
        self.heatmap_renderer: HeatmapRenderer | None = None

        # Formatter for the output
        self.formatter: BaseFormatter | None = None

    def analyze(self, range_stats: RangeStats) -> dict[str, Any]:
        """Perform analysis on the given range stats.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing all analytics results
        """
        return self.analytics_engine.analyze(range_stats)

    def format_analysis(self, range_stats: RangeStats) -> str:
        """Format the analysis results as a string.

        Args:
            range_stats: The range statistics to analyze and format

        Returns:
            Formatted analysis as a string
        """
        if not self.formatter:
            error_msg = "No formatter configured for ExtendedFormatSystem"
            raise ValueError(error_msg)

        # Perform analysis
        analytics = self.analyze(range_stats)

        # Create a wrapper with analytics
        stats_with_analytics = RangeStatsWithAnalytics(
            **{k: v for k, v in vars(range_stats).items() if not k.startswith("_")},
            analytics=analytics,
        )

        # Format the results
        return self.formatter.format_range_stats(stats_with_analytics)

    def set_formatter(self, formatter: "BaseFormatter") -> None:
        """Set the formatter for the system.

        Args:
            formatter: The formatter to use for output
        """
        self.formatter = formatter

    def set_chart_renderer(self, renderer: "ChartRenderer") -> None:
        """Set the chart renderer for the system.

        Args:
            renderer: The chart renderer to use
        """
        self.chart_renderer = renderer

    def set_heatmap_renderer(self, renderer: "HeatmapRenderer") -> None:
        """Set the heatmap renderer for the system.

        Args:
            renderer: The heatmap renderer to use
        """
        self.heatmap_renderer = renderer
