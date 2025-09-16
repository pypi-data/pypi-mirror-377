"""Time-based analytics for commit data.

This module provides comprehensive time-based analysis of git commit patterns,
including velocity trends, activity heatmaps, peak period detection, and bus factor
calculation.
"""

from collections import defaultdict
from dataclasses import dataclass

from beaconled.core.models import CommitStats, RangeStats

from .models import ActivityHeatmap, BusFactor, TimeAnalytics, VelocityTrends


@dataclass
class TimeAnalyzerConfig:
    """Configuration for TimeAnalyzer.

    Attributes:
        velocity_window_days: Number of days for rolling velocity calculation
        peak_threshold: Standard deviations above mean for peak detection
        bus_factor_threshold: Percentage threshold for bus factor calculation
    """

    velocity_window_days: int = 7
    peak_threshold: float = 1.5
    bus_factor_threshold: float = 0.5


class TimeAnalyzer:
    """Analyzes temporal patterns in commit data.

    This class provides comprehensive time-based analytics including:
    - Commit velocity trends over time
    - Activity heatmaps by day and hour
    - Peak activity period identification
    - Team bus factor calculation
    """

    def __init__(self, config: TimeAnalyzerConfig):
        """Initialize the TimeAnalyzer with configuration.

        Args:
            config: TimeAnalyzerConfig object with analysis parameters
        """
        self.velocity_window_days = config.velocity_window_days
        self.peak_threshold = config.peak_threshold
        self.bus_factor_threshold = config.bus_factor_threshold

    def analyze(self, range_stats: RangeStats) -> TimeAnalytics:
        """Generate comprehensive time-based analytics.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            TimeAnalytics object with all time-based analysis results
        """
        return TimeAnalytics(
            velocity_trends=self._calculate_velocity_trends(range_stats.commits),
            activity_heatmap=self._generate_activity_heatmap(range_stats.commits),
            peak_periods=self._identify_peak_periods(range_stats.commits),
            bus_factor=self._calculate_bus_factor(range_stats.authors),
        )

    def _calculate_velocity_trends(self, commits: list[CommitStats]) -> VelocityTrends:
        """Calculate commit velocity trends over time.

        Args:
            commits: List of CommitStats objects

        Returns:
            VelocityTrends object with velocity analysis
        """
        if not commits:
            return VelocityTrends(
                daily_velocity={},
                weekly_average=0.0,
                trend_direction="stable",
                peak_velocity=("", 0.0),
            )

        # Group commits by date
        daily_commits: dict[str, int] = defaultdict(int)
        for commit in commits:
            date_key = commit.date.strftime("%Y-%m-%d")
            daily_commits[date_key] += 1

        # Calculate daily velocity (commits per day)
        daily_velocity = {date: float(count) for date, count in daily_commits.items()}

        # Calculate weekly average
        total_commits = sum(daily_commits.values())
        date_range = (
            max(commits, key=lambda c: c.date).date - min(commits, key=lambda c: c.date).date
        ).days + 1
        weekly_average = (total_commits / max(date_range, 1)) * 7

        # Determine trend direction (simplified: compare first and last week)
        sorted_dates = sorted(daily_commits.keys())
        if len(sorted_dates) >= 14:  # Need at least 2 weeks
            mid_point = len(sorted_dates) // 2
            first_half_avg = sum(daily_commits[d] for d in sorted_dates[:mid_point]) / mid_point
            second_half_avg = sum(daily_commits[d] for d in sorted_dates[mid_point:]) / (
                len(sorted_dates) - mid_point
            )

            if second_half_avg > first_half_avg * 1.1:
                trend_direction = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        # Find peak velocity
        peak_date = max(daily_velocity.keys(), key=lambda d: daily_velocity[d])
        peak_velocity = (peak_date, daily_velocity[peak_date])

        return VelocityTrends(
            daily_velocity=daily_velocity,
            weekly_average=weekly_average,
            trend_direction=trend_direction,
            peak_velocity=peak_velocity,
        )

    def _generate_activity_heatmap(self, commits: list[CommitStats]) -> ActivityHeatmap:
        """Generate activity heatmap by day of week and hour.

        Args:
            commits: List of CommitStats objects

        Returns:
            ActivityHeatmap object with activity patterns
        """
        if not commits:
            return ActivityHeatmap(by_day_of_week={}, by_hour={}, peak_day="", peak_hour=0)

        day_counts: dict[str, int] = defaultdict(int)
        hour_counts: dict[int, int] = defaultdict(int)

        for commit in commits:
            day_name = commit.date.strftime("%A")
            hour = commit.date.hour

            day_counts[day_name] += 1
            hour_counts[hour] += 1

        # Find peak day and hour
        peak_day = max(day_counts.keys(), key=lambda d: day_counts[d]) if day_counts else ""
        peak_hour = max(hour_counts.keys(), key=lambda h: hour_counts[h]) if hour_counts else 0

        return ActivityHeatmap(
            by_day_of_week=dict(day_counts),
            by_hour=dict(hour_counts),
            peak_day=peak_day,
            peak_hour=peak_hour,
        )

    def _identify_peak_periods(self, commits: list[CommitStats]) -> list[tuple[str, int]]:
        """Identify peak activity periods.

        Args:
            commits: List of CommitStats objects

        Returns:
            List of (date, commit_count) tuples for peak periods
        """
        if not commits:
            return []

        # Group by date
        daily_counts: dict[str, int] = defaultdict(int)
        for commit in commits:
            date_key = commit.date.strftime("%Y-%m-%d")
            daily_counts[date_key] += 1

        if not daily_counts:
            return []

        # Calculate mean and standard deviation
        counts = list(daily_counts.values())
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = variance**0.5

        # Identify peaks above threshold
        threshold = mean + (self.peak_threshold * std_dev)
        peaks = [(date, count) for date, count in daily_counts.items() if count >= threshold]

        return sorted(peaks, key=lambda x: x[1], reverse=True)

    def _calculate_bus_factor(self, authors: dict[str, int]) -> BusFactor:
        """Calculate team bus factor.

        Args:
            authors: Dictionary mapping author names to commit counts

        Returns:
            BusFactor object with risk analysis
        """
        if not authors:
            return BusFactor(factor=0, key_contributors=[], risk_level="high")

        total_commits = sum(authors.values())
        if total_commits == 0:
            return BusFactor(factor=0, key_contributors=[], risk_level="high")

        # Sort authors by contribution
        sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)

        # Calculate cumulative percentage
        cumulative = 0.0
        factor = 0
        key_contributors = []

        for author, commits in sorted_authors:
            percentage = commits / total_commits
            cumulative += percentage
            factor += 1
            key_contributors.append((author, percentage))

            if cumulative >= self.bus_factor_threshold:
                break

        # Determine risk level
        if factor <= 1:
            risk_level = "high"
        elif factor <= 3:
            risk_level = "medium"
        else:
            risk_level = "low"

        return BusFactor(factor=factor, key_contributors=key_contributors, risk_level=risk_level)
