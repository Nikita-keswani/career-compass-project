from datetime import datetime

from src.services.mongo_db import MongoDBClient
from utils.logger import get_logger

logger = get_logger(__name__)

class UserManager:

    def __init__(self):
        self.mongo_client = MongoDBClient(collection_name="user_details")

    def create_user(self, user_id: str, username: str, enc_password: str, firstname: str, lastname:str):
        if self.username_exists(username):
            logger.warning(f"Attempt to create user failed: {username} already exists")
            return {"status": "fail", "message": "user with username already exists"}

        self.mongo_client.insert_record({
            "_id": user_id,
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "enc_password": enc_password,
            "created_at": datetime.now()
        })

        logger.info(f"User {username} successfully saved to DB")
        return {
            "status": "success",
            "message": "User created successfully."
        }

    def username_exists(self, username: str):
        record = self.mongo_client.retrieve_record({
            "username": username
        })
        return record is not None

    def get_user_details(self, username:str):
        record = self.mongo_client.retrieve_record({
            "username": username
        })
        if record:
            return {"status": "success", "message": "User found", "data": record}
        else:
            return {"status": "fail", "message": "User not found"}
