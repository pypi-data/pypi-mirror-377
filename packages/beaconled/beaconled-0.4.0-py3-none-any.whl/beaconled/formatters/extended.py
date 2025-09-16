"""Extended output formatter with additional analytics."""

from collections import defaultdict
from collections.abc import Callable
from datetime import datetime

import git
from colorama import Fore, Style

from beaconled.analytics.engine import AnalyticsEngine
from beaconled.core.models import CommitStats, RangeStats
from beaconled.formatters.base_formatter import BaseFormatter


class ExtendedFormatter(BaseFormatter):
    """Extended text formatter with additional analytics.

    Extends the base formatter with additional statistics including:
    - File type breakdown
    - Author contribution details
    - Daily activity patterns
    - Time-based analytics
    - Team collaboration analysis
    - Code quality insights
    - Risk assessment
    - File lifecycle tracking
    """

    def __init__(self, *, no_emoji: bool | None = None, repo_path: str = ".") -> None:
        """Initialize the formatter.

        Args:
            no_emoji: Whether to disable emoji output
            repo_path: Path to the git repository
        """
        super().__init__()
        # Disable emojis in environments that don't support them
        self.no_emoji = no_emoji if no_emoji is not None else not self._supports_emoji()
        self.analytics_engine = AnalyticsEngine()
        self.repo_path = repo_path

        self.EMOJIS = {
            "commit": "📊",
            "author": "👤",
            "contributors": "👥",
            "date": "📅",
            "message": "💬",
            "files": "📂",
            "added": "📈",
            "deleted": "📉",
            "net": "🔀",
            "range": "📊",
        }

    def _get_emoji(self, emoji_name: str) -> str:
        """Get emoji if enabled, otherwise return empty string."""
        if self.no_emoji:
            return ""
        return self.EMOJIS.get(emoji_name, "")

    def _get_file_lifecycle_stats(self, since: str, until: str | None = None) -> dict[str, int]:
        """Get file lifecycle statistics for the given date range.

        Args:
            since: Start date in ISO format (YYYY-MM-DD)
            until: End date in ISO format (YYYY-MM-DD), defaults to now

        Returns:
            Dictionary with counts of added, modified, deleted, and renamed files
        """
        import git

        try:
            repo = git.Repo(self.repo_path)

            # Format date range for git log
            date_args = ["--since", since]
            if until:
                date_args.extend(["--until", until])

            # Get git log with name status
            log_output = repo.git.log("--name-status", "--pretty=format:", *date_args)

            return self._parse_git_log_output(log_output)

        except Exception as e:
            # Log error and return empty stats
            import logging

            logging.error("Error getting file lifecycle stats: %s", str(e))
            return {"added": 0, "modified": 0, "deleted": 0, "renamed": 0}

    def _parse_git_log_output(self, log_output: str) -> dict[str, int]:
        """Parse git log output and count file statuses.

        Args:
            log_output: Raw output from 'git log --name-status'

        Returns:
            Dictionary with counts of each file status
        """
        # Use sets to track unique files for each status
        added = set()
        modified = set()
        deleted = set()
        renamed = set()

        for raw_line in log_output.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            # Split the line into parts
            parts = line.split("\t")
            if not parts:
                continue

            # First character indicates status
            status = parts[0][0].upper()

            # Get the file path
            if status == "R" and len(parts) >= 3:
                # For renames, the format is: R100\told_path\tnew_path
                file_path = parts[2]  # Use the new path for renames
                renamed.add(file_path)
            elif len(parts) >= 2:
                file_path = parts[1]
                if status == "A":
                    added.add(file_path)
                elif status == "M":
                    modified.add(file_path)
                elif status == "D":
                    deleted.add(file_path)

        # Return counts of unique files for each status
        return {
            "added": len(added),
            "modified": len(modified),
            "deleted": len(deleted),
            "renamed": len(renamed),
        }

    def _format_author_breakdown(self, stats: RangeStats) -> list[str]:
        """Format author contribution breakdown.

        Args:
            stats: RangeStats object with author information

        Returns:
            List of formatted strings with author contributions
        """
        if not hasattr(stats, "authors") or not stats.authors:
            return []

        emoji = self._get_emoji
        lines = [f"{emoji('contributors')} Contributors:"]

        # Sort authors by commit count (descending)
        sorted_authors = sorted(
            stats.authors.items(),
            key=lambda x: x[1],  # x[1] is the commit count (int)
            reverse=True,
        )

        for author, commit_count in sorted_authors:
            lines.append(f"• {author}: {commit_count} commit{'s' if commit_count != 1 else ''}")

        return lines

    def _format_temporal_analysis(self, stats: RangeStats) -> list[str]:
        """Format temporal analysis of commits.

        Args:
            stats: RangeStats object with temporal analysis data

        Returns:
            List of formatted strings with temporal analysis
        """
        if not hasattr(stats, "commits_by_day") or not stats.commits_by_day:
            return []

        emoji = self._get_emoji
        lines = [f"{emoji('date')} Temporal Analysis - Daily Activity Timeline:"]

        # Sort dates chronologically
        sorted_dates = sorted(stats.commits_by_day.items(), key=lambda x: x[0])

        for date, count in sorted_dates:
            lines.append(f"  {date}: {count} commit{'s' if count != 1 else ''}")

        return lines

    def _get_largest_file_changes(
        self, commits: list[CommitStats], top_n: int = 5
    ) -> list[tuple[str, int]]:
        """Calculate the largest file changes by summing additions + deletions per file.

        Args:
            commits: List of CommitStats objects to analyze
            top_n: Number of top changes to return (default: 5)

        Returns:
            List of tuples (file_path, total_changes) sorted by total_changes in descending order
        """
        file_changes: dict[str, int] = {}

        for commit in commits:
            if not hasattr(commit, "files") or not commit.files:
                continue

            for file_stat in commit.files:
                file_path = file_stat.path
                changes = file_stat.lines_added + file_stat.lines_deleted

                if file_path in file_changes:
                    file_changes[file_path] += changes
                else:
                    file_changes[file_path] = changes

        # Sort files by total changes in descending order
        sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)

        return sorted_files[:top_n]

    def format_range_stats(self, stats: RangeStats) -> str:  # noqa: C901
        """Format range statistics with extended information.

        Args:
            stats: RangeStats object containing commit range information

        Returns:
            Formatted string with range statistics
        """
        emoji = self._get_emoji
        date_range = (
            f"{emoji('range')} Commit Range: "
            f"{self._format_date_range(stats.start_date)} to "
            f"{self._format_date_range(stats.end_date)}"
        )
        commit_count = stats.total_commits if hasattr(stats, "total_commits") else 0
        # Get total files changed from the stats object if available, otherwise count from commits
        if hasattr(stats, "total_files_changed"):
            total_files = stats.total_files_changed
        else:
            total_files = sum(
                getattr(
                    commit,
                    "files_changed",
                    len(commit.files) if hasattr(commit, "files") else 0,
                )
                for commit in getattr(stats, "commits", [])
            )
        # Get total lines added and deleted from stats if available, otherwise calculate
        if hasattr(stats, "total_lines_added"):
            total_added = stats.total_lines_added
        else:
            total_added = sum(
                f.lines_added
                for commit in getattr(stats, "commits", [])
                for f in getattr(commit, "files", [])
            )
        if hasattr(stats, "total_lines_deleted"):
            total_deleted = stats.total_lines_deleted
        else:
            total_deleted = sum(
                f.lines_deleted
                for commit in getattr(stats, "commits", [])
                for f in getattr(commit, "files", [])
            )
        net_change = total_added - total_deleted
        lines = [
            date_range,
            "",
            f"{emoji('bar_chart')} Range Analysis:",
            f"Total commits: {commit_count}",
            f"Total files changed: {total_files}",
            f"{emoji('added')} Total lines added: {total_added}",
            f"{emoji('deleted')} Total lines deleted: {total_deleted}",
            f"{emoji('net')} Net change: {net_change}",
            "",
        ]

        # Add file lifecycle stats if date range is available
        if hasattr(stats, "start_date") and hasattr(stats, "end_date"):
            since = stats.start_date.strftime("%Y-%m-%d")
            until = stats.end_date.strftime("%Y-%m-%d")
            lifecycle_stats = self._get_file_lifecycle_stats(since, until)
            if lifecycle_stats and any(lifecycle_stats.values()):
                lines.extend(["", *self._format_file_lifecycle(lifecycle_stats)])

        # Add author breakdown if available
        if hasattr(stats, "authors") and stats.authors:
            lines.extend(["", *self._format_author_breakdown(stats)])

        # Add temporal analysis if available
        if hasattr(stats, "commits_by_day") and stats.commits_by_day:
            lines.extend(["", *self._format_temporal_analysis(stats)])

        # Add largest file changes section if there are commits
        if hasattr(stats, "commits") and stats.commits:
            largest_changes = self._format_largest_file_changes_section(stats)
            if largest_changes:
                lines.extend(["", *largest_changes])

        # Add file type breakdown if available
        if hasattr(stats, "file_types") and stats.file_types:
            lines.extend(["", *self._format_file_types(stats.file_types)])

        # Add enhanced analytics if available
        lines.extend(self._format_enhanced_analytics(stats, emoji))

        return "\n".join(lines)

    def _format_enhanced_analytics(  # noqa: C901
        self, stats: RangeStats, emoji_func: Callable[[str], str]
    ) -> list[str]:
        """Format enhanced analytics section.

        Args:
            stats: RangeStats object containing statistics
            emoji_func: Emoji function to use for formatting

        Returns:
            List of formatted strings with enhanced analytics
        """
        lines = []

        # Add enhanced analytics if available
        if hasattr(stats, "time") and stats.time:
            time_analytics = stats.time
            if hasattr(time_analytics, "velocity_trends") and time_analytics.velocity_trends:
                velocity = time_analytics.velocity_trends
                if hasattr(velocity, "weekly_average") and velocity.weekly_average:
                    lines.extend([
                        "",
                        f"{emoji_func('added')} Velocity: "
                        f"{velocity.weekly_average:.1f} commits/week",
                    ])
        else:
            # Try to get enhanced analytics from the analytics engine if not already present
            try:
                # Get analytics data using the range_stats object directly
                analytics_data = self.analytics_engine.analyze(stats)

                # Add velocity information if available
                if analytics_data.get("time"):
                    time_analytics = analytics_data["time"]
                    if (
                        hasattr(time_analytics, "velocity_trends")
                        and time_analytics.velocity_trends
                    ):
                        velocity = time_analytics.velocity_trends
                        if hasattr(velocity, "weekly_average") and velocity.weekly_average:
                            lines.extend([
                                "",
                                f"{emoji_func('added')} Velocity: "
                                f"{velocity.weekly_average:.1f} commits/week",
                            ])

                # Add collaboration information if available
                if analytics_data.get("collaboration"):
                    collaboration = analytics_data["collaboration"]
                    if (
                        hasattr(collaboration, "collaboration_patterns")
                        and collaboration.collaboration_patterns
                    ):
                        patterns = collaboration.collaboration_patterns
                        if hasattr(patterns, "team_connectivity") and patterns.team_connectivity:
                            connectivity = patterns.team_connectivity * 100  # Convert to percentage
                            lines.extend([
                                f"{emoji_func('contributors')} Team connectivity: "
                                f"{connectivity:.1f}%"
                            ])
                        if hasattr(patterns, "knowledge_risk") and patterns.knowledge_risk:
                            lines.extend([
                                f"{emoji_func('warning')} Knowledge risk: {patterns.knowledge_risk}"
                            ])

                # Add quality information if available
                if analytics_data.get("quality"):
                    quality = analytics_data["quality"]
                    if hasattr(quality, "maintainability_index") and quality.maintainability_index:
                        lines.extend([
                            f"{emoji_func('net')} Maintainability: "
                            f"{quality.maintainability_index:.1f}"
                        ])
                    if hasattr(quality, "test_coverage") and quality.test_coverage:
                        coverage = quality.test_coverage
                        lines.extend([f"{emoji_func('added')} Test coverage: {coverage:.1f}%"])

                # Add risk information if available
                if analytics_data.get("risk"):
                    risk = analytics_data["risk"]
                    if hasattr(risk, "risk_score") and risk.risk_score:
                        lines.extend([
                            f"{emoji_func('warning')} Overall risk: {risk.risk_score:.1f}/10"
                        ])
            except Exception:
                # Gracefully handle any analytics errors
                pass

        return lines

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics with emoji support.

        Args:
            stats: CommitStats object containing commit information

        Returns:
            Formatted string with commit statistics
        """
        emoji = self._get_emoji

        # Format commit header
        lines = [
            f"{emoji('commit')} Commit: {stats.hash}",
            f"{emoji('author')} Author: {stats.author}",
            f"{emoji('date')} Date:   {self._format_date(stats.date)}",
            f"{emoji('message')} Message: {stats.message}",
            "",
        ]

        # Add file changes
        lines.append(f"{emoji('files')} Files changed: {len(stats.files) if stats.files else 0}")

        if stats.files:
            for file_stat in stats.files:
                lines.append(self._format_file_stats(file_stat))

        # Add file type breakdown (always shown, even for empty commits)
        file_types = {}
        if stats.files:
            for file_stat in stats.files:
                ext = file_stat.path.split(".")[-1] if "." in file_stat.path else "other"
                if ext not in file_types:
                    file_types[ext] = {"count": 0, "added": 0, "deleted": 0}
                file_types[ext]["count"] += 1
                file_types[ext]["added"] += file_stat.lines_added
                file_types[ext]["deleted"] += file_stat.lines_deleted

        lines.append("\nFile type breakdown:")
        if file_types:
            for ext, data in sorted(file_types.items()):
                lines.append(
                    f"  {ext}: {data['count']} file{'s' if data['count'] != 1 else ''}, "
                    f"+{data['added']}/-{data['deleted']}"
                )
        else:
            lines.append("  No files changed")

        # Add summary
        total_added = sum(f.lines_added for f in stats.files) if stats.files else 0
        total_deleted = sum(f.lines_deleted for f in stats.files) if stats.files else 0
        net_change = total_added - total_deleted

        lines.extend([
            "",
            f"{emoji('added')} Lines added: {Fore.GREEN}+{total_added:,}{Style.RESET_ALL}",
            f"{emoji('deleted')} Lines deleted: {Fore.RED}-{total_deleted:,}{Style.RESET_ALL}",
            f"{emoji('net')} Net change: "
            f"{Fore.GREEN if net_change >= 0 else Fore.RED}{net_change:+,}{Style.RESET_ALL}",
        ])

        return "\n".join(lines)

    def _format_largest_file_changes_section(self, stats: RangeStats) -> list[str]:
        """Format the largest file changes section.

        Args:
            stats: RangeStats object containing commit information

        Returns:
            List of formatted strings with largest file changes
        """
        if not hasattr(stats, "commits") or not stats.commits:
            return []

        largest_changes = self._get_largest_file_changes(stats.commits)
        if not largest_changes:
            return []

        emoji = self._get_emoji
        lines = [
            "",
            f"{emoji('files')} {Fore.MAGENTA}Largest File Changes:{Style.RESET_ALL}",
        ]

        for file_path, changes in largest_changes:
            lines.append(f"  {file_path}: {changes} lines changed")

        return lines

    def _get_frequently_changed_files(self, since: str) -> dict[str, int]:
        """Get files ordered by change frequency within the analysis period.

        Args:
            since: Start of the analysis period in ISO format (e.g., "2025-01-01")

        Returns:
            Dictionary mapping file paths to change frequency, sorted by frequency (descending)
            and limited to the top 5 most frequently changed files.
        """
        file_changes: defaultdict[str, int] = defaultdict(int)

        try:
            # Use GitPython to get file change counts
            repo = git.Repo()

            # Get commits since the specified time
            commits = list(repo.iter_commits(since=since))

            # Count file changes across all commits
            for commit in commits:
                # Get the files changed in this commit
                for file_obj in commit.stats.files:
                    file_path = str(file_obj)
                    file_changes[file_path] += 1

            # Sort by frequency (descending) and return top 5
            sorted_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)
            return dict(sorted_files[:5])

        except Exception:
            # Handle any errors gracefully
            # Log the error instead of printing
            return {}

    def _format_file_lifecycle(self, stats: dict[str, int] | None) -> list[str]:
        """Format file lifecycle statistics for display.

        Args:
            stats: Dictionary with file lifecycle statistics

        Returns:
            List of formatted strings with header and stats, or empty list if all counts are zero
        """
        if not stats:
            return []

        # Check if all counts are zero
        if all(v == 0 for v in stats.values()):
            return []

        emoji = self._get_emoji
        output = [
            f"{emoji('activity')} {Fore.MAGENTA}File Lifecycle Activity:{Style.RESET_ALL}",
            f"• Files Added: {stats.get('added', 0)} new files",
            f"• Files Modified: {stats.get('modified', 0)} files changed",
            f"• Files Deleted: {stats.get('deleted', 0)} files removed",
            f"• Files Renamed: {stats.get('renamed', 0)} files moved",
        ]

        return output

    def _format_frequent_files(self, frequent_files: dict[str, int]) -> list[str]:
        """Format frequently changed files section.

        Args:
            frequent_files: Dictionary mapping file paths to change frequency

        Returns:
            List of formatted strings for the output
        """
        if not frequent_files:
            return []

        output = [
            "",
            f"{self._get_emoji('fire')} {Fore.MAGENTA}Most Frequently Changed "
            f"(last 30 days):{Style.RESET_ALL}",
        ]

        # Sort by frequency (descending) and take top 5
        for file_path, changes in sorted(frequent_files.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            output.append(f"  • {file_path}: {changes} changes")

        return output

    def _format_date_range(self, dt: datetime) -> str:
        """Format a datetime object for use in date ranges (date only)."""
        return dt.strftime("%Y-%m-%d")

    def _format_file_types(self, file_types: dict[str, dict[str, int]]) -> list[str]:
        """Format file type breakdown.

        Args:
            file_types: Dictionary mapping file extensions to stats

        Returns:
            List of formatted strings with file type breakdown
        """
        if not file_types:
            return []

        lines = ["File type breakdown:"]
        for ext, data in sorted(file_types.items()):
            # Handle both old and new key formats
            files_changed = data.get("files_changed", data.get("count", 0))
            lines_added = data.get("lines_added", data.get("added", 0))
            lines_deleted = data.get("lines_deleted", data.get("deleted", 0))
            lines.append(f"  {ext}: {files_changed} files, +{lines_added}/-{lines_deleted}")
        return lines

    def _get_author_contribution_stats(
        self, authors: dict[str, int], total_commits: int
    ) -> list[str]:
        """Get formatted author contribution statistics.

        Args:
            authors: Dictionary mapping author names to commit counts
            total_commits: Total number of commits

        Returns:
            List of formatted strings with author contributions and percentages
        """
        lines = []
        for author, commit_count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
            percentage = (commit_count / max(total_commits, 1)) * 100
            lines.append(f"  {author}: {commit_count} commits ({percentage:.1f}%)")
        return lines

    def _get_daily_activity_stats(self, commits: list[CommitStats]) -> list[str]:
        """Get formatted daily activity statistics.

        Args:
            commits: List of CommitStats objects

        Returns:
            List of formatted strings with daily activity
        """
        from collections import defaultdict

        daily_activity: defaultdict[str, int] = defaultdict(int)
        for commit in commits:
            if hasattr(commit, "date") and commit.date:
                date_key = commit.date.strftime("%Y-%m-%d")
                daily_activity[date_key] += 1

        lines = []
        for date, count in sorted(daily_activity.items()):
            lines.append(f"  {date}: {count} commits")
        return lines
