"""Team collaboration analytics for commit data.

This module provides comprehensive analysis of team collaboration patterns,
including co-authorship metrics, knowledge distribution, and review effectiveness.
"""

from collections import defaultdict
from dataclasses import dataclass

from beaconled.core.models import RangeStats

from .models import (
    CoAuthorshipMetrics,
    CollaborationMetrics,
    CollaborationPatterns,
    KnowledgeDistribution,
    ReviewMetrics,
)


@dataclass
class CollaborationConfig:
    """Configuration for CollaborationAnalyzer.

    Attributes:
        min_collaboration_threshold: Minimum commits for collaboration consideration
        knowledge_silo_threshold: Concentration threshold for knowledge silos
        review_coverage_target: Target review coverage ratio
    """

    min_collaboration_threshold: int = 3
    knowledge_silo_threshold: float = 0.8
    review_coverage_target: float = 0.7


class CollaborationAnalyzer:
    """Analyzes team collaboration patterns in commit data.

    This class provides comprehensive collaboration analysis including:
    - Co-authorship patterns between developers
    - Knowledge distribution across file types
    - Review participation and effectiveness
    - Team connectivity and collaboration balance
    """

    def __init__(self, config: CollaborationConfig):
        """Initialize the CollaborationAnalyzer with configuration.

        Args:
            config: CollaborationConfig object with analysis parameters
        """
        self.min_collaboration_threshold = config.min_collaboration_threshold
        self.knowledge_silo_threshold = config.knowledge_silo_threshold
        self.review_coverage_target = config.review_coverage_target

    def analyze(self, range_stats: RangeStats) -> CollaborationMetrics:
        """Generate comprehensive collaboration metrics.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            CollaborationMetrics object with all collaboration analysis results
        """
        return CollaborationMetrics(
            co_authorship=self._analyze_co_authorship(range_stats),
            knowledge_distribution=self._analyze_knowledge_distribution(range_stats),
            review_metrics=self._analyze_review_metrics(range_stats),
            collaboration_patterns=self._identify_patterns(range_stats),
        )

    def _analyze_co_authorship(self, range_stats: RangeStats) -> CoAuthorshipMetrics:
        """Analyze co-authorship patterns between developers.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            CoAuthorshipMetrics object with collaboration analysis
        """
        if not range_stats.commits:
            return CoAuthorshipMetrics(
                author_pairs={}, collaboration_strength={}, top_collaborators=[]
            )

        # Group commits by files to find co-authorship
        file_authors: dict[str, list[str]] = defaultdict(list)
        for commit in range_stats.commits:
            for file_stat in commit.files:
                file_authors[file_stat.path].append(commit.author)

        # Calculate collaboration pairs
        author_pairs: dict[tuple[str, str], int] = defaultdict(int)
        for _, authors in file_authors.items():
            if len(authors) > 1:
                # Remove duplicates and sort for consistent pairing
                unique_authors = sorted(set(authors))
                for i in range(len(unique_authors)):
                    for j in range(i + 1, len(unique_authors)):
                        pair = (unique_authors[i], unique_authors[j])
                        author_pairs[pair] += 1

        # Calculate collaboration strength (normalized)
        max_collaboration = max(author_pairs.values()) if author_pairs else 1
        collaboration_strength = {
            pair: count / max_collaboration for pair, count in author_pairs.items()
        }

        # Get top collaborators
        top_collaborators = sorted(
            [(pair[0], pair[1], count) for pair, count in author_pairs.items()],
            key=lambda x: x[2],
            reverse=True,
        )[:10]  # Top 10 pairs

        return CoAuthorshipMetrics(
            author_pairs=dict(author_pairs),
            collaboration_strength=collaboration_strength,
            top_collaborators=top_collaborators,
        )

    def _analyze_knowledge_distribution(self, range_stats: RangeStats) -> KnowledgeDistribution:
        """Analyze knowledge distribution across file types.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            KnowledgeDistribution object with knowledge analysis
        """
        if not range_stats.commits:
            return KnowledgeDistribution(
                author_expertise={}, knowledge_silos=[], ownership_patterns={}
            )

        # Calculate author expertise by file type
        author_expertise: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(int))
        file_type_totals: dict[str, float] = defaultdict(int)

        for commit in range_stats.commits:
            for file_stat in commit.files:
                file_type = self._get_file_type(file_stat.path)
                author_expertise[commit.author][file_type] += 1
                file_type_totals[file_type] += 1

        # Convert to expertise scores (normalized)
        author_expertise_scores: dict[str, dict[str, float]] = {}
        for author, file_types in author_expertise.items():
            author_expertise_scores[author] = {}
            for file_type, commits in file_types.items():
                total_commits = file_type_totals[file_type]
                author_expertise_scores[author][file_type] = (
                    commits / total_commits if total_commits > 0 else 0
                )

        # Identify knowledge silos
        knowledge_silos: list[tuple[str, float]] = []
        for file_type, total_commits in file_type_totals.items():
            if total_commits >= self.min_collaboration_threshold:
                # Find the author with highest concentration
                max_concentration = 0.0
                for author_scores in author_expertise_scores.values():
                    concentration = author_scores.get(file_type, 0)
                    max_concentration = max(max_concentration, concentration)

                if max_concentration >= self.knowledge_silo_threshold:
                    knowledge_silos.append((file_type, max_concentration))

        # Calculate ownership patterns
        ownership_patterns: dict[str, list[str]] = {}
        for author, file_types in author_expertise_scores.items():
            owned_types = [
                file_type
                for file_type, score in file_types.items()
                if score >= self.knowledge_silo_threshold
            ]
            if owned_types:
                ownership_patterns[author] = owned_types

        return KnowledgeDistribution(
            author_expertise=author_expertise_scores,
            knowledge_silos=knowledge_silos,
            ownership_patterns=ownership_patterns,
        )

    def _analyze_review_metrics(self, range_stats: RangeStats) -> ReviewMetrics:
        """Analyze review participation and coverage.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            ReviewMetrics object with review analysis
        """
        if not range_stats.authors:
            return ReviewMetrics(
                review_participation={}, review_coverage={}, review_quality_indicators={}
            )

        # For now, use commit patterns as proxy for review activity
        # In a real implementation, this would analyze PR/review data

        total_commits = sum(range_stats.authors.values())

        review_participation = {}
        review_coverage = {}
        review_quality_indicators = {}

        for author, commits in range_stats.authors.items():
            # Review participation based on commit activity
            participation_score = min(commits * 2, 10)  # Scale up to max 10
            review_participation[author] = participation_score

            # Review coverage based on relative activity
            coverage = commits / total_commits if total_commits > 0 else 0
            review_coverage[author] = coverage

            # Quality indicator based on consistency and activity
            quality_score = min(coverage * 2 + 0.5, 1.0)
            review_quality_indicators[author] = quality_score

        return ReviewMetrics(
            review_participation=review_participation,
            review_coverage=review_coverage,
            review_quality_indicators=review_quality_indicators,
        )

    def _identify_patterns(self, range_stats: RangeStats) -> CollaborationPatterns:
        """Identify overall collaboration patterns.

        Args:
            range_stats: RangeStats object containing commit data

        Returns:
            CollaborationPatterns object with pattern analysis
        """
        if not range_stats.authors:
            return CollaborationPatterns(
                team_connectivity=0.0, collaboration_balance=0.0, knowledge_risk="high"
            )

        # Calculate team connectivity based on author distribution
        total_commits = sum(range_stats.authors.values())
        if total_commits == 0:
            return CollaborationPatterns(
                team_connectivity=0.0, collaboration_balance=0.0, knowledge_risk="high"
            )

        # Team connectivity: how evenly distributed the work is
        author_count = len(range_stats.authors)
        ideal_commits_per_author = total_commits / author_count
        connectivity_sum = 0.0

        for commits in range_stats.authors.values():
            deviation = abs(commits - ideal_commits_per_author) / ideal_commits_per_author
            connectivity_sum += 1 - deviation

        team_connectivity = connectivity_sum / author_count

        # Collaboration balance: measure of how collaborative the team is
        # Based on the ratio of single-author commits vs multi-author commits
        single_author_commits = 0
        multi_author_commits = 0

        for commit in range_stats.commits:
            if len(commit.files) > 0:
                authors_in_commit = set()
                for _ in commit.files:
                    authors_in_commit.add(commit.author)
                if len(authors_in_commit) == 1:
                    single_author_commits += 1
                else:
                    multi_author_commits += 1

        total_analyzed_commits = single_author_commits + multi_author_commits
        if total_analyzed_commits > 0:
            collaboration_balance = multi_author_commits / total_analyzed_commits
        else:
            collaboration_balance = 0.0

        # Knowledge risk assessment
        if team_connectivity > 0.7 and collaboration_balance > 0.6:
            knowledge_risk = "low"
        elif team_connectivity > 0.5 or collaboration_balance > 0.4:
            knowledge_risk = "medium"
        else:
            knowledge_risk = "high"

        return CollaborationPatterns(
            team_connectivity=team_connectivity,
            collaboration_balance=collaboration_balance,
            knowledge_risk=knowledge_risk,
        )

    def _get_file_type(self, file_path: str) -> str:
        """Extract file type from file path.

        Args:
            file_path: Path to the file

        Returns:
            File type/extension
        """
        if "." in file_path:
            return file_path.split(".")[-1].lower()
        return "unknown"
