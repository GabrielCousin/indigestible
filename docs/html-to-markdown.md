# HTML to Markdown Conversion

This project uses the [markdownify](https://github.com/matthewwithanm/python-markdownify) library to convert HTML content to clean, well-formatted Markdown.

## Why Markdown?

Markdown is ideal for newsletter content because:
- ✅ **Human-readable** - Easy to read in plain text
- ✅ **Git-friendly** - Tracks changes cleanly in version control
- ✅ **AI-friendly** - Large Language Models work better with structured markdown
- ✅ **Universal** - Can be rendered to HTML, PDF, or other formats
- ✅ **Lightweight** - Much smaller than HTML

## Configuration

In `config.yaml`, set the output format per source:

```yaml
sources:
  - name: "My Newsletter"
    url: "https://example.com"
    output_format: "markdown"  # or "text" for plain text
```

## Conversion Features

### Headings
```html
<h1>Main Title</h1>
<h2>Section</h2>
```
Converts to:
```markdown
# Main Title
## Section
```

### Links
```html
<a href="https://example.com">Link Text</a>
```
Converts to:
```markdown
[Link Text](https://example.com)
```

### Lists
```html
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>
```
Converts to:
```markdown
- Item 1
- Item 2
```

### Emphasis
```html
<strong>Bold</strong> and <em>italic</em>
```
Converts to:
```markdown
**Bold** and *italic*
```

### Code
```html
<code>inline code</code>
<pre>code block</pre>
```
Converts to:
```markdown
`inline code`
\```
code block
\```
```

## Advanced Usage

### Custom Conversion Options

The fetcher uses these default settings:
- **heading_style**: `"ATX"` - Uses `#` style headings
- **bullets**: `"-"` - Uses `-` for unordered lists
- **strong_em_symbol**: `"**"` - Uses `**` for bold text
- **strip**: `['script', 'style']` - Removes script and style tags

### Whitespace Handling

The converter automatically:
- Removes trailing whitespace from lines
- Collapses multiple consecutive empty lines to one
- Strips leading/trailing empty lines from the output

## Comparison: Text vs Markdown

### Plain Text Output
```
Latest newsletter
Here's the latest newsletter sent on 2025-10-09.
Contents
ut — CLI toolkit.
RioTerm — Terminal.
```

### Markdown Output
```markdown
## Latest newsletter

Here's the latest newsletter sent on 2025-10-09.

### Contents

- [ut](https://github.com/ksdme/ut)
  — CLI toolkit.
- [RioTerm](https://rioterm.com/)
  — Terminal.
```

The markdown version preserves:
- Document structure (headings)
- Clickable links
- List formatting
- Better readability

## Why markdownify?

**markdownify** is the best Python library for HTML-to-Markdown conversion because:

1. **Active maintenance** - Regularly updated
2. **BeautifulSoup integration** - Works seamlessly with BS4
3. **Highly configurable** - Customize every aspect of conversion
4. **Smart defaults** - Works great out of the box
5. **Handles edge cases** - Nested elements, malformed HTML, etc.

## Alternative Libraries

Other options we considered:
- `html2text` - Older, less maintained
- `tomd` - Limited configuration options
- `pypandoc` - Requires external Pandoc binary

**markdownify** was chosen for its simplicity, reliability, and active maintenance.
