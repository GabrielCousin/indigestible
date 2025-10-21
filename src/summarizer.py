"""
Module for AI-powered content summarization and grouping.
"""

import os
from pathlib import Path
from typing import List, Dict
import logging
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ContentSummarizer:
    """Summarizes and groups newsletter content using OpenAI."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the ContentSummarizer.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY or OPEN_AI_API_KEY env var)
            model: OpenAI model to use (defaults to gpt-4o-mini)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY') or os.getenv('OPEN_AI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or OPEN_AI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.model = model or "gpt-4o-mini"

    def read_markdown_files(self, directory: str = "output") -> List[Dict[str, str]]:
        """
        Read all markdown files from the output directory.

        Args:
            directory: Directory containing markdown files

        Returns:
            List of dictionaries with filename and content
        """
        output_dir = Path(directory)
        if not output_dir.exists():
            logger.error(f"Output directory not found: {directory}")
            return []

        markdown_files = []
        for md_file in output_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    markdown_files.append({
                        'filename': md_file.name,
                        'content': content
                    })
                logger.info(f"Read {md_file.name}: {len(content)} characters")
            except Exception as e:
                logger.error(f"Error reading {md_file}: {str(e)}")

        return markdown_files

    def create_summary_prompt(self, contents: List[Dict[str, str]]) -> str:
        """
        Create a comprehensive prompt for OpenAI summarization.

        Args:
            contents: List of markdown file contents

        Returns:
            Formatted prompt string
        """
        # Combine all content
        combined_content = "\n\n---\n\n".join([
            f"# Source: {item['filename']}\n\n{item['content']}"
            for item in contents
        ])

        prompt = f"""You are a technical newsletter curator. Analyze the following web development newsletter content and create a comprehensive summary.

# Instructions:

1. **Group content into these sections ONLY:**
   - ## React
   - ## JavaScript
   - ## Updates
   - ## New Tools
   - ## Design
   - ## Misc

2. **Filtering rules:**
   - IGNORE anything related to React Native or mobile development
   - IGNORE framework-specific content EXCEPT React and Node.js
   - REMOVE all sponsor content and advertisements
   - IGNORE job postings and classifieds

3. **Link handling:**
   - Extract and use FINAL destination URLs (follow redirects in your understanding)
   - Remove tracking parameters from URLs when possible
   - Format: [Article Title](clean-url)

4. **Formatting:**
   - Use markdown formatting
   - Each item should be: **[Title](url)** — Brief description
   - Group related items together
   - Order by importance/relevance within each section
   - Don't mention source names or newsletters

5. **Content focus:**
   - Focus on tutorials, libraries, tools, and updates
   - Include version numbers for releases
   - Highlight breaking changes or major features
   - Keep descriptions concise (1-2 sentences max)

# Newsletter Content:

{combined_content}

# Output:

Create a well-organized markdown summary following the structure above."""

        return prompt

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call OpenAI API.

        Args:
            system_prompt: System message/context
            user_prompt: User message/prompt

        Returns:
            Response content from OpenAI
        """
        logger.info(f"Calling OpenAI API with model: {self.model}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Build request parameters based on model capabilities
        kwargs = {
            "model": self.model,
            "messages": messages,
        }

        # GPT-5 and o1 models have different parameter requirements
        if self.model.startswith("gpt-5") or self.model.startswith("o1"):
            # GPT-5/o1 use max_completion_tokens and fixed temperature
            # Use a larger limit for GPT-5 models (they have bigger context windows)
            kwargs["max_completion_tokens"] = 16000
            # Note: temperature is not configurable for these models (defaults to 1)
        else:
            # Older models use max_tokens and support temperature
            kwargs["max_tokens"] = 4000
            kwargs["temperature"] = 0.7

        response = self.client.chat.completions.create(**kwargs)

        # Check if we got a valid response
        if not response.choices:
            raise ValueError(f"No choices returned from {self.model}")

        content = response.choices[0].message.content

        # Check if content is empty
        if not content:
            finish_reason = response.choices[0].finish_reason
            logger.warning(f"Empty response from {self.model}. Finish reason: {finish_reason}")

            # Check if there's a refusal
            if hasattr(response.choices[0].message, 'refusal') and response.choices[0].message.refusal:
                raise ValueError(f"Model refused to respond: {response.choices[0].message.refusal}")

            raise ValueError(f"Empty response from {self.model}. Finish reason: {finish_reason}")

        return content

    def summarize(self, directory: str = "output") -> str:
        """
        Read all markdown files and create an AI-powered summary.

        Args:
            directory: Directory containing markdown files

        Returns:
            Markdown-formatted summary
        """
        logger.info("Reading markdown files...")
        markdown_files = self.read_markdown_files(directory)

        if not markdown_files:
            logger.error("No markdown files found")
            return ""

        logger.info(f"Processing {len(markdown_files)} files")

        # Create prompt
        prompt = self.create_summary_prompt(markdown_files)
        logger.info(f"Prompt length: {len(prompt)} characters")

        # Prepare system and user prompts
        system_prompt = "You are a technical content curator specializing in web development newsletters. You excel at extracting key information, organizing content logically, and presenting it in a clear, concise format."

        # Call OpenAI API
        try:
            summary = self._call_openai(system_prompt, prompt)
            logger.info(f"Generated summary: {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    def save_summary(self, summary: str, output_file: str = "output/SUMMARY.md"):
        """
        Save the summary to a file.

        Args:
            summary: The markdown summary
            output_file: Path to save the summary
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        logger.info(f"Summary saved to: {output_file}")
