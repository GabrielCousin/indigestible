"""
Module for fetching and parsing HTML content from newsletter sources.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
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

    def fetch_content(
        self,
        url: str,
        selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch HTML content from a URL and optionally filter by CSS selector.

        Args:
            url: The URL to fetch
            selector: Optional CSS selector to filter content

        Returns:
            Dictionary with 'url', 'title', 'content', and 'raw_html'

        Raises:
            requests.RequestException: If the request fails
        """
        logger.info(f"Fetching content from: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

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

            # Extract text content
            text_content = content_soup.get_text(separator='\n', strip=True)

            # Clean up multiple newlines
            text_content = '\n'.join(
                line for line in text_content.split('\n')
                if line.strip()
            )

            result = {
                'url': url,
                'title': title_text,
                'content': text_content,
                'raw_html': str(content_soup),
                'success': True
            }

            logger.info(f"Successfully fetched content from {url}")
            logger.info(f"Content length: {len(text_content)} characters")

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
            sources: List of source dictionaries with 'url' and optional 'selector'

        Returns:
            List of content dictionaries
        """
        results = []

        for source in sources:
            if not source.get('enabled', True):
                logger.info(f"Skipping disabled source: {source.get('name', source['url'])}")
                continue

            result = self.fetch_content(
                url=source['url'],
                selector=source.get('selector')
            )
            result['source_name'] = source.get('name', source['url'])
            result['frequency'] = source.get('frequency', 'unknown')
            results.append(result)

        return results

    def close(self):
        """Close the session."""
        self.session.close()
