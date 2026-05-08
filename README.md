# 🧭 Career Navigator

Career Navigator is an AI-powered guidance platform that helps users with career planning, academic information (specifically tailored for SKIT), and intelligent resume analysis. It leverages Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide highly relevant and contextual advice.

## ✨ Key Features

### 1. 💼 AI Career Assistant
* Get tailored advice on career roadmaps, job opportunities, and skill development.
* **Persistent Conversations:** All chat threads are automatically saved and organized so you can return to them later.
* **Smart UI:** Dynamic markdown rendering ensures code blocks, tables, and lists in bot responses look clean and structured.

### 2. 🎓 SKIT Assistant
* An intelligent assistant specifically trained and configured for SKIT academics, campus life, and placement guidelines.
* Separate persistent conversation threads to maintain context and history.

### 3. 📄 ATS Resume Analyser
* Upload your PDF resume, specify a target job role, experience level, and optional company requirements.
* Powered by OpenAI, the analyzer acts as an expert ATS (Applicant Tracking System), providing:
  * **ATS Score:** A 0-100 score indicating resume compatibility with the requested job profile.
  * **Sub-scores:** Detailed matching scores for Skills, Projects, Experience, and Format.
  * **Feedback:** Itemized identification of your strengths, weaknesses, resume lags, and actionable corrections.
  * **Missing Keywords:** Crucial industry/role keywords absent from your resume.

### 4. 🔒 Secure Authentication
* Full user registration and login flows.
* Secured via industry-standard **JWT (JSON Web Tokens)** logic.

---

## 🛠️ Tech Stack & Architecture

### Backend (Python / FastAPI)
* **Framework:** FastAPI for high-performance, async API endpoints.
* **Database (Relational/Document):** MongoDB (stores users and persistent chat histories).
* **Vector Database:** Pinecone (for RAG document retrieval).
* **AI Provider:** Azure OpenAI.
* **Authentication:** JWT (JSON Web Tokens) Bearer Auth Middleware.
* **Data Ingestion:** Automated document parsers to chunk and embed CSV, Excel, PDF, and Text data into Pinecone.

### Frontend (HTML / CSS / JavaScript)
* **UI/UX:** Vanilla HTML5, CSS3, and JavaScript implementation.
* **Styling:** Custom fluid design system using a modern dark-mode aesthetic. 
* **Rendering:** Utilizes `marked.js` to parse markdown elements inside chat widgets dynamically.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* MongoDB setup locally or via MongoDB Atlas.
* Pinecone account and API key.
* Azure OpenAI Endpoint & Key set up.

### Backend Setup

1. **Navigate to backend folder:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have packages like `fastapi`, `uvicorn`, `pymongo`, `pinecone-client`, `openai`, `python-jose`, `passlib`, `python-multipart` installed).*

3. **Environment Setup:**
   Create a `.env` file in the `backend` directory and provide your credentials.
   ```env
   # JWT Configuration
   JWT_SECRET_KEY=your_secret_key_here
   JWT_EXPIRE_MINUTES=1440

   # MongoDB Conifguration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DATABASE_NAME=career_nav_db

   # Pinecone Configuration
   PINECONE_API_KEY=your_pinecone_key_here
   PINECONE_ENVIRONMENT=your_environment_here
   PINECONE_INDEX_NAME=your_index_here

   # Azure OpenAI Configuration
   AZURE_OPENAI_API_KEY=your_azure_key_here
   AZURE_OPENAI_ENDPOINT=your_azure_endpoint
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

4. **Run the API Server:**
   ```bash
   python main.py
   # Or using uvicorn directly:
   # uvicorn main:app --reload --host localhost --port 8000
   ```
   The backend will start at `http://localhost:8000`.

### Frontend Setup

1. **Serve the frontend locally:**
   Navigate to the `frontend` folder and serve the static files. E.g., using Python:
   ```bash
   cd frontend
   python -m http.server 3000
   ```
2. **Launch Application:**
   Open your browser and navigate to `http://localhost:3000/index.html`.
3. Create an account, log in, and you'll be securely redirected to the dashboard!

---

## 📂 Project Structure

```text
PDGRag/
├── backend/
│   ├── app/
│   │   ├── middleware/       # JWT and Auth middleware guards
│   │   └── routes/           # FastAPI routers (auth, assistants, threads, resume)
│   ├── src/
│   │   ├── core/             # AI agent logic, chunking, history management
│   │   ├── prompts/          # System prompts for OpenAI
│   │   ├── scripts/          # Ingestion pipelines and PDF parsers
│   │   └── services/         # Wrappers for external clients (MongoDB, Pinecone, Azure)
│   ├── temp/                 # Local holding directory for uploaded resume PDFs
│   └── main.py               # Application entry point
│
└── frontend/
    ├── css/
    │   └── styles.css        # Comprehensive design system
    ├── js/
    │   ├── api.js            # Centralized API fetch wrapper
    │   ├── auth.js           # Login & Signup logic and error handling
    │   └── dashboard.js      # App orchestration, chat UI, threaded state, resume graphs
    ├── index.html            # Landing / Authentication portal
    └── dashboard.html        # Main app interface (Chat panels & Resume Tools)
```

## 📝 Usage Notes

* **Resume Processing:** When using the ATS Analyzer, the file is temporarily saved inside the `backend/temp` folder, parsed to extract text using OCR/PDF readers, sent to Azure OpenAI with a tightly constrained JSON schematic prompt, and seamlessly discarded upon completion. 
* **Conversations:** The backend's `POST /threads/list` endpoint retrieves a user's threads on dashboard load, and `POST /threads/history` executes a lazy-load retrieval of the conversation only when a thread is clicked.
