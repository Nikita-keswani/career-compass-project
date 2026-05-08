import os
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv(override=True)
logger = get_logger(__name__)

class MongoDBClient:
    """
    Service class for MongoDB operations.
    """

    def __init__(self, uri: str = None, db_name: str = None, collection_name: str = None):
        """
        Initializes the MongoDB client.
        :param uri: Connection string
        :param db_name: Name of the database
        :param collection_name: Name of the default collection
        """
        self.uri = uri or os.getenv("MONGODB_URI")
        self.db_name = db_name or os.getenv("MONGODB_DATABASE_NAME")
        self.collection_name = collection_name or os.getenv("MONGODB_COLLECTION_NAME")

        if not self.uri:
            raise ValueError("MONGODB_URI environment variable is not set.")
        if not self.db_name:
            raise ValueError("MONGODB_DATABASE_NAME environment variable is not set.")
        if not self.collection_name:
            raise ValueError("MONGODB_COLLECTION_NAME environment variable is not set.")

        self.client = MongoClient(self.uri)
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        logger.info(f"MongoDB Client initialized: DB='{self.db_name}', Collection='{self.collection_name}'")

    def insert_record(self, record: Dict[str, Any]):
        """
        Inserts a single record into the collection.
        """
        try:
            result = self.collection.insert_one(record)
            return str(result.inserted_id)
        except Exception as e:
            raise RuntimeError(f"Failed to insert record: {e}")

    def upsert_record(self, filter_query: Dict[str, Any], record: Dict[str, Any]):
        """
        Updates a record if it exists, otherwise inserts it.
        """
        try:
            result = self.collection.update_one(
                filter_query,
                {"$set": record},
                upsert=True
            )
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
        except Exception as e:
            raise RuntimeError(f"Failed to upsert record: {e}")

    def retrieve_record(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single record based on a filter.
        """
        try:
            return self.collection.find_one(filter_query)
        except Exception as e:
            logger.error(f"Failed to retrieve record: {str(e)}")
            raise RuntimeError(f"Failed to retrieve record: {e}")

    def retrieve_records(self, filter_query: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves multiple records based on a filter.
        """
        try:
            query = filter_query or {}
            cursor = self.collection.find(query).limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to retrieve records: {str(e)}")
            raise RuntimeError(f"Failed to retrieve records: {e}")

    def delete_record(self, filter_query: Dict[str, Any]) -> bool:
        """
        Deletes a single record matching the filter.
        Returns True if a document was deleted.
        """
        try:
            result = self.collection.delete_one(filter_query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete record: {str(e)}")
            raise RuntimeError(f"Failed to delete record: {e}")
