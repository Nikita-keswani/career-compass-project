# Career Navigator API (Backend)

The Career Navigator Backend is a robust FastAPI application serving as the brain for the Career Compass ecosystem. It integrates RAG (Retrieval-Augmented Generation) pipelines, user authentication, document parsing, and AI assistants powered by Azure OpenAI and vector embeddings (Pinecone).

## 📁 Directory Structure

```text
backend/
├── app/
│   ├── middleware/        # Global Middleware (e.g., JWT Authentication)
│   └── routes/            # API Endpoints (Assistants, Resume Analyser, User Auth)
├── src/
│   ├── core/              # Core business logic:
│   │   ├── career_assistant.py      # LLM logic for general career queries
│   │   ├── skit_assistant.py        # LLM logic for SKIT specific queries
│   │   ├── chat_history_manager.py  # Stores chat in MongoDB
│   │   ├── document_parser.py       # Langchain parsing (PDF, txt, csv, excel)
│   │   └── user_manager.py          # Registration, login logic
│   ├── prompts/           # System instructions for different AI personas
│   ├── scripts/           # Core execution workflows:
│   │   ├── ingest_data.py           # Loads docs, chunks, creates embeddings, pushes to VectorDB
│   │   └── process_resume.py        # Resume assessment workflow using Azure OpenAI
│   └── services/          # External connections:
│       ├── azure_openai.py          # Embeddings and Text Generation
│       ├── mongo_db.py              # Persistent NoSQL database
│       └── vector_db.py             # Pinecone initialization & retrievals
├── utils/
│   └── logger.py          # Unified structured logging (outputs to console and /logs)
├── main.py                # FastAPI Application Entrypoint
└── run_ingestion.py       # CLI Utility for Pinecone Database Hydration
```

## 🚀 Features

1. **Dual AI Assistants**:
   - `CareerAssistant`: Provides generic career roadmaps, guidance, and tips.
   - `SKITAssistant`: Expert persona focused on academic data or campus-specific knowledge.
   - Built with full RAG pipelines querying Pinecone vector datastores.
2. **Contextual Chat & History**:
   - Conversations are stored using the `ChatHistoryManager` locally in MongoDB keeping track of long-term `thread_id` across varying endpoints.
3. **Resume Analysis Workflow**:
   - Accepts multipart file uploads, processes the PDF content dynamically and uses AI to compare experience criteria to provided job roles/requirements.
4. **Data Ingestion System (`run_ingestion.py`)**:
   - Reads directories of `PDF, TXT, CSV, XLSX`.
   - Normalizes text via Langchain chunkers.
   - Upserts embeddings along with metadata back into Pinecone.
5. **Security & Auth**:
   - Global JWT Authorization middleware.
   - Validates tokens dynamically on secured endpoints while exposing public ones (`/health`, `/users/login`, `/users/signup`).

## 🛠️ Setup & Installation

**1. Create a Virtual Environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

**2. Install Dependencies**
Assuming `requirements.txt` is located in your project root:
```bash
pip install -r ../requirements.txt
```

**3. Configure Environment Variables**
Create a `.env` file either in the root directory or inside `backend/` containing:

```env
# Azure OpenAI Credentials
AZURE_OPENAI_KEY="your-azure-key"
AZURE_OPENAI_API_VERSION="2024-12-01-preview"
AZURE_OPENAI_ENDPOINT="https://openai.openai.azure.com/"
AZURE_OPENAI_LANGUAGE_MODEL="4o"
AZURE_OPENAI_EMBEDDING_MODEL="text-embedding-3-small"

# Pinecone Credentials
PINECONE_API_KEY="your-pinecone-key"
PINECONE_ENVIRONMENT="us-east-1"
PINECONE_INDEX_NAME="test-embeddings"

# MongoDB Database URI
MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/?appName=cluster"
MONGODB_DATABASE_NAME="career_compass"

# JWT Config
JWT_SECRET_KEY="super-secret-key-change-in-production"
JWT_EXPIRE_MINUTES="1440"
```

## 🏃 Running the Application

### Start the API Server

Starts the FastAPI app (running on `uvicorn`):
```bash
cd backend
python main.py
```
> Alternatively, start the backend gracefully via: `uvicorn main:app --reload`

The API will be available at `http://localhost:8000`. You can test endpoints dynamically by heading onto the Interactive Swagger Docs at [http://localhost:8000/docs](http://localhost:8000/docs).

### Data Ingestion Pipeline (Pinecone Database)

To populate the Knowledge Base with new documents, place files in a given directory and run the standalone ingestion script:

```bash
cd backend
python run_ingestion.py /absolute/path/to/data_folder your_index_name
```
*Note: Make sure to provide an absolute path to avoid permission or resolution errors.*

## 📋 Logging
You can configure or debug applications via logs stored automatically within `backend/logs/app.log`. Everything from server startup, JWT errors, Pinecone upload batch results, and specific backend failures are recorded meticulously in both the local console and this rotating file.
