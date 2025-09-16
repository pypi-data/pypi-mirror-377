"""Standard output formatter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from colorama import Fore, Style

from .base_formatter import BaseFormatter

if TYPE_CHECKING:
    # Only import for typing to avoid runtime import cycles
    from beaconled.core.models import CommitStats, RangeStats


class StandardFormatter(BaseFormatter):
    """Standard text formatter for Beacon delivery analytics output.

    Provides basic formatting of commit and range statistics with color coding.
    """

    def __init__(self, *, no_emoji: bool = False):
        """Initializes the formatter."""
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji or not self._supports_emoji()

        self.EMOJIS = {
            "commit": "📊",
            "author": "👤",
            "date": "📅",
            "message": "💬",
            "files": "📂",
            "added": "+",
            "deleted": "-",
            "net": "🔀",
            "period": "🗓️",
            "commits": "commits",
            "files_changed": "files changed",
            "lines_added": "lines added",
            "lines_deleted": "lines deleted",
            "net_change": "net change",
            "contributors": "👥",
            "breakdown": "🔍",
            "overview": "🚀",
            "activity": "🔥",
        }

    def _supports_emoji(self) -> bool:
        """Check if the environment supports emoji."""
        import sys

        # A simple check for UTF-8 encoding is usually sufficient.
        # Also, handle environments where stdout might be redirected or missing (like in tests).
        encoding = getattr(sys.stdout, "encoding", "")
        if encoding:
            return encoding.lower() == "utf-8"
        return False

    def _get_emoji(self, name: str) -> str:
        """Return emoji if supported, else empty string."""
        return self.EMOJIS.get(name, "") if not self.no_emoji else ""

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics as standard text."""
        net_change_str = self._format_net_change(
            stats.lines_added,
            stats.lines_deleted,
        )
        output = [
            f"{self._get_emoji('commit')} {Fore.CYAN}Commit:{Style.RESET_ALL} {stats.hash[:8]}",
            f"{self._get_emoji('author')} {Fore.CYAN}Author:{Style.RESET_ALL} {stats.author}",
            (
                f"{self._get_emoji('date')} {Fore.CYAN}Date:{Style.RESET_ALL} "
                f"{self._format_date(stats.date)}"
            ),
            f"{self._get_emoji('message')} {Fore.CYAN}Message:{Style.RESET_ALL} {stats.message}",
            "",
            (
                f"{self._get_emoji('files')} {Fore.YELLOW}Files changed:{Style.RESET_ALL} "
                f"{stats.files_changed:,}"
            ),
            (
                f"{self._get_emoji('added')} {Fore.GREEN}Lines added:{Style.RESET_ALL} "
                f"{stats.lines_added:,}"
            ),
            (
                f"{self._get_emoji('deleted')} {Fore.RED}Lines deleted:{Style.RESET_ALL} "
                f"{stats.lines_deleted:,}"
            ),
            f"{self._get_emoji('net')} {Fore.YELLOW}Net change:{Style.RESET_ALL} {net_change_str}",
        ]

        if stats.files:
            output.extend(
                [
                    "",
                    f"{Fore.MAGENTA}File changes:{Style.RESET_ALL}",
                    *[self._format_file_stats(f) for f in stats.files],
                ],
            )

        return "\n".join(output)

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics as enhanced standard text."""
        # Calculate duration in days - for relative dates, use actual span
        # to match user expectations (e.g., --since 9d should show "9 days")
        duration_days = (stats.end_date.date() - stats.start_date.date()).days
        if duration_days == 0:  # Same day
            duration_days = 1

        # Enhanced header
        output = [
            f"{self._get_emoji('period')} {Fore.CYAN}Analysis Period:{Style.RESET_ALL} "
            f"{self._format_date(stats.start_date).split()[0]} to "
            f"{self._format_date(stats.end_date).split()[0]} ({duration_days} days)",
            "",
            # Total statistics with comma formatting
            f"{self._get_emoji('commits')} Total commits: {stats.total_commits:,}",
            (
                f"{self._get_emoji('files_changed')} Total files changed: "
                f"{stats.total_files_changed:,}"
            ),
            (f"{self._get_emoji('lines_added')} Total lines added: {stats.total_lines_added:,}"),
            (
                f"{self._get_emoji('lines_deleted')} Total lines deleted: "
                f"{stats.total_lines_deleted:,}"
            ),
            f"{self._get_emoji('net_change')} Net change: "
            + self._format_net_change(stats.total_lines_added, stats.total_lines_deleted),
        ]

        # Team Overview Section
        if stats.authors:
            active_days = len(getattr(stats, "commits_by_day", {}))
            avg_commits_per_day = round(stats.total_commits / max(duration_days, 1), 1)

            output.extend([
                "",
                (
                    f"{self._get_emoji('overview')} {Fore.YELLOW}"
                    f"=== TEAM OVERVIEW ==={Style.RESET_ALL}"
                ),
                f"{self._get_emoji('contributors')} Total Contributors: {len(stats.authors)}",
                f"Total Commits: {stats.total_commits}",
                f"Average Commits/Day: {avg_commits_per_day}",
                f"Active Days: {active_days}/{duration_days}",
            ])

        # Contributor Breakdown Section
        if stats.authors and hasattr(stats, "author_impact_stats"):
            output.extend([
                "",
                (
                    f"{self._get_emoji('breakdown')} {Fore.YELLOW}"
                    f"=== CONTRIBUTOR BREAKDOWN ==={Style.RESET_ALL}"
                ),
            ])

            # Sort authors by commit count and take top 3
            top_contributors = sorted(stats.authors.items(), key=lambda x: x[1], reverse=True)[:3]

            for author, commit_count in top_contributors:
                percentage = round((commit_count / stats.total_commits) * 100)
                output.append(f"{author}: {commit_count} commits ({percentage}%)")

                # Add impact breakdown
                if author in stats.author_impact_stats:
                    impact_stats = stats.author_impact_stats[author]
                    output.extend([
                        f"  - High Impact: {impact_stats.get('high', 0)} commits",
                        f"  - Medium Impact: {impact_stats.get('medium', 0)} commits",
                        f"  - Low Impact: {impact_stats.get('low', 0)} commits",
                    ])

                # Add most active days
                if (
                    hasattr(stats, "author_activity_by_day")
                    and author in stats.author_activity_by_day
                ):
                    day_activity = stats.author_activity_by_day[author]
                    if day_activity:
                        # Get top 2 most active days
                        top_days = sorted(day_activity.items(), key=lambda x: x[1], reverse=True)[
                            :2
                        ]
                        most_active = ", ".join([day for day, _ in top_days])
                        output.append(f"  - Most Active: {most_active}")

                output.append("")  # Empty line between contributors

        # Component Activity Section
        if hasattr(stats, "component_stats") and stats.component_stats:
            output.extend([
                (
                    f"{self._get_emoji('activity')} {Fore.YELLOW}"
                    f"=== COMPONENT ACTIVITY ==={Style.RESET_ALL}"
                ),
                "Most Changed Components:",
            ])

            # Sort components by commits, then by lines
            sorted_components = sorted(
                stats.component_stats.items(),
                key=lambda x: (x[1]["commits"], x[1]["lines"]),
                reverse=True,
            )[:5]  # Top 5 components

            for component, component_stats in sorted_components:
                commits = component_stats["commits"]
                lines = component_stats["lines"]
                output.append(f"  {component} {commits} commits, {lines:,} lines")

        return "\n".join(output)
