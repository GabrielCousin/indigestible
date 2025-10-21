# Two-Step Fetch System

## Overview

The two-step fetch system allows you to fetch newsletters that don't have a direct link to the latest issue. Instead, you can:
1. Navigate to a list/archive page
2. Extract a link using a CSS selector
3. Fetch and parse the actual newsletter content

This is useful for newsletters that have archive pages or index pages where the latest issue is listed.

## Configuration

### Basic Structure

```yaml
- name: "Newsletter Name"
  list_page:
    url: "https://example.com/newsletter/archive"
    link_selector: "nav:not(.navbar) a"
    link_index: 0  # Optional: which matched link to use (default: 0)
  frequency: "weekly"
  selector: "article"
  ignore_selectors:
    - "nav"
    - "footer"
  output_format: "markdown"
  enabled: true
```

### Configuration Fields

#### `list_page` (object)
Main configuration object for two-step fetch. If present, the system will use two-step fetch instead of direct URL fetch.

- **`url`** (required, string): The URL of the list/archive page
- **`link_selector`** (required, string): CSS selector to find the link to the newsletter
- **`link_index`** (optional, integer, default: 0): Which matched link to use if multiple links match the selector

#### Other Fields
All other configuration fields work the same as with direct URL fetch:
- `selector`: CSS selector for content filtering
- `ignore_selectors`: List of selectors to remove from content
- `output_format`: "markdown" or "text"
- `enabled`: Whether the source is active

## Examples

### Example 1: This Week in React

```yaml
- name: "This Week in React"
  list_page:
    url: "https://thisweekinreact.com/newsletter"
    link_selector: "nav:not(.navbar) a"
    link_index: 0
  frequency: "weekly"
  selector: "article"
  ignore_selectors:
    - "nav"
    - "footer"
    - ".subscribe-form"
  output_format: "markdown"
  enabled: true
```

**How it works:**
1. Fetches `https://thisweekinreact.com/newsletter`
2. Finds all `<a>` tags within `<nav>` elements (excluding those with class `navbar`)
3. Extracts the `href` from the first match (index 0)
4. Converts relative URLs to absolute URLs
5. Fetches the newsletter content from the extracted URL
6. Applies the `article` selector and removes unwanted elements
7. Converts to markdown

### Example 2: Archive Page with Latest Issue

```yaml
- name: "Example Newsletter"
  list_page:
    url: "https://example.com/archive"
    link_selector: ".issue-list .latest a"
    link_index: 0
  selector: "main"
  output_format: "markdown"
  enabled: true
```

### Example 3: Using Link Index

If the first link isn't the one you want:

```yaml
- name: "Another Newsletter"
  list_page:
    url: "https://example.com/issues"
    link_selector: ".issue-item a"
    link_index: 1  # Get the second match
  selector: "article"
  output_format: "markdown"
  enabled: true
```

## How to Find the Right Selector

1. Open the list/archive page in your browser
2. Open Developer Tools (F12 or right-click → Inspect)
3. Use the element picker to select the link to the latest newsletter
4. Look at the HTML structure to determine the CSS selector
5. Test the selector in the browser console:
   ```javascript
   document.querySelectorAll('your-selector-here')
   ```
6. Verify it selects the right link(s)

## Tips

- **Relative URLs**: The system automatically converts relative URLs to absolute URLs
- **Multiple Matches**: If your selector matches multiple links, use `link_index` to specify which one to use
- **Fallback**: If the link extraction fails, the source will be skipped with an error message
- **Debugging**: Check the logs to see which URL was extracted and if there were any issues

## Backward Compatibility

The original direct URL fetch still works. Just use the `url` field directly:

```yaml
- name: "Direct Newsletter"
  url: "https://example.com/latest"
  selector: "main"
  output_format: "markdown"
  enabled: true
```

You cannot use both `url` and `list_page` in the same source configuration. If `list_page` is present, it takes precedence.
