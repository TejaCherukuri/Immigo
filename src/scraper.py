from abc import ABC, abstractmethod
import requests
import fitz
from langchain.schema import Document
from langchain_community.document_loaders import WebBaseLoader
import os

os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class Scraper(ABC):
    """Abstract Class for Scrapers"""

    @abstractmethod
    def scrape(self, url: str) -> list[Document]:
        """Method to be implemented by subclasses for scraping data."""
        pass

class PDFScraper(Scraper):
    """Scraper for extracting text from PDFs."""

    def scrape(self, url: str) -> list[Document]:
        """Fetches a PDF from the URL and extracts text as LangChain Document objects."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTP errors if any

            # Iterate through the headers
            for header, value in response.headers.items():
                print(f"{header}: {value}")
            
            pdf = fitz.open(stream=response.content, filetype='pdf')
            documents = [
                Document(
                    page_content=page.get_text(),
                    metadata={"source": url, "page": page_num + 1}
                )
                for page_num, page in enumerate(pdf)
            ]
            return documents

        except requests.exceptions.RequestException as e:
            print(f"Error fetching PDF from {url}: {e}")
            return []
        except Exception as e:
            print(f"Error processing PDF from {url}: {e}")
            return []

class WebScraper(Scraper):
    """Scraper for extracting text from webpages."""

    def scrape(self, url: str) -> list[Document]:
        """Fetches and parses a webpage using LangChain's WebBaseLoader."""
        try:
            loader = WebBaseLoader([url])
            return loader.load()
        except Exception as e:
            print(f"Error fetching webpage from {url}: {e}")
            return []
    
class ScraperFactory:
    """Factory class to get the appropriate scraper based on the file type."""

    @classmethod
    def get_scraper(cls, file_type: str) -> Scraper:
        """Returns the appropriate scraper based on file type."""
        scrapers = {
            "pdf": PDFScraper(),
            "web": WebScraper(),
        }
        return scrapers.get(file_type, WebScraper())  # Default to WebScraper

    



