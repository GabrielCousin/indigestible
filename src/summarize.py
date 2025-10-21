"""
Main script for summarizing newsletter content.
"""

import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.summarizer import ContentSummarizer
from src.config import Config


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

    logger.info("Starting newsletter summarization")

    try:
        # Load configuration
        config = Config()
        ai_config = config.ai_config

        # Get model setting
        model = ai_config.get('model')

        if model:
            logger.info(f"Using model: {model}")

        # Initialize summarizer
        summarizer = ContentSummarizer(model=model)

        # Generate summary
        summary = summarizer.summarize()

        if summary:
            # Save summary
            summarizer.save_summary(summary)

            # Print summary preview
            logger.info("\n" + "="*80)
            logger.info("SUMMARY PREVIEW")
            logger.info("="*80)
            print(summary[:1000] + "..." if len(summary) > 1000 else summary)
            logger.info("\n" + "="*80)
            logger.info("Full summary saved to: output/SUMMARY.md")
            logger.info("="*80)
        else:
            logger.error("No summary generated")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
