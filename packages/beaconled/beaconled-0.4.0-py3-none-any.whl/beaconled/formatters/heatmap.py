"""Heatmap formatter for visualizing git repository analytics."""

from __future__ import annotations

import os
import tempfile
from datetime import date as date_type
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    from beaconled.core.models import CommitStats, RangeStats

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    np = None
    LinearSegmentedColormap = None
    MATPLOTLIB_AVAILABLE = False


class HeatmapFormatter(BaseFormatter):
    """Heatmap formatter for visualizing git repository analytics.

    Generates visual heatmaps showing commit activity patterns over time
    and author activity by day of week.
    """

    def __init__(self, output_file: str | None = None, *, show_plot: bool = True):
        """Initialize the heatmap formatter.

        Args:
            output_file: Path to save the heatmap image. If None, saves to temp file.
            show_plot: Whether to display the plot interactively.
        """
        if not MATPLOTLIB_AVAILABLE:
            msg = (
                "matplotlib and numpy are required for heatmap visualization. "
                "Install with: pip install matplotlib numpy"
            )
            raise ImportError(msg)

        self.output_file = output_file
        self.show_plot = show_plot

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as heatmap (not applicable for single commits)."""
        return "Heatmap visualization is only available for date range analysis (--since/--until)"

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as visual heatmaps."""
        if not stats.commits:
            return "No commits found in the specified date range"

        # Ensure extended stats are calculated
        if not hasattr(stats, "commits_by_day") or not stats.commits_by_day:
            stats.calculate_extended_stats()

        # Create the heatmaps
        self._create_activity_heatmap(stats)
        self._create_author_heatmap(stats)

        # Determine output file path
        if self.output_file:
            output_path = self.output_file
        else:
            temp_dir = tempfile.gettempdir()
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(temp_dir, f"beacon_heatmap_{timestamp}.png")

        # Save plots to files
        self._save_plots(output_path)

        message = f"📊 Heatmap visualization saved to: {output_path}"

        if self.show_plot:
            message += "\n💡 The heatmap shows commit activity patterns over time"

        return message

    def _create_activity_heatmap(self, stats: RangeStats) -> None:
        """Create a calendar-style heatmap of daily commit activity."""
        if not MATPLOTLIB_AVAILABLE or not plt or not np:
            return

        if not hasattr(stats, "commits_by_day") or not stats.commits_by_day:
            return

        # Parse dates and commit counts
        dates = []
        commits = []

        for date_str, count in stats.commits_by_day.items():
            try:
                # Handle different date formats that might be in commits_by_day
                if isinstance(date_str, str):
                    # Try different date formats
                    for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]:
                        try:
                            parsed_dt = datetime.strptime(date_str, fmt)  # noqa: DTZ007
                            date_obj = parsed_dt.replace(tzinfo=timezone.utc).date()
                            dates.append(date_obj)
                            commits.append(count)
                            break
                        except ValueError:
                            continue
                    else:
                        # If no format works, skip this date
                        continue
            except (ValueError, AttributeError):
                continue

        if not dates:
            return

        # Sort by date
        date_commit_pairs = sorted(zip(dates, commits, strict=False))
        sorted_dates, sorted_commits = zip(*date_commit_pairs, strict=False)  # type: ignore
        dates = list(sorted_dates)
        commits = list(sorted_commits)

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle("Git Repository Activity Heatmap", fontsize=16, fontweight="bold")

        # Daily activity line plot
        ax1.plot(dates, commits, marker="o", linewidth=2, markersize=4, color="#2E86AB")
        ax1.set_title("Daily Commit Activity", fontsize=14)
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Commits")
        ax1.grid(visible=True, alpha=0.3)  # type: ignore

        # Rotate x-axis labels for better readability
        ax1.tick_params(axis="x", rotation=45)

        # Calendar heatmap (simplified version)
        self._create_calendar_heatmap(ax2, dates, commits)

        plt.tight_layout()

    def _create_calendar_heatmap(
        self,
        ax: Any,
        dates: list[date_type],
        commits: list[int],
    ) -> None:
        """Create a simplified calendar heatmap."""
        if not MATPLOTLIB_AVAILABLE or not plt or not np or not LinearSegmentedColormap:
            return

        # Group by month and day
        month_data: dict[str, dict[int, int]] = {}
        max_commits = max(commits) if commits else 1

        for commit_date, commit_count in zip(dates, commits, strict=False):
            month_key = commit_date.strftime("%Y-%m")
            if month_key not in month_data:
                month_data[month_key] = {}

            day = commit_date.day
            month_data[month_key][day] = commit_count

        # Create a simple grid visualization
        months = sorted(month_data.keys())
        if not months:
            return

        # Use the most recent month for the heatmap
        current_month = months[-1]
        days_in_month = month_data[current_month]

        # Create a 7x5 grid (weeks x days)
        heatmap_data = np.zeros((5, 7))
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        # Fill the grid (simplified - doesn't handle month boundaries perfectly)
        for day, commit_count in days_in_month.items():
            week_row = (day - 1) // 7
            day_col = (day - 1) % 7

            if week_row < 5:  # Stay within our 5-week grid
                heatmap_data[week_row, day_col] = commit_count

        # Create custom colormap
        colors = ["#f7fbff", "#08306b"]  # Light blue to dark blue
        cmap = LinearSegmentedColormap.from_list("custom_blue", colors)

        # Plot heatmap
        im = ax.imshow(heatmap_data, cmap=cmap, aspect="auto")  # type: ignore

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Commits")

        # Set labels
        ax.set_title(f"Commit Activity - {current_month}", fontsize=14)  # type: ignore
        ax.set_xticks(range(7))  # type: ignore
        ax.set_yticks(range(5))  # type: ignore
        ax.set_xticklabels(day_names)  # type: ignore
        ax.set_yticklabels([f"Week {i + 1}" for i in range(5)])  # type: ignore

        # Add commit counts as text
        for i in range(5):
            for j in range(7):
                if heatmap_data[i, j] > 0:
                    ax.text(  # type: ignore
                        j,
                        i,
                        int(heatmap_data[i, j]),
                        ha="center",
                        va="center",
                        color="white" if heatmap_data[i, j] > max_commits * 0.6 else "black",
                        fontweight="bold",
                    )

    def _create_author_heatmap(self, stats: RangeStats) -> None:
        """Create a heatmap showing author activity by day of week."""
        if not MATPLOTLIB_AVAILABLE or not plt or not np or not LinearSegmentedColormap:
            return

        if not hasattr(stats, "author_activity_by_day") or not stats.author_activity_by_day:
            return

        # Extract data
        authors = list(stats.author_activity_by_day.keys())
        if not authors:
            return

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        author_data = []

        for author in authors:
            day_activity = stats.author_activity_by_day[author]
            week_data = [day_activity.get(day, 0) for day in day_names]
            author_data.append(week_data)

        if not author_data:
            return

        # Create heatmap data
        heatmap_data = np.array(author_data)
        max_activity = np.max(heatmap_data) if heatmap_data.size > 0 else 1

        # Create new figure for author heatmap
        _fig, ax = plt.subplots(figsize=(10, max(4, len(authors) * 0.5)))

        # Create custom colormap (green to red for activity levels)
        colors = ["#f7fcf5", "#00441b"]  # Light green to dark green
        cmap = LinearSegmentedColormap.from_list("custom_green", colors)

        # Plot heatmap
        im = ax.imshow(heatmap_data, cmap=cmap, aspect="auto")

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label("Commits")

        # Set labels
        ax.set_title("Author Activity by Day of Week", fontsize=14, fontweight="bold")
        ax.set_xticks(range(len(day_names)))
        ax.set_yticks(range(len(authors)))
        ax.set_xticklabels([day[:3] for day in day_names])  # Abbreviated day names
        ax.set_yticklabels(authors)

        # Add activity counts as text
        for i in range(len(authors)):
            for j in range(len(day_names)):
                count = heatmap_data[i, j]
                if count > 0:
                    ax.text(
                        j,
                        i,
                        count,
                        ha="center",
                        va="center",
                        color="white" if count > max_activity * 0.6 else "black",
                        fontweight="bold",
                    )

        plt.tight_layout()

    def _save_plots(self, output_path: str) -> None:
        """Save all current plots to the specified path."""
        if not MATPLOTLIB_AVAILABLE or not plt:
            return

        # Save all open figures
        for i, fig in enumerate(plt.get_fignums()):
            plt.figure(fig)
            if i == 0:
                # First figure (activity heatmap)
                filename = f"{output_path.rsplit('.', 1)[0]}_activity.png"
            else:
                # Second figure (author heatmap)
                filename = f"{output_path.rsplit('.', 1)[0]}_authors.png"
            plt.savefig(filename, dpi=150, bbox_inches="tight")

        if self.show_plot:
            plt.show()
        else:
            plt.close("all")  # Close all figures to free memory</content>
