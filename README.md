# Indigestible 📰

A Python-based newsletter aggregator that fetches, processes, and organizes tech newsletter content. Built to run in GitHub Actions for automated newsletter curation.

## Features

- 🔍 **Configurable Content Fetching**: Fetch content from multiple newsletter sources
- 🎯 **CSS Selector Support**: Extract specific content using CSS selectors
- 🚫 **Element Filtering**: Remove unwanted elements (ads, forms, navigation) with ignore selectors
- 📝 **Markdown Conversion**: Convert HTML to clean, well-formatted Markdown automatically
- 📅 **Frequency Tracking**: Track publication frequency (daily, weekly, monthly)
- 🤖 **AI-Powered Summarization**: Group content by themes using OpenAI
- 🔄 **GitHub Issues**: (Coming soon) Automatically create GitHub issues with curated content

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
    ignore_selectors:  # Optional list to remove unwanted elements
      - "header"
      - "nav"
      - "footer"
      - "form"
    output_format: "markdown"
    enabled: true

ai:
  model: "gpt-4o-mini"  # OpenAI model
  temperature: 0.7
```

### Configuration Options

#### Newsletter Sources
- **name**: A friendly name for the source
- **url**: The URL to fetch content from
- **frequency**: Publication frequency (daily, weekly, biweekly, monthly)
- **selector**: Optional CSS selector to extract specific content
- **ignore_selectors**: Optional list of CSS selectors to remove (e.g., ads, forms, navigation)
- **output_format**: Output format - `"markdown"` (default) or `"text"`
- **enabled**: Whether to process this source (true/false)

#### AI Configuration
- **model**: OpenAI model to use (e.g., `gpt-4o-mini`, `gpt-5-nano`, `gpt-4o`)
- **temperature**: Creativity level (0.0-1.0, default: 0.7) - note: not supported by GPT-5/o1 models

## Usage

### Basic Usage

1. **Fetch newsletters:**
```bash
source .venv/bin/activate  # If not already activated
python src/main.py
```

2. **Generate AI summary:**

First, create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

Then configure your model in `config.yaml`:
```yaml
ai:
  model: "gpt-4o-mini"  # or gpt-5-nano, gpt-4o, etc.
```

Run the summarizer:
```bash
python src/summarize.py
```

This will create `output/SUMMARY.md` with an organized summary grouped by:
- React
- JavaScript
- Updates
- New Tools
- Design
- Misc

The summary automatically:
- Removes sponsor content and ads
- Filters out React Native and mobile-specific content
- Cleans URLs and removes tracking parameters
- Groups content by theme (not by source)

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
- Full content is saved to `output/<source_name>_content.md` (or `.txt` for plain text format)
- Markdown output includes proper formatting: headings, links, lists, emphasis

### Markdown Conversion Features

The `markdownify` library provides excellent HTML-to-Markdown conversion:
- **Headings**: `<h1>` → `#`, `<h2>` → `##`, etc.
- **Links**: `<a href="...">text</a>` → `[text](...)`
- **Lists**: Proper bullet (`-`) and numbered lists
- **Emphasis**: `<strong>` → `**bold**`, `<em>` → `*italic*`
- **Code**: `<code>` and `<pre>` blocks preserved
- Automatic cleanup of extra whitespace

### Automatic Content Cleanup

The fetcher automatically removes noisy elements:
- **Scripts**: All `<script>` tags including JSON-LD structured data
- **Styles**: All `<style>` tags and inline `style` attributes
- **Images**: All `<img>`, `<picture>`, and `<svg>` tags
- Perfect for text-focused AI processing!

## Project Structure

```
indigestible/
├── src/
│   ├── __init__.py
│   ├── config.py        # Configuration management
│   ├── fetcher.py       # HTML fetching and parsing
│   ├── main.py          # Main execution script
│   ├── summarizer.py    # AI-powered summarization
│   └── summarize.py     # Summary generation script
├── config.yaml          # Source & AI configuration
├── pyproject.toml       # Project metadata & dependencies
├── uv.lock              # Locked dependency versions
├── .env                 # API keys (not committed)
├── .gitignore
└── README.md
```

## Supported Models

### OpenAI Models
- **GPT-4o models**: `gpt-4o`, `gpt-4o-mini` - Latest generation, great balance of speed and quality
- **GPT-5 models**: `gpt-5-nano` - Newest generation with larger context windows
- **o1 models**: `o1-preview`, `o1-mini` - Advanced reasoning models
- **Legacy**: `gpt-4-turbo`, `gpt-3.5-turbo`

**API Key**: Set `OPENAI_API_KEY` or `OPEN_AI_API_KEY` in `.env`

**Note**: GPT-5 and o1 models use `max_completion_tokens` instead of `max_tokens` and have fixed temperature settings.

## Roadmap

### Current Version (v0.1)
- ✅ Configurable source management
- ✅ HTML fetching with CSS selector filtering
- ✅ Markdown conversion
- ✅ AI-powered summarization with OpenAI
- ✅ Support for GPT-4o, GPT-5, and o1 models

### Upcoming Features
- 🔄 Duplicate detection and removal
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
