from pydantic import BaseModel
from fastapi import APIRouter, File, UploadFile, Form
from src.core.career_assistant import CareerAssistant
from src.core.skit_assistant import SKITAssistant
from src.core.chat_history_manager import ChatHistoryManager
from utils.logger import get_logger

class AssistantRequest(BaseModel):
    user_input: str
    thread_id: str
    user_id: str

router = APIRouter()
career_assistant = CareerAssistant()
skit_assistant = SKITAssistant()
chat_manager = ChatHistoryManager()
logger = get_logger(__name__)

@router.post("/chat_career_assistant")
async def chat_career_assistant(request: AssistantRequest):
    logger.info(f"Career assistant chat requested by user {request.user_id} in thread {request.thread_id}")
    response = {
        "question": request.user_input,
        "response": career_assistant.chat(request.user_input, request.user_id, request.thread_id)
        }
    return response

@router.post("/chat_skit_assistant")
async def chat_skit_assistant(request: AssistantRequest):
    logger.info(f"SKIT assistant chat requested by user {request.user_id} in thread {request.thread_id}")
    response = {
        "question": request.user_input,
        "response": skit_assistant.chat(request.user_input, request.user_id, request.thread_id)
        }
    return response

