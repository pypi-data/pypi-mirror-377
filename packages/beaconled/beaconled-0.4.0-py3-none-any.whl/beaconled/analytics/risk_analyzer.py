"""Risk analysis for the extended format.

This module provides the RiskAnalyzer class that analyzes potential risks in the codebase,
including code hotspots, stale code, and security vulnerabilities.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from beaconled.core.models import RangeStats


@dataclass
class RiskConfig:
    """Configuration for the RiskAnalyzer.

    Attributes:
        hotspot_threshold: Number of changes after which a file is considered a hotspot
        stale_threshold_days: Number of days after which unchanged code is considered stale
        security_risk_keywords: List of keywords that might indicate security risks
    """

    hotspot_threshold: int = 5  # Number of changes to consider a file a hotspot
    stale_threshold_days: int = 90  # Days after which code is considered stale
    security_risk_keywords: tuple[str, ...] = (
        "password",
        "secret",
        "key",
        "token",
        "credential",
        "auth",
        "private_key",
        "api_key",
        "pwd",
    )


class RiskAnalyzer:
    """Analyzes potential risks in the codebase based on commit history."""

    def __init__(self, config: RiskConfig | None = None) -> None:
        """Initialize the risk analyzer with optional configuration."""
        self.config = config or RiskConfig()

    def analyze(self, range_stats: RangeStats) -> dict[str, float | list[str] | dict[str, Any]]:
        """Analyze potential risks from the given range statistics.

        Args:
            range_stats: The range statistics to analyze

        Returns:
            Dictionary containing risk metrics:
            {
                'risk_score': float,  # Overall risk score (0-10)
                'hotspots': List[str],  # Files with high churn
                'stale_code': int,  # Number of stale files
                'security_concerns': List[str],  # Potential security issues
                'details': {  # Detailed risk breakdown
                    'hotspot_risk': float,
                    'stale_code_risk': float,
                    'security_risk': float
                }
            }
        """
        # Initialize result with default values
        result: dict[str, Any] = {
            "risk_score": 0.0,
            "hotspots": [],
            "stale_code": 0,
            "security_concerns": [],
            "details": {"hotspot_risk": 0.0, "stale_code_risk": 0.0, "security_risk": 0.0},
        }

        if not range_stats.commits:
            return result

        # Analyze different types of risks
        hotspot_risk, hotspots = self._analyze_hotspots(range_stats)
        stale_code_risk, stale_count = self._analyze_stale_code(range_stats)
        security_risk, security_concerns = self._analyze_security_risks(range_stats)

        # Calculate overall risk score (weighted average)
        risk_score = (
            hotspot_risk * 0.4  # 40% weight to hotspots
            + stale_code_risk * 0.3  # 30% to stale code
            + security_risk * 0.3  # 30% to security concerns
        )

        # Update result
        result.update({
            "risk_score": round(risk_score, 1),
            "hotspots": hotspots,
            "stale_code": stale_count,
            "security_concerns": security_concerns,
            "details": {
                "hotspot_risk": round(hotspot_risk, 1),
                "stale_code_risk": round(stale_code_risk, 1),
                "security_risk": round(security_risk, 1),
            },
        })

        return result

    def _analyze_hotspots(self, range_stats: RangeStats) -> tuple[float, list[str]]:
        """Analyze code hotspots (frequently changed files)."""
        if not range_stats.commits:
            return 0.0, []

        # Count changes per file
        file_changes: dict[str, int] = {}
        for commit in range_stats.commits:
            for file_stat in commit.files:
                file_changes[file_stat.path] = file_changes.get(file_stat.path, 0) + 1

        # Identify hotspots (files changed more than threshold)
        hotspots = [
            path for path, count in file_changes.items() if count >= self.config.hotspot_threshold
        ]

        # Calculate hotspot risk (0-10 scale)
        max_changes = max(file_changes.values()) if file_changes else 0
        hotspot_risk = min(10.0, (max_changes / self.config.hotspot_threshold) * 2)

        return hotspot_risk, sorted(hotspots)

    def _analyze_stale_code(self, range_stats: RangeStats) -> tuple[float, int]:
        """Analyze stale code (unchanged for a long time)."""
        if not range_stats.commits:
            return 0.0, 0

        # Find the most recent commit date for each file
        file_last_modified: dict[str, datetime] = {}
        for commit in range_stats.commits:
            for file_stat in commit.files:
                # Keep the most recent commit date for each file
                if (
                    file_stat.path not in file_last_modified
                    or commit.date > file_last_modified[file_stat.path]
                ):
                    file_last_modified[file_stat.path] = commit.date

        # Count stale files (not modified in the last threshold days)
        threshold_date = datetime.now(timezone.utc) - timedelta(
            days=self.config.stale_threshold_days
        )
        stale_count = sum(
            1 for last_modified in file_last_modified.values() if last_modified < threshold_date
        )

        # Calculate stale code risk (0-10 scale)
        total_files = len(file_last_modified)
        if total_files == 0:
            return 0.0, 0

        stale_ratio = stale_count / total_files
        stale_risk = min(10.0, stale_ratio * 20)  # 50% stale = 10 risk score

        return stale_risk, stale_count

    def _analyze_security_risks(self, range_stats: RangeStats) -> tuple[float, list[str]]:
        """Analyze potential security risks in the codebase."""
        if not range_stats.commits:
            return 0.0, []

        security_concerns = set()

        # Check for security-related keywords in commit messages and file paths
        for commit in range_stats.commits:
            # Check commit message
            if any(
                keyword in commit.message.lower() for keyword in self.config.security_risk_keywords
            ):
                msg = f"Security-related keyword in commit: {commit.hash[:8]}"
                msg += f" - {commit.message[:50]}..."
                security_concerns.add(msg)

            # Check file paths
            for file_stat in commit.files:
                if any(
                    keyword in file_stat.path.lower()
                    for keyword in self.config.security_risk_keywords
                ):
                    security_concerns.add(
                        f"Security-related keyword in file path: {file_stat.path}"
                    )

        # Calculate security risk (0-10 scale)
        security_risk = min(10.0, len(security_concerns) * 2)  # 5+ concerns = max risk

        return security_risk, sorted(security_concerns)
