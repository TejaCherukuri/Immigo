from src.scraper import ScraperFactory
from utils import load_urls, clean_text
from src.database import ChromaDBHandler

def process_urls():
    """Fetches data from URLs and stores it in ChromaDB."""
    # urls = load_urls()
    urls = ['https://www.uscis.gov/forms/all-forms', 'https://www.uscis.gov/sites/default/files/document/legal-docs/2013-1231_OLF_Exemption_PM_Effective.pdf']
    chroma_db = ChromaDBHandler()

    for url in urls:
        file_type = "pdf" if url.endswith(".pdf") else "web"
        scraper = ScraperFactory.get_scraper(file_type)

        try:
            documents = scraper.scrape(url)

            for doc in documents:
                doc.page_content = clean_text(doc.page_content)
                print("===============")
                print(doc.page_content[:500])
            
            chroma_db.add_documents(documents)
            print(f"Successfully added {len(documents)} document(s) from {url}")
        except Exception as e:
            print(f"Failed to process {url}: {str(e)}")

if __name__ == "__main__":
    process_urls()
