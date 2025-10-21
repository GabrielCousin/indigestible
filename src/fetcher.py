"""
Module for fetching and parsing HTML content from newsletter sources.
"""

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from typing import Optional, Dict, Any, Literal
import logging

logger = logging.getLogger(__name__)


class ContentFetcher:
    """Fetches and parses HTML content from web sources."""

    def __init__(self, timeout: int = 30):
        """
        Initialize the ContentFetcher.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_link_from_list(
        self,
        list_url: str,
        link_selector: str,
        link_index: int = 0
    ) -> Optional[str]:
        """
        Fetch a URL from a list/archive page using a CSS selector.

        Args:
            list_url: The URL of the list/archive page
            link_selector: CSS selector to find the target link
            link_index: Which matched link to use (default: 0 for first)

        Returns:
            The extracted URL, or None if not found

        Raises:
            requests.RequestException: If the request fails
        """
        logger.info(f"Fetching link from list page: {list_url}")
        logger.info(f"Using selector: {link_selector}")

        try:
            response = self.session.get(list_url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Find all matching links
            links = soup.select(link_selector)

            if not links:
                logger.warning(f"No links found with selector: {link_selector}")
                return None

            if link_index >= len(links):
                logger.warning(f"Link index {link_index} out of range. Found {len(links)} link(s)")
                link_index = 0

            # Get the href from the selected link
            target_link = links[link_index]
            href = target_link.get('href')

            if not href:
                logger.warning(f"Selected link has no href attribute")
                return None

            # Handle relative URLs
            from urllib.parse import urljoin
            absolute_url = urljoin(list_url, href)

            logger.info(f"Extracted URL: {absolute_url}")
            return absolute_url

        except requests.RequestException as e:
            logger.error(f"Failed to fetch list page {list_url}: {str(e)}")
            return None

    def fetch_content(
        self,
        url: str,
        selector: Optional[str] = None,
        ignore_selectors: Optional[list] = None,
        output_format: Literal["text", "markdown"] = "markdown"
    ) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL and optionally filter by CSS selector.

        Args:
            url: The URL to fetch
            selector: Optional CSS selector to filter content
            ignore_selectors: Optional list of CSS selectors to remove from content
            output_format: Output format - "text" for plain text or "markdown" for markdown

        Returns:
            Dictionary with 'url', 'title', 'content', 'raw_html', and 'format'

        Raises:
            requests.RequestException: If the request fails
        """
        logger.info(f"Fetching content from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Remove unwanted elements early (before selector filtering)
            # Remove all script tags (including JSON-LD)
            for script in soup.find_all('script'):
                script.decompose()

            # Remove all style tags
            for style in soup.find_all('style'):
                style.decompose()

            # Remove all images
            for img in soup.find_all('img'):
                img.decompose()

            # Remove picture elements
            for picture in soup.find_all('picture'):
                picture.decompose()

            # Remove SVG elements (often used as icons/images)
            for svg in soup.find_all('svg'):
                svg.decompose()

            # Remove inline styles
            for tag in soup.find_all(style=True):
                del tag['style']

            # Extract title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else url

            # Filter by selector if provided
            if selector:
                logger.info(f"Applying selector: {selector}")
                selected_elements = soup.select(selector)

                if not selected_elements:
                    logger.warning(f"Selector '{selector}' matched no elements")
                    content_soup = soup
                else:
                    # Create new soup with only selected elements
                    content_soup = BeautifulSoup('', 'lxml')
                    for element in selected_elements:
                        content_soup.append(element)
            else:
                content_soup = soup

            # Remove ignored elements
            if ignore_selectors:
                removed_count = 0
                for ignore_selector in ignore_selectors:
                    elements_to_remove = content_soup.select(ignore_selector)
                    for element in elements_to_remove:
                        element.decompose()
                        removed_count += 1
                if removed_count > 0:
                    logger.info(f"Removed {removed_count} element(s) using ignore selectors")

            # Convert to desired format
            if output_format == "markdown":
                # Convert HTML to Markdown
                content = md(
                    str(content_soup),
                    heading_style="ATX",  # Use # style headings
                    bullets="-",  # Use - for unordered lists
                    strong_em_symbol="**",  # Use ** for bold
                    strip=['script', 'style', 'table', 'thead', 'tbody', 'tr', 'td', 'th']  # Remove tables and their elements
                )
                # Clean up extra whitespace while improving readability
                lines = content.split('\n')
                cleaned_lines = []
                prev_empty = False
                empty_count = 0

                for i, line in enumerate(lines):
                    line = line.rstrip()
                    is_empty = len(line) == 0

                    # Allow up to 2 consecutive empty lines
                    if is_empty:
                        empty_count += 1
                        if empty_count <= 2:
                            cleaned_lines.append(line)
                    else:
                        empty_count = 0
                        cleaned_lines.append(line)

                        # Add extra spacing after headings for readability
                        if line.startswith('#'):
                            cleaned_lines.append('')
                        # Add spacing after links that end sentences (likely article titles)
                        elif line.endswith(')') and '[' in line and '](' in line:
                            # Check if next line is not empty and doesn't start with - or #
                            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith(('-', '#', '*')):
                                cleaned_lines.append('')

                    prev_empty = is_empty

                content = '\n'.join(cleaned_lines).strip()

                # Add paragraph breaks between long text blocks
                # Split content that's too long without breaks
                paragraphs = content.split('\n\n')
                formatted_paragraphs = []
                for para in paragraphs:
                    # Split on double spaces which often separate articles/sections in newsletters
                    if '  ' in para and len(para) > 300:
                        # Split on patterns like "Author  [Title" or "Text  [Link"
                        import re
                        # Replace "  [" with "\n\n[" to separate articles
                        para = re.sub(r'  +\[', '\n\n[', para)
                        # Replace "Author  Text" patterns (word followed by double space and capital letter)
                        para = re.sub(r'([a-z])  +([A-Z🎯📄🛠💻🔧])', r'\1\n\n\2', para)
                        # Split on emoji section markers
                        para = re.sub(r'  +(📰|📢|🛠|💻|🔧)', r'\n\n\1', para)

                    # If still very long, try sentence splitting
                    if len(para) > 500 and '. ' in para and para.count('.') > 3:
                        sentences = para.split('.  ')
                        formatted_paragraphs.append('\n\n'.join(sentences))
                    else:
                        formatted_paragraphs.append(para)
                content = '\n\n'.join(formatted_paragraphs)
            else:
                # Extract plain text
                content = content_soup.get_text(separator='\n', strip=True)
                # Clean up multiple newlines
                content = '\n'.join(
                    line for line in content.split('\n')
                    if line.strip()
                )

            result = {
                'url': url,
                'title': title_text,
                'content': content,
                'raw_html': str(content_soup),
                'format': output_format,
                'success': True
            }

            logger.info(f"Successfully fetched content from {url}")
            logger.info(f"Content length: {len(content)} characters")
            logger.info(f"Output format: {output_format}")

            return result

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            return {
                'url': url,
                'title': '',
                'content': '',
                'raw_html': '',
                'success': False,
                'error': str(e)
            }

    def fetch_multiple(self, sources: list) -> list:
        """
        Fetch content from multiple sources.

        Args:
            sources: List of source dictionaries with 'url' or 'list_page' and optional 'selector'

        Returns:
            List of content dictionaries
        """
        results = []

        for source in sources:
            if not source.get('enabled', True):
                logger.info(f"Skipping disabled source: {source.get('name', 'unknown')}")
                continue

            source_name = source.get('name', 'unknown')

            # Determine the target URL
            target_url = None

            # Check if this is a two-step fetch (list page)
            if 'list_page' in source:
                list_config = source['list_page']
                list_url = list_config.get('url')
                link_selector = list_config.get('link_selector')
                link_index = list_config.get('link_index', 0)

                if not list_url or not link_selector:
                    logger.error(f"Invalid list_page config for {source_name}: missing url or link_selector")
                    results.append({
                        'url': '',
                        'title': '',
                        'content': '',
                        'raw_html': '',
                        'source_name': source_name,
                        'frequency': source.get('frequency', 'unknown'),
                        'success': False,
                        'error': 'Invalid list_page configuration'
                    })
                    continue

                # Fetch the target URL from the list page
                target_url = self.fetch_link_from_list(
                    list_url=list_url,
                    link_selector=link_selector,
                    link_index=link_index
                )

                if not target_url:
                    logger.error(f"Could not extract link from list page for {source_name}")
                    results.append({
                        'url': list_url,
                        'title': '',
                        'content': '',
                        'raw_html': '',
                        'source_name': source_name,
                        'frequency': source.get('frequency', 'unknown'),
                        'success': False,
                        'error': 'Could not extract link from list page'
                    })
                    continue
            elif 'url' in source:
                # Direct URL (original behavior)
                target_url = source['url']
            else:
                logger.error(f"Source {source_name} has neither 'url' nor 'list_page'")
                results.append({
                    'url': '',
                    'title': '',
                    'content': '',
                    'raw_html': '',
                    'source_name': source_name,
                    'frequency': source.get('frequency', 'unknown'),
                    'success': False,
                    'error': 'No url or list_page specified'
                })
                continue

            # Fetch the content from the target URL
            result = self.fetch_content(
                url=target_url,
                selector=source.get('selector'),
                ignore_selectors=source.get('ignore_selectors'),
                output_format=source.get('output_format', 'markdown')
            )
            result['source_name'] = source_name
            result['frequency'] = source.get('frequency', 'unknown')
            results.append(result)

        return results

    def close(self):
        """Close the session."""
        self.session.close()
