import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
from app.routes.resume_routes import router as resume_router
from app.routes.assistant_routes import router as assistant_router
from app.routes.user_login import router as user_login_router
from app.routes.thread_routes import router as thread_router
from app.middleware.jwt_auth import JWTAuthMiddleware
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

app = FastAPI(title="Career Navigator API")

# --- Middleware (order matters: last added = first executed) ---
# JWT auth runs first, then CORS headers are applied
app.add_middleware(JWTAuthMiddleware)
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(resume_router, prefix="/resume", tags=["ResumeAnalyzer"])
app.include_router(assistant_router, prefix="/assistant", tags=["Assistants"])
app.include_router(user_login_router, prefix="/user", tags=["User"])
app.include_router(thread_router, prefix="/threads", tags=["Threads"])

@app.get("/")
def root():
    return {"message": "Career Navigator API running"}

@app.get("/health")
def health():
    return {"status": "OK"}

if __name__ == "__main__":
    logger.info("Starting Career Navigator API...")
    uvicorn.run(app, host="localhost", port=8000)
