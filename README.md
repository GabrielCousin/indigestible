# Indigestible 📰

A Python-based newsletter aggregator that fetches, processes, and organizes tech newsletter content. Built to run in GitHub Actions for automated newsletter curation.

## Features

- 🔍 **Configurable Content Fetching**: Fetch content from multiple newsletter sources
- 🎯 **CSS Selector Support**: Extract specific content using CSS selectors
- 🚫 **Element Filtering**: Remove unwanted elements (ads, forms, navigation) with ignore selectors
- 📝 **Markdown Conversion**: Convert HTML to clean, well-formatted Markdown automatically
- 📅 **Frequency Tracking**: Track publication frequency (daily, weekly, monthly)
- 🤖 **AI-Powered Summarization**: Group content by themes using OpenAI
- 🔗 **Two-Step Fetch**: Extract newsletter links from archive pages before fetching content
- 🐙 **GitHub Actions Integration**: Automatically create GitHub issues with weekly digests

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
- **url**: The direct URL to fetch content from (for direct access)
- **list_page**: Configuration for two-step fetch from archive pages (alternative to `url`)
  - **url**: The URL of the list/archive page
  - **link_selector**: CSS selector to find the newsletter link
  - **link_index**: Which matched link to use (default: 0)
- **frequency**: Publication frequency (daily, weekly, biweekly, monthly)
- **selector**: Optional CSS selector to extract specific content
- **ignore_selectors**: Optional list of CSS selectors to remove (e.g., ads, forms, navigation)
- **output_format**: Output format - `"markdown"` (default) or `"text"`
- **enabled**: Whether to process this source (true/false)

**Note**: Use either `url` for direct links or `list_page` for two-step fetch. See [`docs/two-step-fetch.md`](docs/two-step-fetch.md) for details.

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
├── .github/
│   └── workflows/
│       └── newsletter-digest.yml  # GitHub Actions workflow
├── docs/
│   ├── github-action.md           # GitHub Action documentation
│   ├── two-step-fetch.md          # Two-step fetch system guide
│   └── html-to-markdown.md        # Markdown conversion details
├── src/
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── fetcher.py                 # HTML fetching and parsing
│   ├── main.py                    # Main execution script
│   ├── summarizer.py              # AI-powered summarization
│   └── summarize.py               # Summary generation script
├── output/                        # Generated newsletter content
├── config.yaml                    # Source & AI configuration
├── pyproject.toml                 # Project metadata & dependencies
├── uv.lock                        # Locked dependency versions
├── .env                           # API keys (not committed)
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

### Current Version (v0.2)
- ✅ Configurable source management
- ✅ HTML fetching with CSS selector filtering
- ✅ Markdown conversion
- ✅ AI-powered summarization with OpenAI
- ✅ Support for GPT-4o, GPT-5, and o1 models
- ✅ Two-step fetch system for archive pages
- ✅ GitHub Actions integration with automated issue creation

### Upcoming Features
- 🔄 Duplicate detection and removal
- 📊 Content analysis and statistics
- 📧 Email notifications for digest

## GitHub Actions Integration

The project includes a GitHub Action that automatically runs every Monday at 8AM Paris time and creates a GitHub issue with the weekly newsletter digest.

### Quick Start

The workflow is already configured in `.github/workflows/newsletter-digest.yml` and will:
1. ✅ Fetch all enabled newsletters
2. ✅ Generate an AI-curated summary organized by topic
3. ✅ Create a formatted GitHub issue with the summary
4. ✅ Upload all files as artifacts (for reference)

**Setup Required:**
- Add `OPENAI_API_KEY` as a repository secret in Settings → Secrets and variables → Actions
- The AI model is configured in `config.yaml` (default: `gpt-5-nano`)

### Manual Trigger

You can manually trigger the workflow anytime:
1. Go to **Actions** tab in your repository
2. Select **Newsletter Digest** workflow
3. Click **Run workflow**

### Issue Format

Each issue includes:
- 🤖 Title: `AI Newsletter Digest - [Date]`
- 📝 **AI-curated summary** organized by topic (React, JavaScript, Tools, etc.)
- 🏷️ Automatic labels: `newsletter`, `automated`

The AI summary removes duplicates, filters ads/sponsors, groups related content intelligently, and stays under 65k characters for readability.

For detailed configuration and customization options, see [`docs/github-action.md`](docs/github-action.md).

### Schedule Customization

Edit `.github/workflows/newsletter-digest.yml` to change when it runs:

```yaml
on:
  schedule:
    - cron: '0 6 * * 1'  # 6AM UTC = ~8AM Paris time on Mondays
  workflow_dispatch:  # Allow manual triggers
```

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
