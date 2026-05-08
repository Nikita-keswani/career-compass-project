import time
import json
from datetime import datetime

from src.services.mongo_db import MongoDBClient
from utils.logger import get_logger

logger = get_logger(__name__)

class ChatHistoryManager:
    def __init__(self):
        self.mongo_client = MongoDBClient(collection_name="chat_details")

    def list_threads(self, user_id: str, chat_type: str) -> list:
        """
        Returns all threads for a user+chat_type as [{id, name}].
        The name is derived from the first user message in the thread.
        """
        records = self.mongo_client.retrieve_records(
            {"user_id": user_id, "chat_type": chat_type},
            limit=100
        )
        threads = []
        for record in records:
            thread_id = record.get("_id", "")
            chat_history = record.get("chat_history", [])
            # Derive name from first user message
            if chat_history:
                first_msg = chat_history[0].get("user_input", "New Thread")
                name = first_msg[:40] + "…" if len(first_msg) > 40 else first_msg
            else:
                name = "Empty Thread"
            threads.append({"id": thread_id, "name": name})
        return threads

    def save_history(self, user_id: str, user_input: str|dict, response: str, thread_id: str, chat_type: str):
        logger.debug(f"Saving chat history for user: {user_id}, thread: {thread_id}, type: {chat_type}")
        record = self.mongo_client.retrieve_record(
            {
                "user_id": user_id,
                "_id": thread_id,
                "chat_type": chat_type
            }
        )
        if isinstance(user_input, dict):
            user_input = json.dumps(user_input)
        if record:
            record["chat_history"].append({
                "user_input": user_input,
                "bot_response": response,
                "timestamp": datetime.now()
            })

            self.mongo_client.upsert_record(
                {
                    "user_id": user_id,
                    "_id": thread_id,
                    "chat_type": chat_type
                },
                record
            )
        else:
            self.mongo_client.insert_record({
                "user_id": user_id,
                "_id": thread_id,
                "chat_type": chat_type,
                "chat_history": [
                    {
                        "user_input": user_input,
                        "bot_response": response,
                        "timestamp": datetime.now()
                    }
                ]
            })

    def get_history(self, user_id: str, thread_id: str, chat_type: str):
        record = self.mongo_client.retrieve_record({
            "user_id": user_id,
            "_id": thread_id,
            "chat_type": chat_type
        })

        if record:
            return record["chat_history"]
        logger.debug(f"No chat history found for user: {user_id}, thread: {thread_id}")
        return []

    def delete_thread(self, user_id: str, thread_id: str, chat_type: str) -> bool:
        """Deletes a thread's chat history from MongoDB."""
        logger.info(f"Deleting thread: user={user_id}, thread={thread_id}, type={chat_type}")
        return self.mongo_client.delete_record({
            "user_id": user_id,
            "_id": thread_id,
            "chat_type": chat_type
        })