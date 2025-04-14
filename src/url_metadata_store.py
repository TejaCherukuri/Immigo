
import sqlite3
from utils.logger import logging

DB_FILE = "db/scraper_metadata.db"

class SQLiteMetadataStore:
    """Handles metadata storage for tracking webpage updates using SQLite."""

    def __init__(self, db_file=DB_FILE):
        """
        Initializes the SQLite metadata store.

        Args:
            db_file (str): Path to the SQLite database file.
        """
        self.db_file = db_file
        self._setup_database()

    def _setup_database(self):
        """
        Creates the necessary database table if it does not exist.
        This table stores URL metadata, including last modified timestamps, content hashes, and ETags.
        """
        logging.info("Setting up SQLite metadata database")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS web_pages (
                url TEXT PRIMARY KEY,
                last_modified TEXT,
                content_hash TEXT,
                etag TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_metadata(self, url):
        """
        Retrieves metadata (last modified timestamp, content hash, and ETag) for a given URL.

        Args:
            url (str): The webpage URL.

        Returns:
            tuple: (last_modified, content_hash, etag) or None if the URL is not found.
        """
        logging.info(f"Fetching metadata for {url}")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT last_modified, content_hash, etag FROM web_pages WHERE url = ?", (url,))
        result = cursor.fetchone()
        conn.close()
        return result  # Returns (last_modified, content_hash, etag) or None

    def update_metadata(self, url, last_modified, content_hash, etag):
        """
        Updates or inserts metadata for a given URL.

        Args:
            url (str): The webpage URL.
            last_modified (str): The last modified timestamp of the page.
            content_hash (str): The hash of the page content for change detection.
            etag (str): The ETag value for tracking changes.
        """
        logging.info(f"Updating metadata for {url}")
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO web_pages (url, last_modified, content_hash, etag)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET 
                last_modified=excluded.last_modified, 
                content_hash=excluded.content_hash,
                etag=excluded.etag
        """, (url, last_modified, content_hash, etag))
        conn.commit()
        conn.close()
