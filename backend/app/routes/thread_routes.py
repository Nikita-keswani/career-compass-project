from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter
from src.core.chat_history_manager import ChatHistoryManager
from utils.logger import get_logger

router = APIRouter()
chat_manager = ChatHistoryManager()
logger = get_logger(__name__)


class ThreadListRequest(BaseModel):
    user_id: str
    chat_type: str


class ThreadHistoryRequest(BaseModel):
    user_id: str
    thread_id: str
    chat_type: str


@router.post("/list")
async def list_threads(request: ThreadListRequest):
    """
    Returns all thread IDs and their first message (as thread name)
    for a given user and chat type.
    """
    logger.info(f"Listing threads for user={request.user_id}, type={request.chat_type}")
    threads = chat_manager.list_threads(request.user_id, request.chat_type)
    return {"threads": threads}


@router.post("/history")
async def get_thread_history(request: ThreadHistoryRequest):
    """
    Returns the full chat history for a specific thread.
    """
    logger.info(f"Fetching history for thread={request.thread_id}, user={request.user_id}")
    history = chat_manager.get_history(request.user_id, request.thread_id, request.chat_type)
    return {"history": history}


@router.post("/delete")
async def delete_thread(request: ThreadHistoryRequest):
    """
    Deletes a specific thread and its chat history.
    """
    logger.info(f"Deleting thread={request.thread_id}, user={request.user_id}")
    deleted = chat_manager.delete_thread(request.user_id, request.thread_id, request.chat_type)
    return {"deleted": deleted}
