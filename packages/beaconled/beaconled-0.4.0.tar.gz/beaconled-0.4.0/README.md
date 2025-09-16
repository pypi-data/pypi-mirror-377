# Beacon Delivery Compass

[![PyPI version](https://badge.fury.io/py/beaconled.svg)](https://badge.fury.io/py/beaconled)
[![Python Version](https://img.shields.io/pypi/pyversions/beaconled.svg)](https://pypi.org/project/beaconled/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Your delivery compass for empowered product builders. Transform engineering activity into executive-ready insights and data-driven product delivery decisions.

## Quick Install

Beacon requires Python 3.10+ and Git 2.23+. We recommend installing in a virtual environment.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install from PyPI
pip install beaconled

# Verify installation
beaconled --version
```

## Quick Start

Analyze a git repository:
```bash
beaconled /path/to/repo
```

Generate a weekly team report:
```bash
beaconled --since 1w --until "now"
```

### Usage Examples

#### Basic Analysis
```bash
# Analyze changes in the last 3 days
beaconled --since "3d"

# Date range analysis with timezone support
beaconled --since "2025-01-01" --until "2025-01-31"

# Extended analysis with team, quality, and risk metrics
beaconled --since "2w" --format extended

# Generate visual heatmaps of commit activity (requires matplotlib)
beaconled --since "1w" --format heatmap

# Disable emoji icons for plain text output
beaconled --since "1w" --no-emoji
```

#### Extended Format Features
The extended format (`--format extended`) includes comprehensive analytics:

- **Time-Based Analytics**: Velocity trends, activity heatmaps, peak periods
- **Team Collaboration**: Co-authorship patterns, ownership distribution
- **Code Quality**: Churn metrics, complexity trends, large changes
- **Risk Assessment**: Risk indicators, hotspot detection, stability metrics
- **File Analysis**:
  - **Largest Changes**: Identify files with most modifications (additions + deletions)
  - **Frequently Changed**: Track most active files during the analysis period
  - **Lifecycle Tracking**: Monitor file operations (added/modified/deleted/renamed)

Example:
```
=== TIME-BASED ANALYTICS ===
• Velocity: 5.2 commits/day
• Peak hours: 10:00, 14:00
• Bus factor: 3

=== TEAM COLLABORATION ===
• Core contributors: alice, bob
• Knowledge distribution: Balanced

=== CODE QUALITY ===
• Churn rate: 12.5%
• Complexity trend: Decreasing

=== RISK ASSESSMENT ===
• Risk score: 4/10
• Hotspots: src/auth/, src/api/

=== FILE ANALYSIS ===
• Largest Changes (Top 5):
  - src/core/engine.py: 1,245 lines changed
  - tests/test_engine.py: 856 lines changed
  - src/api/endpoints.py: 732 lines changed
  - src/utils/helpers.py: 521 lines changed
  - docs/api_reference.md: 487 lines changed

• Frequently Changed:
  - src/utils/helpers.py: 12 changes
  - src/config/settings.py: 8 changes
  - tests/conftest.py: 7 changes
  - src/api/middleware/auth.py: 6 changes
  - src/core/models.py: 5 changes

• File Lifecycle (this period):
  - Added: 12 files
  - Modified: 45 files
  - Deleted: 5 files
  - Renamed: 3 files
```

#### Date Formats
Beacon supports flexible date parsing with UTC timezone handling:

```bash
# Relative dates
beaconled --since "1d"   # 1 day ago
beaconled --since "2w"   # 2 weeks ago
beaconled --since "3m"   # 3 months ago

# Absolute dates (UTC)
beaconled --since "2025-01-15"
beaconled --since "2025-01-15 14:30"
```

For more examples, see [Basic Usage](docs/examples/basic-usage.md) and [Advanced Usage](docs/examples/advanced-usage.md) guides.

## Sample Outputs

### Repository Analysis

```bash
beaconled /path/to/my-project
```

```
Repository Analysis: /path/to/my-project
Analysis Period: Last 30 commits

=== COMMIT SUMMARY ===
Total Commits: 30
Contributors: 4
Date Range: 2025-01-15 to 2025-01-23

=== COMMIT DETAILS ===
[2025-01-23 14:32] feat: Add user authentication module (John Doe)
  Impact: HIGH - 8 files changed, 245 insertions, 12 deletions
  Components: auth/, middleware/, tests/

[2025-01-23 10:15] fix: Resolve database connection timeout (Jane Smith)
  Impact: MEDIUM - 3 files changed, 28 insertions, 15 deletions
  Components: database/, config/

=== FILE CHANGE METRICS ===
Most Active Files:
  src/auth/login.py: 12 changes
  config/database.py: 8 changes
  tests/test_auth.py: 6 changes

=== IMPACT ASSESSMENT ===
High Impact Commits: 8 (27%)
Medium Impact Commits: 15 (50%)
Low Impact Commits: 7 (23%)
```

### Weekly Team Report

```bash
beaconled --since "1w" --format extended
```

```
🗓️ Analysis Period: 2025-01-16 to 2025-01-23 (7 days)

commits Total commits: 23
files changed Total files changed: 156
lines added Total lines added: 2,847
lines deleted Total lines deleted: 1,234
net change Net change: 1,613

🚀 === TEAM OVERVIEW ===
👥 Total Contributors: 4
Total Commits: 23
Average Commits/Day: 2.9
Active Days: 6/7

🔍 === CONTRIBUTOR BREAKDOWN ===
John Doe <john@company.com>: 9 commits (39%)
  - High Impact: 3 commits
  - Medium Impact: 4 commits
  - Low Impact: 2 commits
  - Most Active: Monday, Wednesday

Jane Smith <jane@company.com>: 7 commits (30%)
  - High Impact: 2 commits
  - Medium Impact: 3 commits
  - Low Impact: 2 commits
  - Most Active: Tuesday, Friday

Bob Wilson <bob@company.com>: 7 commits (30%)
  - High Impact: 1 commits
  - Medium Impact: 4 commits
  - Low Impact: 2 commits
  - Most Active: Wednesday, Thursday

🔥 === COMPONENT ACTIVITY ===
Most Changed Components:
  frontend/: 8 commits, 1,234 lines
  backend/api/: 6 commits, 892 lines
  tests/: 5 commits, 567 lines
  docs/: 4 commits, 154 lines

=== TIME-BASED ANALYTICS ===
• Velocity: 5.2 commits/day
• Peak hours: 10:00, 14:00
• Bus factor: 3

=== TEAM COLLABORATION ===
• Core contributors: alice, bob
• Knowledge distribution: Balanced

=== CODE QUALITY ===
• Churn rate: 12.5%
• Complexity trend: Decreasing

=== RISK ASSESSMENT ===
• Risk score: 4/10
• Hotspots: src/auth/, src/api/

=== FILE ANALYSIS ===
• Largest Changes (Top 5):
  - src/core/engine.py: 1,245 lines changed
  - tests/test_engine.py: 856 lines changed
  - src/api/endpoints.py: 732 lines changed
  - src/utils/helpers.py: 521 lines changed
  - docs/api_reference.md: 487 lines changed

• Frequently Changed:
  - src/utils/helpers.py: 12 changes
  - src/config/settings.py: 8 changes
  - tests/conftest.py: 7 changes
  - src/api/middleware/auth.py: 6 changes
  - src/core/models.py: 5 changes

• File Lifecycle (this period):
  - Added: 12 files
  - Modified: 45 files
  - Deleted: 5 files
  - Renamed: 3 files
```

## Features

- **Executive-Ready Reports**: Transform engineering metrics into business insights for leadership decisions
- **Team Health Monitoring**: Data-driven team management with contribution analysis and workload distribution
- **Product Delivery Analytics**: Comprehensive insights into development patterns, release readiness, and technical health
- **Multi-Stakeholder Value**: One platform serving executives, engineering managers, and technical leads
- **Flexible Output Formats**: Choose from standard, extended, JSON, and heatmap formats to fit your workflow needs
- **Visual Analytics**: Generate interactive heatmaps showing commit patterns and author activity over time
- **Emoji-Enhanced Visual Scanning**: Optional emoji icons for better visual parsing of output (configurable via --no-emoji)
- **Reliable Git Integration**: Built on GitPython for robust and secure repository operations
- **Rich Terminal Output**: Colorized and well-formatted output powered by `rich`

## Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions and troubleshooting
- [Basic Usage](docs/examples/basic-usage.md) - Standard repository analysis
- [Advanced Usage](docs/examples/advanced-usage.md) - Executive reporting, team health, and technical debt analysis
- [Integration Guide](docs/delivery/integrations.md) - CI/CD pipelines and git hooks
- [API Reference](docs/api/api.md) - Detailed API documentation
- [System Architecture](docs/development/architecture/overview.md) - High-level system design

## Development & Contribution

We welcome contributions! For details on how to contribute, please see our [Contribution Guidelines](CONTRIBUTING.md).

### Project Roadmap

Our development priorities and planned improvements are tracked in the [Enhancement Plan](docs/development/roadmap.md). This document provides visibility into:
- Upcoming features and improvements
- Current technical debt
- Performance optimization plans
- Testing and quality assurance goals

### Code Quality

Beacon is built with a strong focus on code quality and maintainability. We use pre-commit hooks to ensure consistent code quality across the project.

#### Pre-commit Configuration

We provide two pre-commit configurations:

1. **Development Mode** (`.pre-commit-dev.yaml`):
   - More lenient rules for local development
   - Focuses on critical issues only
   - Faster feedback loop

   ```bash
   # Setup development pre-commit hooks
   make dev-setup
   ```

2. **Production Mode** (`.pre-commit-config.yaml`):
   - Strict rules for CI/CD and production
   - Enforces all code quality standards
   - Includes all linters and formatters

   ```bash
   # Setup production pre-commit hooks
   make prod-setup
   ```

#### Key Quality Tools

- **Type Safety**: Full static type checking with [mypy](https://mypy-lang.org/)
- **Code Style**: Consistent code formatting with [Black](https://black.readthedocs.io/)
- **Linting**: Code quality enforcement with [Ruff](https://github.com/charliermarsh/ruff)
- **Documentation**: Comprehensive docstrings and API documentation

#### Development Workflow

1. During active development, use `dev-setup` for faster commits
2. Before pushing changes, run `prod-setup` to ensure all checks pass
3. Use `git commit --no-verify` sparingly when needed

#### Manual Checks

```bash
# Run type checking
mypy --ignore-missing-imports src/beaconled

# Run all code quality checks
make lint
```

### Testing

For contributors, run the test suite with:

```bash
python run_tests.py
```

For detailed testing options, see our [Testing Guide](docs/development/testing.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

Check out our [Roadmap](docs/development/roadmap.md) to see what we're working on and what's coming next!
