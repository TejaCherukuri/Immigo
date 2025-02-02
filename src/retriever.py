from src.database import ChromaDBHandler

class RetrieverFactory:
    """Factory for creating retrievers."""
    
    @staticmethod
    def get_retriever():
        """Returns a retriever instance."""
        chroma_db = ChromaDBHandler()
        return chroma_db.get_retriever()
