"""Chart formatter for generating trend visualizations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    import matplotlib.pyplot as plt  # type: ignore
    import numpy as np  # type: ignore
    import pandas as pd  # type: ignore

    from beaconled.core.models import CommitStats, RangeStats


class ChartFormatter(BaseFormatter):
    """Chart formatter for generating trend visualizations using matplotlib.

    This formatter creates PNG chart files showing development trends over time,
    including commit activity, code health metrics, and contributor patterns.
    """

    def __init__(self, output_path: str = "beacon-charts.png", *, no_emoji: bool = False):
        """Initialize the chart formatter.

        Args:
            output_path: Path where to save the generated chart file
            no_emoji: Whether to disable emoji in console output
        """
        self.output_path = Path(output_path)
        self.no_emoji = no_emoji
        self.plt: plt | None = None
        self.pd: pd | None = None
        self.np: np | None = None
        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """Check if required dependencies for chart generation are available."""
        try:
            import matplotlib.pyplot as plt  # type: ignore
            import numpy as np  # type: ignore
            import pandas as pd  # type: ignore

            self.plt = plt
            self.pd = pd
            self.np = np
        except ImportError as e:
            error_msg = (
                "Chart generation requires matplotlib, pandas, and numpy. "
                "Please install with: pip install matplotlib pandas numpy\n"
                f"Error: {e}"
            )
            raise ImportError(error_msg) from e

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as chart (not supported for single commits)."""
        return (
            "Chart generation is only supported for range analysis (--since flag).\n"
            "Use: beaconled --since 1m --format chart"
        )

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as trend charts."""
        try:
            self._generate_trend_charts(stats)
            return f"📊 Charts generated successfully!\nSaved to: {self.output_path}"
        except Exception as e:
            return f"❌ Error generating charts: {e}"

    def _generate_trend_charts(self, stats: RangeStats) -> None:
        """Generate comprehensive trend charts for the analysis period."""
        if self.plt is None:
            error_msg = "Matplotlib not available"
            raise RuntimeError(error_msg)

        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = self.plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(
            f"Code Health Trends - {stats.start_date.strftime('%Y-%m-%d')} to "
            f"{stats.end_date.strftime('%Y-%m-%d')}",
            fontsize=16,
            fontweight="bold",
        )

        # Chart 1: Commit Activity Timeline
        self._plot_commit_timeline(ax1, stats)

        # Chart 2: Author Contribution Breakdown
        self._plot_author_breakdown(ax2, stats)

        # Chart 3: Code Health Metrics
        self._plot_health_metrics(ax3, stats)

        # Chart 4: File Change Patterns
        self._plot_file_patterns(ax4, stats)

        # Adjust layout and save
        self.plt.tight_layout()
        self.plt.savefig(self.output_path, dpi=300, bbox_inches="tight")
        self.plt.close()

    def _plot_commit_timeline(self, ax: Any, stats: RangeStats) -> None:
        """Plot commit activity over time."""
        if not hasattr(stats, "commits_by_day") or not stats.commits_by_day:
            ax.text(
                0.5,
                0.5,
                "No daily commit data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            ax.set_title("Commit Timeline")
            return

        # Sort dates and create timeline
        dates = sorted(stats.commits_by_day.keys())
        commits = [stats.commits_by_day[date] for date in dates]

        ax.plot(dates, commits, marker="o", linewidth=2, color="#2E86AB", markersize=4)
        ax.set_title("Daily Commit Activity", fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Commits")
        ax.tick_params(axis="x", rotation=45)
        ax.grid(visible=True, alpha=0.3)

        # Add trend line if we have enough data
        if len(dates) > 3:
            try:
                x_numeric = list(range(len(dates)))
                coeffs = self._linear_regression(x_numeric, commits)
                trend_line = [coeffs[0] * x + coeffs[1] for x in x_numeric]
                ax.plot(dates, trend_line, "--", color="#A23B72", alpha=0.7, label="Trend")
                ax.legend()
            except (ValueError, ZeroDivisionError, TypeError):
                # Gracefully skip trend line if statistical calculation fails
                # This is acceptable for optional visualization features
                pass  # nosec B110

    def _plot_author_breakdown(self, ax: Any, stats: RangeStats) -> None:
        """Plot author contribution breakdown."""
        if not stats.authors:
            ax.text(
                0.5,
                0.5,
                "No author data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            ax.set_title("Author Contributions")
            return

        authors = list(stats.authors.keys())
        commits = list(stats.authors.values())

        # Sort by commit count
        sorted_data = sorted(zip(authors, commits, strict=False), key=lambda x: x[1], reverse=True)
        authors_sorted, commits_sorted = zip(*sorted_data, strict=False)

        bars = ax.bar(range(len(authors_sorted)), commits_sorted, color="#F18F01", alpha=0.8)
        ax.set_title("Author Contributions", fontweight="bold")
        ax.set_xlabel("Contributors")
        ax.set_ylabel("Commits")
        ax.set_xticks(range(len(authors_sorted)))
        ax.set_xticklabels(
            [f"Author {i + 1}" for i in range(len(authors_sorted))],
            rotation=45,
            horizontalalignment="right",
        )

        # Add value labels on bars
        for bar, count in zip(bars, commits_sorted, strict=False):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(count),
                horizontalalignment="center",
                verticalalignment="bottom",
                fontweight="bold",
            )

    def _plot_health_metrics(self, ax: Any, stats: RangeStats) -> None:
        """Plot code health metrics."""
        metrics = []

        # Calculate basic health metrics
        if stats.total_commits > 0:
            avg_files_per_commit = stats.total_files_changed / stats.total_commits
            avg_lines_per_commit = (
                stats.total_lines_added + stats.total_lines_deleted
            ) / stats.total_commits

            metrics = [
                ("Avg Files/Commit", avg_files_per_commit, "#2E86AB"),
                ("Avg Lines/Commit", avg_lines_per_commit, "#A23B72"),
                ("Total Commits", stats.total_commits, "#F18F01"),
                ("Total Files", stats.total_files_changed, "#C73E1D"),
            ]
        else:
            metrics = [("Total Commits", 0, "#F18F01"), ("Total Files", 0, "#C73E1D")]

        if not metrics:
            ax.text(
                0.5,
                0.5,
                "No health metrics available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            ax.set_title("Code Health Metrics")
            return

        labels, values, colors = zip(*metrics, strict=False)
        bars = ax.bar(labels, values, color=colors, alpha=0.8)
        ax.set_title("Code Health Metrics", fontweight="bold")
        ax.set_ylabel("Value")
        ax.tick_params(axis="x", rotation=45, labelright=True)

        # Add value labels
        for bar, value in zip(bars, values, strict=False):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f"{value:.1f}",
                horizontalalignment="center",
                verticalalignment="bottom",
                fontweight="bold",
            )

    def _plot_file_patterns(self, ax: Any, stats: RangeStats) -> None:
        """Plot file change patterns."""
        if self.plt is None:
            return

        # Calculate file type statistics from commits
        file_type_counts: dict[str, int] = {}
        for commit in stats.commits:
            for file_stat in commit.files:
                ext = file_stat.path.split(".")[-1] if "." in file_stat.path else "no-ext"
                file_type_counts[ext] = file_type_counts.get(ext, 0) + 1

        if not file_type_counts:
            ax.text(
                0.5,
                0.5,
                "No file type data available",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )
            ax.set_title("File Change Patterns")
            return

        # Get top 8 file types
        sorted_types = sorted(file_type_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        file_types, changes = zip(*sorted_types, strict=False)

        _wedges, texts, autotexts = ax.pie(
            changes,
            labels=file_types,
            autopct="%1.1f%%",
            colors=self.plt.cm.Set3.colors,
            startangle=90,
        )
        ax.set_title("File Types Changed", fontweight="bold")

        # Improve text readability
        for text in texts:
            text.set_fontsize(8)
        for autotext in autotexts:
            autotext.set_fontsize(8)

    def _linear_regression(self, x: list[int], y: list[int]) -> tuple[float, float]:
        """Simple linear regression to calculate trend line."""
        if self.np is None:
            return 0, 0

        x_array = self.np.array(x)
        y_array = self.np.array(y)

        # Calculate coefficients
        n = len(x)
        sum_x = self.np.sum(x_array)
        sum_y = self.np.sum(y_array)
        sum_xy = self.np.sum(x_array * y_array)
        sum_x2 = self.np.sum(x_array * x_array)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        return slope, intercept
