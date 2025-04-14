import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from utils.logger import logging
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient,  models
from qdrant_client.http.models import VectorParams, Distance, SparseVectorParams

class QdrantDBHandler:
    """
    Handles storing and retrieving chunked documents using Qdrant with flexible retrieval methods.
    """
    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of QdrantDBHandler is created."""

        if cls._instance is None:
            cls._instance = super(QdrantDBHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self, collection_name="qdrant_col", qdrant_host="localhost", qdrant_port=6333):
        """
        Initializes the Qdrant vector store.

        :param collection_name: Name of the Qdrant collection.
        :param qdrant_host: Host where Qdrant is running.
        :param qdrant_port: Port for Qdrant.
        """

        if hasattr(self, "initialized"):  # Prevents re-initialization
            return

        self.collection_name = collection_name
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

        # Check if collection exists
        existing_collections = [c.name for c in self.client.get_collections().collections]
        if self.collection_name not in existing_collections:
            logging.info(f"Creating new collection: {self.collection_name}")

            # Create a collection with both dense and sparse vectors
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={"dense": VectorParams(size=384, distance=Distance.COSINE)},
                sparse_vectors_config={
                    "sparse": SparseVectorParams(index=models.SparseIndexParams(on_disk=False))
                },
            )
        else:
            logging.info(f"Collection '{self.collection_name}' already exists. Skipping creation.")

        # Use Hugging Face Sentence Transformers Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Initialize Qdrant VectorStore
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            sparse_embedding=self.sparse_embeddings,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

        self.initialized = True  # Mark instance as initialized


    def add_documents(self, documents):
        """
        Stores processed documents into Qdrant.

        :param documents: List of LangChain Document objects to store.
        """
        self.vector_store.add_documents(documents)
        logging.info(f"Stored {len(documents)} documents in Qdrant.")

    def search(self, query_text, top_k=5):
        """
        Searches for the most relevant documents using the chosen method.

        :param query_text: Input text to find similar chunks.
        :param top_k: Number of top results to return.
        :return: List of matching documents with metadata.
        """

        results = self.vector_store.similarity_search_with_score(query_text, k=top_k)

        return results
