from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any
import os
from utils.logger import get_logger

logger = get_logger(__name__)

class PineconeClient:
    """
    Initializes Pinecone and stores vectors from JSON input.
    """

    def __init__(
        self,
        api_key: str | None = None,
        environment: str | None = None,
        index_name: str | None = None,
        dimension: int | None = 1536,
        metric: str | None = "cosine",
    ):
        """
        :param api_key: Pinecone API key
        :param environment: Pinecone environment
        :param index_name: Name of the index
        :param dimension: Embedding vector size
        :param metric: cosine | euclidean | dotproduct
        """
        pinecone = Pinecone(
            api_key=api_key or os.getenv("PINECONE_API_KEY")
        )

        self.index_name = index_name or os.getenv("PINECONE_INDEX_NAME")
        self.dimension = dimension or os.getenv("PINECONE_DIMENSION")
        self.metric = metric or os.getenv("PINECONE_METRIC")
        indexes = [i.name for i in pinecone.list_indexes()]
        if self.index_name not in indexes:
            pinecone.create_index(
                name=self.index_name,
                dimension=self.dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                  cloud="aws",
                  region="us-east-1",)
            )

        self.index = pinecone.Index(self.index_name)
        logger.info(f"Pinecone Client initialized for index: {self.index_name}")

    def upsert_from_json(
        self,
        records: List[Dict[str, Any]],
        batch_size: int = 10,
    ):
        """
        Upserts vectors into Pinecone from JSON records.

        Expected format:
        {
            "id": str,
            "embedding": List[float],
            "metadata": Dict[str, Any]
        }
        """
        batch = []
        try:
          for record in records:
              vector_id = record["doc_id"]
              embedding = record["embedding"]
              metadata = record.get("metadata", {})

              batch.append((vector_id, embedding, metadata))

              if len(batch) >= batch_size:
                  self.index.upsert(vectors=batch)
                  batch = []

          if batch:
              self.index.upsert(vectors=batch)
          logger.info(f"Successfully upserted {len(records)} records into Pinecone")
        except Exception as e:
          logger.error(f"Failed to upsert vectors to Pinecone: {str(e)}")
          raise RuntimeError(f"Failed to upsert vectors to Pinecone: {e}")

    def retrieve(
        self,
        vector: List[float],
        top_k: int = 5,
        include_metadata: bool = True,
    ):
        """
        Query Pinecone index.
        """
        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=include_metadata,
        )