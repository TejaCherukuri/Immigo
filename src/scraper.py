import os
from io import BytesIO
from abc import ABC, abstractmethod
import requests
import fitz
import asyncio
import pymupdf4llm
from langchain_core.documents import Document
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from utils.logger import logging


os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class Scraper(ABC):
    """Abstract Class for Scrapers"""

    @abstractmethod
    def scrape(self, url: str) -> str:
        """Method to be implemented by subclasses for scraping data."""
        pass

class PDFScraper(Scraper):
    """Scraper for extracting text from PDFs."""

    def scrape(self, url: str) -> str:
        """Fetches a PDF from the URL and extracts text as LangChain Document objects."""
        try:
            # Fetch the PDF content
            response = requests.get(url)
            response.raise_for_status()
            pdf_bytes = BytesIO(response.content)  # Convert to a byte stream

            # Open the PDF directly from memory
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            md_text = pymupdf4llm.to_markdown(pdf_document)

            return md_text
        except Exception as e:
            logging.info(f"Failed to process PDF {url}: {e}")
            return ""

class WebScraper(Scraper):
    """Scraper for extracting text from webpages."""

    async def fetch_web_content(self, web_url: str) -> str:
        """Asynchronously fetches web content using AsyncWebCrawler."""

        run_config = CrawlerRunConfig(
                excluded_tags=["header", "footer", "nav", "aside", "script", "style"],  # Remove entire tag blocks
                cache_mode=CacheMode.DISABLED,
                excluded_selector="#header, #footer, #back-to-top, #sm-share, #resources, #appendices, #updates, #feedback-message, .reviewed-date"
            )
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=web_url, config=run_config)
                return result.markdown
            
        except Exception as e:
            logging.info(f"Error fetching {web_url}: {e}")
            return ""

    def scrape(self, url: str) -> str:
        """Fetches and parses a webpage using LangChain's WebBaseLoader."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.fetch_web_content(url))
        except Exception as e:
            logging.info(f"Error fetching webpage from {url}: {e}")
            return ""
        
class TextScraper(Scraper):
    """Scraper for extracting text from plain text files (.txt)."""

    def scrape(self, url: str) -> str:
        """Fetches text content from a .txt file or plain text URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logging.info(f"Failed to fetch text from {url}: {e}")
            return ""
        
    
class ScraperFactory:
    """Factory class to get the appropriate scraper based on the file type."""

    @classmethod
    def get_scraper(cls, file_type: str) -> Scraper:
        """Returns the appropriate scraper based on file type."""
        scrapers = {
            "pdf": PDFScraper(),
            "web": WebScraper(),
            "txt": TextScraper()
        }
        return scrapers.get(file_type, WebScraper())  # Default to WebScraper

    



