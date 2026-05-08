from src.services.mongo_db import MongoDBClient
from src.services.azure_openai import OpenAIClient
from src.prompts.skit_assistant_prompts import skit_assistant_sm, skit_assistant_um
from src.services.vector_db import PineconeClient
from src.core.chat_history_manager import ChatHistoryManager
from utils.logger import get_logger

logger = get_logger(__name__)

class SKITAssistant:

    def __init__(self):
        self.openai_client = OpenAIClient()
        self.pinecone_client = PineconeClient()
        self.chat_manager = ChatHistoryManager()

    def retrieve_context(self, query: str) -> list:
        query_embedding = self.openai_client.generate_embedding(query)
        return self.pinecone_client.retrieve(query_embedding)

    def generate_response(self, query: str, context: list, chat_history: list) -> str:
        prompt = skit_assistant_um.format(query=query, context=context, chat_history=chat_history)
        return self.openai_client.generate_text(skit_assistant_sm, prompt)

    def chat(self, query: str, user_id: str, thread_id: str) -> str:
        logger.info(f"SKITAssistant chat initiated for user: {user_id}, thread: {thread_id}")
        context = self.retrieve_context(query)
        chat_history = self.chat_manager.get_history(user_id, thread_id, "skit_assistant")
        response = self.generate_response(query, context, chat_history)
        self.chat_manager.save_history(user_id, query, response, thread_id, "skit_assistant")
        return response