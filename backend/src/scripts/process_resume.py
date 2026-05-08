from src.core.document_parser import DocumentParser
from src.services.azure_openai import OpenAIClient
from src.prompts.resume_prompt import resume_sm, resume_um
from src.core.chat_history_manager import ChatHistoryManager

from utils.logger import get_logger

parser = DocumentParser()
openai_client = OpenAIClient()
chat_history_manager = ChatHistoryManager()
logger = get_logger(__name__)


def process_resume(
    resume_path: str, 
    job_role: str, 
    experience_level: str, 
    company_requirements: str|None,
    user_id: str,
    thread_id: str
    ):
    logger.info(f"Parsing PDF document from path: {resume_path}")
    docs = parser.parse_pdf(resume_path)
    resume_text = "\n".join([doc.page_content for doc in docs])
    logger.info("Sending parsed resume text to Azure OpenAI for generation")
    response = openai_client.generate_text(resume_sm, resume_um.format(resume_text=resume_text, job_role=job_role, experience_level=experience_level, company_requirements=company_requirements))
    logger.info("Successfully received generated evaluation from Azure OpenAI")
    user_input = f"Resume: {resume_text}\n\nJob Role: {job_role}\n\nExperience Level: {experience_level}\n\nCompany Requirements: {company_requirements}"
    chat_history_manager.save_history(user_id, user_input, response, thread_id, "resume_assistant")
    return response







    

    