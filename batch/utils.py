
import requests
from utils.logger import logging
from src.url_metadata_store import SQLiteMetadataStore
from src.scraper import ScraperFactory
import hashlib

def should_scrape(url):

    """Determines if a webpage should be re-scraped based on Last-Modified, ETag, or content hash."""
    response = requests.head(url)  # Fetch headers only
    last_modified = response.headers.get("Last-Modified")
    etag = response.headers.get("ETag")  # Fetch ETag header

    datastore = SQLiteMetadataStore()
    db_entry = datastore.get_metadata(url)  # Retrieve last-modified, hash from DB

    if last_modified:
        if db_entry and db_entry[0] == last_modified:
            return False, last_modified, None, etag  # No need to scrape
        logging.info(f"Update detected for {url} (Last-Modified changed). Scraping...")
        return True, last_modified, None, etag

    if etag:
        if db_entry and db_entry[2] == etag:  # Check if ETag matches stored value
            return False, None, None, etag  # No need to scrape
        logging.info(f"Update detected for {url} (ETag changed). Scraping...")
        return True, None, None, etag


    # Get the Scraper
    text = "pdf" if url.endswith(".pdf") else "web"
    scraper = ScraperFactory.get_scraper(text)
    content = scraper.scrape(url)
    
    # If neither Last-Modified nor ETag is available, fall back to content hashing
    new_hash = compute_hash(content)

    if db_entry and db_entry[1] == new_hash:
        return False, None, new_hash, etag  # No need to scrape

    logging.info(f"Update detected for {url} (Content hash changed). Scraping...")
    return True, None, new_hash, etag

def compute_hash(content):
    logging.info("computing hash")
    """Computes SHA256 hash of the content for change detection."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()