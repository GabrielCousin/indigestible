"""
Main script for the newsletter aggregator.
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.fetcher import ContentFetcher


def setup_logging(level: str = "INFO"):
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main execution function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting newsletter aggregator")

    try:
        # Load configuration
        config = Config()
        logger.info(f"Found {len(config.sources)} source(s) in configuration")

        # Get enabled sources
        enabled_sources = config.get_enabled_sources()
        logger.info(f"Processing {len(enabled_sources)} enabled source(s)")

        if not enabled_sources:
            logger.warning("No enabled sources found in configuration")
            return

        # Fetch content from all sources
        fetcher = ContentFetcher()

        try:
            results = fetcher.fetch_multiple(enabled_sources)

            # Display results
            logger.info("\n" + "="*80)
            logger.info("RESULTS SUMMARY")
            logger.info("="*80)

            for result in results:
                logger.info(f"\nSource: {result['source_name']}")
                logger.info(f"URL: {result['url']}")
                logger.info(f"Frequency: {result['frequency']}")
                logger.info(f"Success: {result['success']}")

                if result['success']:
                    logger.info(f"Title: {result['title']}")
                    logger.info(f"Format: {result.get('format', 'text')}")
                    logger.info(f"Content length: {len(result['content'])} characters")
                    logger.info(f"\nContent preview (first 500 chars):")
                    logger.info("-" * 80)
                    logger.info(result['content'][:500] + "...")
                    logger.info("-" * 80)
                else:
                    logger.error(f"Error: {result.get('error', 'Unknown error')}")

            # Save results to file for inspection
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)

            for result in results:
                if result['success']:
                    source_name = result['source_name'].replace(' ', '_').lower()
                    output_format = result.get('format', 'text')
                    file_extension = 'md' if output_format == 'markdown' else 'txt'
                    output_file = output_dir / f"{source_name}_content.{file_extension}"

                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"Source: {result['source_name']}\n")
                        f.write(f"URL: {result['url']}\n")
                        f.write(f"Title: {result['title']}\n")
                        f.write(f"Frequency: {result['frequency']}\n")
                        f.write(f"Format: {output_format}\n")
                        f.write("\n" + "="*80 + "\n")
                        f.write("CONTENT\n")
                        f.write("="*80 + "\n\n")
                        f.write(result['content'])

                    logger.info(f"Saved content to: {output_file}")

            logger.info("\n" + "="*80)
            logger.info(f"Successfully processed {len([r for r in results if r['success']])} source(s)")
            logger.info("="*80)

        finally:
            fetcher.close()

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
