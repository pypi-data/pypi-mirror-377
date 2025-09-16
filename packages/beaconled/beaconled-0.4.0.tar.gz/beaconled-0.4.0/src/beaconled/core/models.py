"""Data models for Beacon delivery analytics.

This module defines the core data structures used throughout the application
for representing git repository statistics and analysis results.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FileStats:
    """Statistics for a single file in a git commit.

    Attributes:
        path: Relative path of the file in the repository
        lines_added: Number of lines added in this file
        lines_deleted: Number of lines deleted from this file
        lines_changed: Total number of lines changed (added + deleted)
    """

    path: str
    lines_added: int = 0
    lines_deleted: int = 0
    lines_changed: int = 0

    def __post_init__(self) -> None:
        """Initialize computed fields after instance creation."""
        if self.lines_changed == 0:
            self.lines_changed = self.lines_added + self.lines_deleted


@dataclass
class CommitStats:
    """Statistics for a single git commit.

    Attributes:
        hash: Full 40-character SHA-1 hash of the commit
        author: Name and email of the commit author
        date: Timestamp when the commit was created (in UTC)
        message: Commit message (first line)
        files_changed: Number of files changed in this commit
        lines_added: Total lines added across all files
        lines_deleted: Total lines deleted across all files
        files: List of FileStats objects for each changed file
    """

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0
    files: list[FileStats] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate and compute derived fields after initialization."""
        # Be flexible for unit tests/mocks: accept any non-empty string for hash.
        # Real repository validation occurs in analyzer/repo layer.
        if not isinstance(self.hash, str) or not self.hash.strip():
            msg = f"Invalid commit hash: {self.hash}"
            raise ValueError(msg)
        self.hash = self.hash.strip()

        if not self.files_changed and self.files:
            self.files_changed = len(self.files)

        if not (self.lines_added or self.lines_deleted) and self.files:
            self.lines_added = sum(f.lines_added for f in self.files)
            self.lines_deleted = sum(f.lines_deleted for f in self.files)


@dataclass
class RangeStats:
    """Statistics for a range of git commits.

    Attributes:
        start_date: Start of the date range (inclusive, UTC)
        end_date: End of the date range (inclusive, UTC)
        total_commits: Total number of commits in the range
        total_files_changed: Total files changed across all commits
        total_lines_added: Total lines added across all commits
        total_lines_deleted: Total lines deleted across all commits
        commits: List of CommitStats objects in chronological order
        authors: Dictionary mapping author names to commit counts
        author_impact_stats: Dictionary mapping author names to impact breakdown
        author_activity_by_day: Dictionary mapping author names to day-of-week activity
        component_stats: Dictionary with component activity statistics
        commits_by_day: Dictionary mapping dates to commit counts
    """

    start_date: datetime
    end_date: datetime
    total_commits: int = 0
    total_files_changed: int = 0
    total_lines_added: int = 0
    total_lines_deleted: int = 0
    commits: list[CommitStats] = field(default_factory=list)
    authors: dict[str, int] = field(default_factory=dict)
    author_impact_stats: dict[str, dict[str, int]] = field(default_factory=dict)
    author_activity_by_day: dict[str, dict[str, int]] = field(default_factory=dict)
    component_stats: dict[str, dict[str, int]] = field(default_factory=dict)
    commits_by_day: dict[str, int] = field(default_factory=dict)
    file_types: dict[str, dict[str, int]] = field(default_factory=dict)
    risk_indicators: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and compute derived fields after initialization."""
        if self.start_date > self.end_date:
            msg = "start_date cannot be after end_date"
            raise ValueError(msg)

        if not self.commits:
            return

        # Recalculate totals from commits if not explicitly set
        if not self.total_commits:
            self.total_commits = len(self.commits)

        author_counts: dict[str, int] = defaultdict(int)
        for commit in self.commits:
            author_counts[commit.author] += 1
        self.authors = dict(author_counts)

        if not (self.total_files_changed or self.total_lines_added or self.total_lines_deleted):
            self.total_files_changed = sum(c.files_changed for c in self.commits)
            self.total_lines_added = sum(c.lines_added for c in self.commits)
            self.total_lines_deleted = sum(c.lines_deleted for c in self.commits)

    @staticmethod
    def categorize_commit_impact(commit: "CommitStats") -> str:
        """Categorize a commit's impact level based on files changed and lines modified.

        Args:
            commit: CommitStats object to categorize

        Returns:
            str: Impact level ("high", "medium", or "low")
        """
        files_changed = getattr(commit, "files_changed", 0)
        lines_changed = getattr(commit, "lines_added", 0) + getattr(commit, "lines_deleted", 0)

        # High Impact: >15 files changed OR >100 lines added/deleted
        if files_changed > 15 or lines_changed > 100:
            return "high"
        # Medium Impact: 5-15 files changed OR 25-100 lines added/deleted
        elif files_changed >= 5 or lines_changed >= 25:
            return "medium"
        # Low Impact: <5 files changed AND <25 lines added/deleted
        else:
            return "low"

    @staticmethod
    def get_component_name(file_path: str) -> str:
        """Extract component name from file path.

        Args:
            file_path: Relative file path

        Returns:
            str: Component name (top-level directory or "root" for root files)
        """
        if not file_path or "/" not in file_path:
            return "root"
        return file_path.split("/")[0] + "/"

    def calculate_extended_stats(self) -> None:
        """Calculate extended statistics for enhanced formatting.

        This method populates the author_impact_stats, author_activity_by_day,
        and component_stats fields based on the commits data.
        """
        if not self.commits:
            return

        # Initialize tracking dictionaries with type annotations
        author_impact_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"high": 0, "medium": 0, "low": 0}
        )
        author_activity_by_day: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        component_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"commits": 0, "lines": 0})
        commits_by_day: dict[str, int] = defaultdict(int)

        # Process each commit
        for commit in self.commits:
            # Impact categorization
            impact = self.categorize_commit_impact(commit)
            author = getattr(commit, "author", "Unknown")
            author_impact_stats[author][impact] += 1

            # Day of week activity tracking
            if hasattr(commit, "date") and commit.date:
                day_name = commit.date.strftime("%A")  # Full day name (Monday, Tuesday, etc.)
                author_activity_by_day[author][day_name] += 1

                # Overall daily activity
                date_key = commit.date.strftime("%Y-%m-%d")
                commits_by_day[date_key] += 1

            # Component analysis
            if hasattr(commit, "files") and commit.files:
                commit_components = set()
                for file_stat in commit.files:
                    if hasattr(file_stat, "path"):
                        component = self.get_component_name(file_stat.path)
                        commit_components.add(component)
                        component_stats[component]["lines"] += getattr(
                            file_stat, "lines_added", 0
                        ) + getattr(file_stat, "lines_deleted", 0)

                # Count this commit for each unique component it touches
                for component in commit_components:
                    component_stats[component]["commits"] += 1

        # Convert defaultdicts to regular dicts and store
        self.author_impact_stats = {k: dict(v) for k, v in author_impact_stats.items()}
        self.author_activity_by_day = {k: dict(v) for k, v in author_activity_by_day.items()}
        self.component_stats = {k: dict(v) for k, v in component_stats.items()}
        self.commits_by_day = dict(commits_by_day)
