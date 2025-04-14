from utils.logger import logging
from datetime import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import hashlib
from utils.utils import preprocess_text

class Chunker:
    """
    A class to process, chunk, and store markdown text extracted from webpages.
    """

    def __init__(self, db_handler):
        """
        Initializes the Chunker with a database handler.
        
        :param db_handler: An instance of the database handler (e.g., ChromaDBHandler)
        """
        self.db_handler = db_handler

    def generate_id(self, text):
        # Use hash of content as ID (you can customize this logic)
        return hashlib.md5(text.encode()).hexdigest()

    def write_markdown_data_to_file(self, text, filename="chunked_data.md"):
        """
        Writes the given text to a Markdown file.

        :param text: The content to write into the Markdown file.
        :param filename: The name of the Markdown file to write to (default is 'output.md').
        """
        with open(filename, "a") as file:
            file.write("\n" + "=" * 100 + "\n" + "=" * 100 + "\n" + "=" * 100 + "\n")  # Section separator
            file.write(text)

    def process_and_store_markdown(self, url, text):
        """
        Processes markdown text by chunking, processing, and storing it.
        
        :param url: Source URL of the text
        :param text: Extracted markdown text
        """
        text = preprocess_text(text)

        self.write_markdown_data_to_file(text)

        # Step 1: Chunking the text
        chunks = self.chunk_text(text)

        # Step 2: Write chunked data to a file (for visualization/debugging)
        self.write_chunked_data_to_file(url, chunks)

        # Step 3: Process the chunks into structured documents
        documents = self.process_chunks(chunks, url)

        # Step 4: Store the processed chunks
        self.store_chunks(documents)

    def chunk_text(self, text):
        """
        Splits the given text into smaller chunks using RecursiveCharacterTextSplitter.
        
        :param text: Raw text to be chunked
        :return: List of text chunks
        """
        logging.info("Chunking text...")
        splitter = RecursiveCharacterTextSplitter(separators=["\n\n"], chunk_size=500, chunk_overlap=50)
        return splitter.split_text(text)

    def process_chunks(self, chunks, url):
        """
        Converts text chunks into structured Document objects with metadata.
        
        :param chunks: List of chunked text
        :param url: Source URL of the document
        :return: List of Document objects
        """
        logging.info("Processing chunks...")
        documents = []
        total_length = sum(len(chunk) for chunk in chunks)

        for index, chunk in enumerate(chunks):
            doc_id = self.generate_id(chunk)
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": url,
                    "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "chunk_number": index + 1,
                    "chunk_size": len(chunk),
                    "text_length": total_length,
                }
            )
            doc.id = doc_id
            documents.append(doc)
        
        return documents

    def store_chunks(self, documents):
        """
        Stores the processed document chunks into the database.
        
        :param documents: List of Document objects to be stored
        """
        logging.info("Storing chunks in the database...")
        self.db_handler.add_documents(documents)

    def write_chunked_data_to_file(self, url, chunks, file_path="chunked_data.txt"):
        """
        Writes chunked data to a file for debugging or visualization.
        
        :param url: Source URL of the text
        :param chunks: List of text chunks
        :param file_path: File path to store the chunked data
        """
        with open(file_path, "a") as file:
            file.write(f"Chunks for URL: {url}\n")
            for index, chunk in enumerate(chunks):
                file.write(f"Chunk {index + 1}:\n")
                file.write(f"Content: {chunk}\n")  # Show first 300 characters
                file.write(f"Size: {len(chunk)} characters\n")
                file.write("-" * 50 + "\n")  # Separator line
            file.write("\n" + "=" * 100 + "\n" + "=" * 100 + "\n" + "=" * 100 + "\n")  # Section separator
