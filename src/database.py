import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain_core.vectorstores.base import VectorStoreRetriever

class ChromaDBHandler:
    """Handles ChromaDB operations using Singleton Pattern."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = chromadb.PersistentClient(path="chroma_db_test")

            cls._instance.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

            cls._instance.collection = Chroma(
                collection_name="scraped_docs_test",
                embedding_function=cls._instance.embeddings,
                client=cls._instance.client,
            )
        return cls._instance

    def add_documents(self, documents: list[Document]):
        """Adds documents to the vector store."""
        self.collection.add_documents(documents)

    def search(self, query: str, k: 5):
        """Performs a search on the vector store."""
        return self.collection.similarity_search(query, k=k)
    
    def get_retriever(self) -> VectorStoreRetriever:
        """Returns a retriever for LangChain."""
        return self.collection.as_retriever(search_kwargs={"k": 5})
