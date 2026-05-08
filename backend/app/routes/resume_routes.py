import os
import shutil
from fastapi import APIRouter, File, UploadFile, Form
from src.scripts.process_resume import process_resume
from utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/upload_resume")
async def upload_resume(
        file: UploadFile = File(...), 
        job_role: str = Form(...), 
        experience_level: str = Form(...), 
        company_requirements: str|None = Form(None),
        user_id: str = Form(...),
        thread_id: str = Form(...)
    ):
    logger.info(f"Resume upload initiated: filename={file.filename}, job_role={job_role}, user={user_id}")
    # Create temp directory
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save the file locally
    temp_file_path = os.path.join(temp_dir, file.filename)
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process the resume
        logger.info(f"Processing resume: {file.filename}")
        response = process_resume(temp_file_path, job_role, experience_level, company_requirements, user_id, thread_id)
        logger.info(f"Successfully processed resume: {file.filename}")
        return {"filename": file.filename, "response": response}
    except Exception as e:
        logger.error(f"Error processing resume {file.filename}: {str(e)}")
        raise e
    finally:
        # Clean up: remove the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
