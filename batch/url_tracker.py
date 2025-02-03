import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from typing import List, Set

class URLTracker:
    def __init__(self, base_url: str, page_urls: List[str], file_path: str, new_file_path: str, valid_url_prefixes: Set[str] = None):
        """
        Initializes the URLTracker class with necessary parameters.
        
        :param base_url: The base URL to resolve relative links
        :param page_urls: List of URLs to track for new links
        :param file_path: Path to the file storing previously found URLs
        :param new_file_path: Path to the file for appending new URLs
        """
        self.base_url = base_url
        self.page_urls = page_urls
        self.file_path = file_path
        self.new_file_path = new_file_path
        self.valid_url_prefixes = valid_url_prefixes or self.get_default_valid_url_prefixes()
        self.setup_logging()

    def setup_logging(self):
        """Sets up logging configuration."""
        os.makedirs("logs/", exist_ok=True)
        logging.basicConfig(
            filename=os.path.join("logs", 'url_tracker.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.info("URL Tracker initialized.")

    def get_default_valid_url_prefixes(self) -> Set[str]:
        """Returns a set of valid URL prefixes for filtering links."""
        return {
            "/content/travel/en/News/visas-news/",
            "/content/travel/en/legal/visa-law0/visa-bulletin/",
            "/news/news-releases/",
            "/news/alerts/",
            "/newsroom/all-news/",
            "/newsroom/stakeholder-messages/",
            "/newsroom/news-releases/",
            "/newsroom/alerts/"
        }

    def get_urls_from_page(self, url: str) -> Set[str]:
        """Fetches and extracts URLs from the provided webpage."""
        try:
            # Send an HTTP request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error if the HTTP request failed

            # Parse the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all anchor tags and extract the href attribute
            links = soup.find_all('a', href=True)

            # Filter and collect only valid URLs under the 'visas-news' or 'visa-bulletin' paths
            urls = set()  # Use a set to avoid duplicates
            for link in links:
                href = link['href']
                # Resolve the relative URL to a full URL
                full_url = urljoin(self.base_url, href)
                if any(full_url.startswith(self.base_url + prefix) for prefix in self.valid_url_prefixes):
                    urls.add(full_url)

            return urls

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching the page {url}: {e}")
            return set()

    def track_new_urls(self):
        """Tracks new URLs and stores them to compare against previous ones."""
        # To accumulate all new URLs
        all_new_urls = set()

        for page_url in self.page_urls:
            logging.info(f"Processing URL: {page_url}")
            # Get the current URLs from the page
            current_urls = self.get_urls_from_page(page_url)

            # Try to read previously stored URLs
            old_urls = self.read_old_urls()

            # Find new URLs that were not previously tracked
            new_urls = current_urls - old_urls
            all_new_urls.update(new_urls)

            if new_urls:
                logging.info(f"New URLs found on {page_url}:")
                for url in new_urls:
                    logging.info(url)

        # If there are new URLs to store, update the file
        if all_new_urls:
            self.store_new_urls(all_new_urls)
        else:
            logging.info("No new URLs found.")

    def read_old_urls(self) -> Set[str]:
        """Reads the previously stored URLs from the file."""
        try:
            with open(self.file_path, 'r') as file:
                old_urls = set(file.read().splitlines())
        except FileNotFoundError:
            old_urls = set()  # If the file doesn't exist, start with an empty set
        return old_urls

    def store_new_urls(self, new_urls: Set[str]):
        """Stores new URLs to the file."""
        try:
            with open(self.new_file_path, 'a') as file:  # Append to the file
                file.write("\n".join(new_urls) + "\n")
            logging.info(f"Stored new URLs in {self.new_file_path}")
        except Exception as e:
            logging.error(f"Error writing new URLs to file: {e}")


class URLTrackerFactory:
    def __init__(self):
        self.base_url = ""
        self.page_urls = []
        self.file_path = ""
        self.new_file_path = ""
        self.root_dir = os.path.dirname(os.path.dirname(__file__))

    def create_dos_tracker(self) -> URLTracker:
        """Creates a URLTracker for DOS with its specific configuration."""
        self.base_url = "https://travel.state.gov"
        self.page_urls = [
            "https://travel.state.gov/content/travel/en/News/visas-news.html",
            "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"
        ]
        self.file_path = os.path.join(self.root_dir, "resources/dos.txt")
        self.new_file_path = os.path.join(self.root_dir, "resources/dos_untracked.txt")
        return URLTracker(self.base_url, self.page_urls, self.file_path, self.new_file_path)

    def create_uscis_tracker(self) -> URLTracker:
        """Creates a URLTracker for USCIS with its specific configuration."""
        self.base_url = "https://www.uscis.gov"
        self.page_urls = [
            "https://www.uscis.gov/news/alerts",
            "https://www.uscis.gov/news/news-releases",
            "https://www.uscis.gov/newsroom/all-news",
            "https://www.uscis.gov/newsroom/stakeholder-messages"
        ]
        self.file_path = os.path.join(self.root_dir, "resources/uscis.txt")
        self.new_file_path = os.path.join(self.root_dir, "resources/uscis_untracked.txt")
        return URLTracker(self.base_url, self.page_urls, self.file_path, self.new_file_path)


# Main function to start the tracking process
if __name__ == "__main__":
    # Initialize the factory
    factory = URLTrackerFactory()

    # Create and track new URLs for DOS
    dos_tracker = factory.create_dos_tracker()
    dos_tracker.track_new_urls()

    # Create and track new URLs for USCIS
    uscis_tracker = factory.create_uscis_tracker()
    uscis_tracker.track_new_urls()
   