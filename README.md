# Indigestible 📰

A Python-based newsletter aggregator that fetches, processes, and organizes tech newsletter content. Built to run in GitHub Actions for automated newsletter curation.

## Features

- 🔍 **Configurable Content Fetching**: Fetch content from multiple newsletter sources
- 🎯 **CSS Selector Support**: Extract specific content using CSS selectors
- 📅 **Frequency Tracking**: Track publication frequency (daily, weekly, monthly)
- 🤖 **AI-Powered Organization**: (Coming soon) Group content by themes and remove duplicates
- 📝 **GitHub Issues**: (Coming soon) Automatically create GitHub issues with curated content

## Installation

### Option 1: Using uv (Recommended - Fast! ⚡)

1. Install uv if you don't have it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# or: brew install uv
```

2. Clone and setup:
```bash
git clone <your-repo-url>
cd indigestible

# Create venv, install dependencies with lockfile in one command!
uv sync

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

That's it! `uv sync` reads `pyproject.toml` and `uv.lock` to create a reproducible environment.

### Option 2: Using standard pip

1. Clone the repository:
```bash
git clone <your-repo-url>
cd indigestible
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to add your newsletter sources:

```yaml
sources:
  - name: "Console.dev"
    url: "https://console.dev/"
    frequency: "weekly"
    selector: "main"  # Optional CSS selector
    enabled: true
```

### Configuration Options

- **name**: A friendly name for the source
- **url**: The URL to fetch content from
- **frequency**: Publication frequency (daily, weekly, biweekly, monthly)
- **selector**: Optional CSS selector to extract specific content
- **enabled**: Whether to process this source (true/false)

## Usage

### Basic Usage

Run the aggregator:
```bash
source .venv/bin/activate  # If not already activated
python src/main.py
```

### Managing Dependencies with uv

Add a new dependency:
```bash
uv add package-name
```

Remove a dependency:
```bash
uv remove package-name
```

Update all dependencies:
```bash
uv lock --upgrade
uv sync
```

The `uv.lock` file ensures everyone gets the exact same versions! 🔒

This will:
1. Fetch content from all enabled sources
2. Apply CSS selectors if specified
3. Save extracted content to `output/` directory
4. Display a summary in the console

### Output

- Console logs show processing status and content previews
- Full content is saved to `output/<source_name>_content.txt`

## Project Structure

```
indigestible/
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── fetcher.py       # HTML fetching and parsing
│   └── main.py          # Main execution script
├── config.yaml          # Source configuration
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

## Roadmap

### Current Version (v0.1)
- ✅ Configurable source management
- ✅ HTML fetching with CSS selector filtering
- ✅ Basic content extraction

### Upcoming Features
- 🔄 Duplicate detection and removal
- 🏷️ AI-powered theme grouping
- 🐙 GitHub issue creation
- 📊 Content analysis and statistics
- 🔔 GitHub Actions integration

## GitHub Actions Integration (Coming Soon)

This tool is designed to run in GitHub Actions on a schedule:

```yaml
name: Newsletter Aggregator
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  aggregate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python src/main.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
