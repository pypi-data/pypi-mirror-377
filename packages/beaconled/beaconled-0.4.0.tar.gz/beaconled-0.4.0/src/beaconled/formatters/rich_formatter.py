"""Rich formatter for enhanced terminal output using the Rich library."""

from io import StringIO

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from beaconled.core.models import CommitStats, RangeStats

from .base_formatter import BaseFormatter


class RichFormatter(BaseFormatter):
    """Rich formatter for enhanced terminal output with tables, panels, and colors.

    Uses the Rich library to provide visually appealing and structured output
    with proper formatting, colors, and layout for git repository analytics.
    """

    def __init__(self, console: Console | None = None):
        """Initialize the Rich formatter.

        Args:
            console: Rich console instance. If None, creates a new one.
        """
        self.console = console or Console()

    def format_commit_stats(self, stats: CommitStats) -> str:
        """Format commit statistics using Rich components."""
        # Use StringIO to capture console output
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        # Create main commit panel
        commit_info = Table(box=box.ROUNDED, show_header=False)
        commit_info.add_column("Field", style="cyan", no_wrap=True)
        commit_info.add_column("Value", style="white")

        commit_info.add_row("📊 Commit", f"[bold blue]{stats.hash[:8]}[/bold blue]")
        commit_info.add_row("👤 Author", f"[green]{stats.author}[/green]")
        commit_info.add_row("📅 Date", f"[yellow]{self._format_date(stats.date)}[/yellow]")
        commit_info.add_row("💬 Message", f"[white]{stats.message}[/white]")

        # Create statistics table
        stats_table = Table(box=box.SIMPLE, title="📈 Statistics", title_style="bold magenta")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white", justify="right")

        stats_table.add_row("Files Changed", f"{stats.files_changed:,}")
        stats_table.add_row("Lines Added", f"[green]+{stats.lines_added:,}[/green]")
        stats_table.add_row("Lines Deleted", f"[red]-{stats.lines_deleted:,}[/red]")
        stats_table.add_row(
            "Net Change", self._format_net_change(stats.lines_added, stats.lines_deleted)
        )

        # Add commit info panel
        commit_panel = Panel(commit_info, title="[bold]Commit Details[/bold]", border_style="blue")
        console.print(commit_panel)
        console.print()

        # Add statistics
        console.print(stats_table)
        console.print()

        # Create file changes table if files exist
        if stats.files:
            file_table = Table(box=box.SIMPLE, title="📂 File Changes", title_style="bold blue")
            file_table.add_column("File", style="cyan", no_wrap=True)
            file_table.add_column("Added", style="green", justify="right")
            file_table.add_column("Deleted", style="red", justify="right")
            file_table.add_column("Net", style="yellow", justify="right")

            for file_stat in stats.files:
                net = file_stat.lines_added - file_stat.lines_deleted
                net_color = "green" if net >= 0 else "red"
                file_table.add_row(
                    file_stat.path,
                    f"+{file_stat.lines_added:,}",
                    f"-{file_stat.lines_deleted:,}",
                    f"[{net_color}]{net:,}[/{net_color}]",
                )
            console.print(file_table)
            console.print()

        # Create file type breakdown if files exist
        if stats.files:
            file_types = self._get_file_type_breakdown(stats.files)
            if file_types:
                file_types_table = Table(
                    box=box.SIMPLE, title="🔍 File Types", title_style="bold purple"
                )
                file_types_table.add_column("Type", style="cyan")
                file_types_table.add_column("Files", style="white", justify="right")
                file_types_table.add_column("Added", style="green", justify="right")
                file_types_table.add_column("Deleted", style="red", justify="right")

                for ext, counts in sorted(file_types.items()):
                    file_types_table.add_row(
                        ext,
                        f"{counts['count']:,}",
                        f"+{counts['added']:,}",
                        f"-{counts['deleted']:,}",
                    )
                console.print(file_types_table)

        return output_buffer.getvalue()

    def format_range_stats(self, stats: RangeStats) -> str:
        """Format range statistics using Rich components."""
        # Use StringIO to capture console output
        output_buffer = StringIO()
        console = Console(file=output_buffer, width=120)

        # Calculate duration
        duration_days = (stats.end_date.date() - stats.start_date.date()).days
        if duration_days == 0:
            duration_days = 1

        # Create main overview panel
        overview_table = Table(box=box.ROUNDED, show_header=False)
        overview_table.add_column("Field", style="cyan", no_wrap=True)
        overview_table.add_column("Value", style="white")

        start_date = self._format_date(stats.start_date).split()[0]
        end_date = self._format_date(stats.end_date).split()[0]
        overview_table.add_row("📅 Period", f"{start_date} to {end_date}")
        overview_table.add_row("📊 Duration", f"{duration_days} days")
        overview_table.add_row("🔢 Total Commits", f"{stats.total_commits:,}")
        overview_table.add_row("📂 Files Changed", f"{stats.total_files_changed:,}")
        overview_table.add_row("+ Lines Added", f"[green]{stats.total_lines_added:,}[/green]")
        overview_table.add_row("- Lines Deleted", f"[red]{stats.total_lines_deleted:,}[/red]")
        overview_table.add_row(
            "🔄 Net Change",
            self._format_net_change(stats.total_lines_added, stats.total_lines_deleted),
        )

        # Add overview panel
        overview_panel = Panel(
            overview_table, title="[bold]📈 Range Analysis Overview[/bold]", border_style="green"
        )
        console.print(overview_panel)
        console.print()

        # Create team overview table
        if stats.authors:
            active_days = len(getattr(stats, "commits_by_day", {}))
            avg_commits_per_day = round(stats.total_commits / max(duration_days, 1), 1)

            team_table = Table(box=box.SIMPLE, title="👥 Team Overview", title_style="bold green")
            team_table.add_column("Metric", style="cyan")
            team_table.add_column("Value", style="white", justify="right")

            team_table.add_row("Contributors", f"{len(stats.authors)}")
            team_table.add_row("Total Commits", f"{stats.total_commits}")
            team_table.add_row("Avg Commits/Day", f"{avg_commits_per_day}")
            team_table.add_row("Active Days", f"{active_days}/{duration_days}")

            console.print(team_table)
            console.print()

        # Create contributor breakdown table
        if stats.authors and hasattr(stats, "author_impact_stats"):
            contributor_table = Table(
                box=box.SIMPLE, title="📈 Contributor Breakdown", title_style="bold yellow"
            )
            contributor_table.add_column("Author", style="cyan", no_wrap=True)
            contributor_table.add_column("Commits", style="white", justify="right")
            contributor_table.add_column("Percentage", style="magenta", justify="right")
            contributor_table.add_column("High Impact", style="red", justify="right")
            contributor_table.add_column("Medium Impact", style="yellow", justify="right")
            contributor_table.add_column("Low Impact", style="green", justify="right")

            # Sort authors by commit count
            top_contributors = sorted(stats.authors.items(), key=lambda x: x[1], reverse=True)[
                :5
            ]  # Top 5

            for author, commit_count in top_contributors:
                percentage = round((commit_count / stats.total_commits) * 100, 1)

                # Get impact stats
                impact_stats = stats.author_impact_stats.get(author, {})
                high_impact = impact_stats.get("high", 0)
                medium_impact = impact_stats.get("medium", 0)
                low_impact = impact_stats.get("low", 0)

                contributor_table.add_row(
                    author,
                    f"{commit_count}",
                    f"{percentage}%",
                    f"{high_impact}",
                    f"{medium_impact}",
                    f"{low_impact}",
                )

            console.print(contributor_table)
            console.print()

        # Create component activity table
        if hasattr(stats, "component_stats") and stats.component_stats:
            component_table = Table(
                box=box.SIMPLE, title="🔥 Component Activity", title_style="bold red"
            )
            component_table.add_column("Component", style="cyan", no_wrap=True)
            component_table.add_column("Commits", style="white", justify="right")
            component_table.add_column("Lines Changed", style="yellow", justify="right")

            # Sort components by commits, then by lines
            sorted_components = sorted(
                stats.component_stats.items(),
                key=lambda x: (x[1]["commits"], x[1]["lines"]),
                reverse=True,
            )[:5]  # Top 5 components

            for component, component_stats in sorted_components:
                component_table.add_row(
                    component, f"{component_stats['commits']}", f"{component_stats['lines']:,}"
                )

            console.print(component_table)
            console.print()

        # Create daily activity table
        if hasattr(stats, "commits_by_day") and stats.commits_by_day:
            daily_table = Table(box=box.SIMPLE, title="📊 Daily Activity", title_style="bold cyan")
            daily_table.add_column("Date", style="cyan")
            daily_table.add_column("Commits", style="white", justify="right")

            # Show last 7 days of activity
            recent_days = sorted(stats.commits_by_day.items(), reverse=True)[:7]

            for date, count in recent_days:
                daily_table.add_row(date, f"{count}")

            console.print(daily_table)

        return output_buffer.getvalue()
