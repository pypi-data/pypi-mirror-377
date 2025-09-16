"""ASCII chart formatter for Beacon delivery analytics.

This module provides ASCII-based chart visualizations for git repository statistics,
including bar charts, pie charts, and other visual representations that work in
terminal environments without requiring graphical libraries.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from colorama import Fore, Style

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    # Only import for typing to avoid runtime import cycles
    from beaconled.core.models import CommitStats, RangeStats


class ASCIIChartFormatter(BaseFormatter):
    """ASCII chart formatter for visualizing git repository analytics.

    Provides various ASCII-based charts including:
    - Bar charts for daily activity
    - Pie charts for author contributions
    - Component activity visualizations
    - Impact distribution charts
    """

    def __init__(self, width: int = 80, height: int = 20):
        """Initialize the ASCII chart formatter.

        Args:
            width: Maximum width of charts in characters
            height: Maximum height of charts in characters
        """
        self.width = width
        self.height = height
        self.chart_chars = {
            "bar_full": "█",
            "bar_half": "▌",
            "bar_quarter": "▎",
            "pie_full": "●",
            "pie_empty": "○",
            "line_horizontal": "─",
            "line_vertical": "│",
            "corner_top_left": "┌",
            "corner_top_right": "┐",
            "corner_bottom_left": "└",
            "corner_bottom_right": "┘",
            "tee_right": "├",
            "tee_left": "┤",
            "cross": "┼",
        }

    def _create_bar_chart(
        self, data: dict[str, int], title: str = "", max_width: int | None = None
    ) -> str:
        """Create an ASCII bar chart from data.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            max_width: Maximum width for bars (defaults to self.width)

        Returns:
            str: ASCII bar chart representation
        """
        if not data:
            return "No data available for chart"

        if max_width is None:
            max_width = self.width - 20  # Leave space for labels

        # Find max value for scaling
        max_value = max(data.values()) if data else 0
        if max_value == 0:
            return "No activity data to display"

        # Sort data for consistent display
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

        lines = []
        if title:
            lines.append(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
            lines.append("")

        for label, value in sorted_data[:10]:  # Show top 10
            # Calculate bar length
            if max_value > 0:
                bar_length = int((value / max_value) * max_width)
            else:
                bar_length = 0

            # Create bar with full blocks
            bar = self.chart_chars["bar_full"] * bar_length

            # Format line
            lines.append(f"{label[:15]:<15} {bar}")

        return "\n".join(lines)

    def _create_pie_chart(self, data: dict[str, int], title: str = "", radius: int = 8) -> str:
        """Create an ASCII pie chart from data.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            radius: Radius of the pie chart

        Returns:
            str: ASCII pie chart representation
        """
        if not data:
            return "No data available for chart"

        total = sum(data.values())
        if total == 0:
            return "No data to display"

        # Calculate percentages
        percentages = {}

        for label, value in data.items():
            percentage = (value / total) * 100
            percentages[label] = percentage

        # Sort by percentage for legend
        sorted_items = sorted(percentages.items(), key=lambda x: x[1], reverse=True)

        lines = []
        if title:
            lines.append(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
            lines.append("")

        # Create a simple pie representation using characters
        # This is a simplified version - a full pie would be more complex
        pie_lines = []
        center_y, center_x = radius, radius * 2

        # Create grid
        grid = [[" " for _ in range(radius * 4)] for _ in range(radius * 2)]

        # Draw a simple circle representation
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                # Distance from center
                dy = y - center_y
                dx = x - center_x
                distance = (dx**2 + dy**2) ** 0.5

                if radius - 0.5 <= distance <= radius + 0.5:
                    grid[y][x] = self.chart_chars["pie_full"]

        # Convert grid to strings
        for row in grid:
            pie_lines.append("".join(row))

        lines.extend(pie_lines)
        lines.append("")

        # Add legend
        lines.append(f"{Fore.YELLOW}Legend:{Style.RESET_ALL}")
        for _i, (label, percentage) in enumerate(sorted_items[:8]):  # Show top 8
            display_label = label[:20] + "..." if len(label) > 20 else label
            lines.append(f"  {display_label}: {percentage:.1f}%")

        return "\n".join(lines)

    def _create_horizontal_bar_chart(
        self, data: dict[str, int], title: str = "", max_width: int | None = None
    ) -> str:
        """Create a horizontal ASCII bar chart.

        Args:
            data: Dictionary mapping labels to values
            title: Chart title
            max_width: Maximum width for bars

        Returns:
            str: ASCII horizontal bar chart
        """
        if not data:
            return "No data available for chart"

        if max_width is None:
            max_width = self.width - 25  # Leave space for labels and values

        # Find max value for scaling
        max_value = max(data.values()) if data else 0
        if max_value == 0:
            return "No activity data to display"

        # Sort data
        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)

        lines = []
        if title:
            lines.append(f"{Fore.CYAN}{title}{Style.RESET_ALL}")
            lines.append("")

        for label, value in sorted_data[:10]:  # Show top 10
            # Calculate bar length
            if max_value > 0:
                bar_length = int((value / max_value) * max_width)
            else:
                bar_length = 0

            # Create bar
            bar = self.chart_chars["bar_full"] * bar_length

            # Truncate label if needed
            max_label_len = 20
            display_label = label[:max_label_len] + "..." if len(label) > max_label_len else label

            # Format line with fixed width
            lines.append(f"{display_label:<20} {bar} {value:,}")

        return "\n".join(lines)

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as ASCII charts.

        For single commits, shows file change breakdown and impact visualization.
        """
        lines = [
            f"{Fore.CYAN}Commit Analysis: {stats.hash[:8]}{Style.RESET_ALL}",
            f"Author: {stats.author}",
            f"Date: {self._format_date(stats.date)}",
            "",
        ]

        # File changes bar chart
        if stats.files:
            file_changes = {f.path.split("/")[-1]: f.lines_changed for f in stats.files}
            lines.append(
                self._create_horizontal_bar_chart(file_changes, "File Changes (Lines Modified)")
            )
            lines.append("")

        # Summary statistics
        lines.extend([
            f"{Fore.YELLOW}Summary:{Style.RESET_ALL}",
            f"Files Changed: {stats.files_changed}",
            f"Lines Added: {stats.lines_added:,}",
            f"Lines Deleted: {stats.lines_deleted:,}",
            f"Net Change: {self._format_net_change(stats.lines_added, stats.lines_deleted)}",
        ])

        return "\n".join(lines)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as ASCII charts.

        Shows comprehensive charts for the date range including:
        - Daily activity bar chart
        - Author contribution breakdown
        - Component activity
        - Impact distribution
        """
        # Calculate duration
        duration_days = (stats.end_date.date() - stats.start_date.date()).days
        if duration_days == 0:
            duration_days = 1

        lines = [
            f"{Fore.CYAN}Repository Analysis{Style.RESET_ALL}",
            f"Period: {self._format_date(stats.start_date).split()[0]} to "
            f"{self._format_date(stats.end_date).split()[0]} ({duration_days} days)",
            "",
        ]

        # Daily activity chart
        if hasattr(stats, "commits_by_day") and stats.commits_by_day:
            lines.append(self._create_bar_chart(stats.commits_by_day, "Daily Commit Activity"))
            lines.append("")

        # Author contribution chart
        if stats.authors:
            lines.append(self._create_horizontal_bar_chart(stats.authors, "Author Contributions"))
            lines.append("")

        # Component activity chart
        if hasattr(stats, "component_stats") and stats.component_stats:
            component_commits = {
                comp: data["commits"] for comp, data in stats.component_stats.items()
            }
            lines.append(
                self._create_horizontal_bar_chart(component_commits, "Component Activity (Commits)")
            )
            lines.append("")

        # Impact distribution (if available)
        if hasattr(stats, "author_impact_stats") and stats.author_impact_stats:
            # Aggregate impact across all authors
            total_impact = {"high": 0, "medium": 0, "low": 0}
            for author_stats in stats.author_impact_stats.values():
                for impact_level, count in author_stats.items():
                    total_impact[impact_level] += count

            if sum(total_impact.values()) > 0:
                lines.append(
                    self._create_horizontal_bar_chart(total_impact, "Commit Impact Distribution")
                )
                lines.append("")

        # Summary statistics
        lines.extend([
            f"{Fore.YELLOW}Summary Statistics:{Style.RESET_ALL}",
            f"Total Commits: {stats.total_commits:,}",
            f"Total Files Changed: {stats.total_files_changed:,}",
            f"Total Lines Added: {stats.total_lines_added:,}",
            f"Total Lines Deleted: {stats.total_lines_deleted:,}",
            "Net Change: "
            + self._format_net_change(stats.total_lines_added, stats.total_lines_deleted),
            f"Contributors: {len(stats.authors)}",
        ])

        return "\n".join(lines)
