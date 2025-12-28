from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional, Dict, Any
from ..config import get_settings
import logging
import re


logger = logging.getLogger(__name__)


class VectorStore:
    """
    Singleton class to manage Qdrant Cloud connection and operations.
    Supports versioned collections with aliasing for seamless upgrades.
    """
    _instance = None
    _client: Optional[QdrantClient] = None

    # Collection versioning configuration
    BASE_COLLECTION_NAME = "book_embeddings"
    CURRENT_VERSION = "v2"  # Cohere embed-english-v3.0 (1024 dims)
    VECTOR_DIMENSIONS = 1024  # Updated for Cohere embeddings

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def versioned_collection_name(self) -> str:
        """Get the versioned collection name."""
        return f"{self.BASE_COLLECTION_NAME}_{self.CURRENT_VERSION}"

    @property
    def active_collection_name(self) -> str:
        """
        Get the active collection name (alias or versioned name).
        Prefers alias if it exists, otherwise uses versioned name.
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # Check if alias exists
        try:
            aliases = self._client.get_collection_aliases(self.BASE_COLLECTION_NAME)
            if aliases and aliases.aliases:
                return self.BASE_COLLECTION_NAME
        except:
            pass

        return self.versioned_collection_name

    def initialize(self):
        """
        Initialize the Qdrant client connection.
        """
        settings = get_settings()
        self._client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False  # Using HTTP for better compatibility
        )

        # Ensure the collection exists
        self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        """
        Ensure the versioned collection exists with correct configuration.
        Sets up alias pointing to the current version.
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        collection_name = self.versioned_collection_name

        try:
            # Try to get collection info to see if it exists
            self._client.get_collection(collection_name)
            logger.info(f"Collection {collection_name} already exists")
        except:
            # Collection doesn't exist, create it
            logger.info(f"Creating versioned collection {collection_name}")
            self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=self.VECTOR_DIMENSIONS,  # Cohere embed-english-v3.0
                    distance=models.Distance.COSINE
                ),
                on_disk_payload=True  # For free tier memory constraints
            )
            logger.info(f"Collection {collection_name} created successfully")

        # Set up alias pointing to current version
        self._setup_alias()

    def _setup_alias(self):
        """
        Set up alias pointing to the current versioned collection.
        This allows querying via the base name while supporting version upgrades.
        """
        if self._client is None:
            return

        try:
            # Update alias to point to current version
            self._client.update_collection_aliases(
                change_aliases_operations=[
                    models.CreateAliasOperation(
                        create_alias=models.CreateAlias(
                            collection_name=self.versioned_collection_name,
                            alias_name=self.BASE_COLLECTION_NAME
                        )
                    )
                ]
            )
            logger.info(
                f"Alias '{self.BASE_COLLECTION_NAME}' now points to '{self.versioned_collection_name}'"
            )
        except Exception as e:
            # Alias may already exist or there may be other issues
            logger.warning(f"Could not set up alias (may already exist): {e}")

    def create_new_version(self, version: str) -> str:
        """
        Create a new versioned collection for migration purposes.

        Args:
            version: Version string (e.g., 'v3')

        Returns:
            The new collection name
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        new_collection_name = f"{self.BASE_COLLECTION_NAME}_{version}"

        try:
            self._client.get_collection(new_collection_name)
            logger.info(f"Version {version} collection already exists")
        except:
            logger.info(f"Creating new version collection: {new_collection_name}")
            self._client.create_collection(
                collection_name=new_collection_name,
                vectors_config=models.VectorParams(
                    size=self.VECTOR_DIMENSIONS,
                    distance=models.Distance.COSINE
                ),
                on_disk_payload=True
            )
            logger.info(f"Collection {new_collection_name} created successfully")

        return new_collection_name

    def switch_alias_to_version(self, version: str) -> None:
        """
        Switch the alias to point to a different version.
        Use this after successfully migrating data to a new version.

        Args:
            version: Version string to switch to (e.g., 'v3')
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        target_collection = f"{self.BASE_COLLECTION_NAME}_{version}"

        # Verify target collection exists
        try:
            self._client.get_collection(target_collection)
        except:
            raise ValueError(f"Collection {target_collection} does not exist")

        # Update alias
        self._client.update_collection_aliases(
            change_aliases_operations=[
                models.CreateAliasOperation(
                    create_alias=models.CreateAlias(
                        collection_name=target_collection,
                        alias_name=self.BASE_COLLECTION_NAME
                    )
                )
            ]
        )
        logger.info(f"Alias '{self.BASE_COLLECTION_NAME}' now points to '{target_collection}'")

    def list_versions(self) -> List[str]:
        """
        List all available collection versions.

        Returns:
            List of version strings
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        collections = self._client.get_collections().collections
        versions = []

        pattern = re.compile(f"^{self.BASE_COLLECTION_NAME}_(.+)$")
        for collection in collections:
            match = pattern.match(collection.name)
            if match:
                versions.append(match.group(1))

        return sorted(versions)

    @property
    def client(self) -> QdrantClient:
        """
        Get the Qdrant client.
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        return self._client

    async def search_embeddings(
        self,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        collection_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the vector store.

        Args:
            query_vector: The query embedding vector
            limit: Maximum number of results to return
            filters: Optional filters for the search
            collection_name: Optional collection name (uses alias by default)

        Returns:
            List of search results with id, score, and payload
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # Use alias (which points to current version) by default
        target_collection = collection_name or self.BASE_COLLECTION_NAME

        # Build filter if provided
        search_filter = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(
                    models.FieldCondition(
                        key=f"payload.{key}",
                        match=models.MatchValue(value=value)
                    )
                )
            if must_conditions:
                search_filter = models.Filter(must=must_conditions)

        # Use query_points (qdrant-client 1.16+)
        results = self._client.query_points(
            collection_name=target_collection,
            query=query_vector,
            limit=limit,
            query_filter=search_filter,
            with_payload=True
        )

        # Format results
        formatted_results = []
        for result in results.points:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })

        return formatted_results

    async def store_embedding(
        self,
        chunk_id: str,
        embedding: List[float],
        payload: Dict[str, Any],
        collection_name: Optional[str] = None
    ):
        """
        Store a single embedding in the vector store.

        Args:
            chunk_id: Unique identifier for the chunk
            embedding: The embedding vector
            payload: Metadata payload
            collection_name: Optional target collection (uses versioned by default for writes)
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # Write to versioned collection by default
        target_collection = collection_name or self.versioned_collection_name

        self._client.upsert(
            collection_name=target_collection,
            points=[
                models.PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

    async def batch_store_embeddings(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        payloads: List[Dict[str, Any]],
        collection_name: Optional[str] = None
    ):
        """
        Store multiple embeddings in the vector store.

        Args:
            chunk_ids: List of unique identifiers
            embeddings: List of embedding vectors
            payloads: List of metadata payloads
            collection_name: Optional target collection (uses versioned by default for writes)
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # Write to versioned collection by default
        target_collection = collection_name or self.versioned_collection_name

        points = []
        for chunk_id, embedding, payload in zip(chunk_ids, embeddings, payloads):
            points.append(
                models.PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload=payload
                )
            )

        self._client.upsert(
            collection_name=target_collection,
            points=points
        )

    async def delete_embedding(self, chunk_id: str, collection_name: Optional[str] = None):
        """
        Delete an embedding from the vector store.

        Args:
            chunk_id: The chunk ID to delete
            collection_name: Optional target collection (uses versioned by default)
        """
        if self._client is None:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")

        # Delete from versioned collection by default
        target_collection = collection_name or self.versioned_collection_name

        self._client.delete(
            collection_name=target_collection,
            points_selector=models.PointIdsList(
                points=[chunk_id]
            )
        )


# Global instance
vector_store = VectorStore()


def get_vector_store():
    """
    Get the vector store instance.
    """
    return vector_store