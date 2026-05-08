import os
from openai import AzureOpenAI
from typing import List
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv(override=True)
logger = get_logger(__name__)

class OpenAIClient:

    def __init__(self):

        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.key = os.getenv("AZURE_OPENAI_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        if not self.endpoint or not self.key:
            raise Exception("Missing OpenAI key or endpoint")

        self.language_model = os.getenv("AZURE_OPENAI_LANGUAGE_MODEL")
        self.embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")

        if not self.embedding_model or not self.language_model:
            raise Exception("Missing embedding model or language model")
        
        self.client = AzureOpenAI(
                api_key=self.key,
                azure_endpoint=self.endpoint,
                api_version=self.api_version
            )

        logger.info("Azure OpenAI Client initialized.")

    def generate_text(self, system_message:str, user_message:str) -> str:
        response = self.client.chat.completions.create(
            model=self.language_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3
        )

        logger.debug(f"Generated text completion using {self.language_model}")
        return response.choices[0].message.content

    def generate_embedding(self, text:str) -> List[float]:
    
        embedding = self.client.embeddings.create(
            input=[text],
            model=self.embedding_model
        )
        return embedding.data[0].embedding

    def stream_text(self, system_message:str, user_message:str):
        
        chunk_stream = self.client.chat.completions.create(
            model=self.language_model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            stream = True
        )
        for chunk in chunk_stream:
            yield chunk.content

    






#   def get_llm_client(api_key: str = None, endpoint: str = None, version: str = None):
#       """
#       Create Azure OpenAI client for LLM services.
#       """
#       return AzureOpenAI(
#           api_key=api_key or os.getenv("AZURE_OPENAI_API_KEY"),
#           azure_endpoint=endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"),
#           api_version=version or os.getenv("AZURE_OPENAI_API_VERSION"),
#       )


#   def generate_answer(context: str, query: str):
#       client = get_llm_client()

#       system_prompt = """
#   ### Identity
#   You are **Career Compass AI**, a sophisticated and empathetic career guidance assistant. Your mission is to provide accurate, up-to-date, and actionable advice to students and professionals regarding their educational and career journeys.

#   ### Scope of Expertise
#   You specialize exclusively in the following areas:
#   - **Career Planning & Roadmaps**: Step-by-step guidance on choosing streams and building career paths (e.g., "How to become a Data Scientist", "B.Tech Roadmap").
#   - **Education & Admissions**: Information on colleges (Government & Private), admission procedures, and counseling (e.g., REAP, JoSAA, CSAB).
#   - **Competitive & Government Exams**: Updates on National and State-level exams (JEE, NEET, UPSC, SSC, RRB, etc.), including notification dates and eligibility.
#   - **Real-time Internships & Jobs**: Latest updates on internship openings, placement support, and skill development.
#   - **Financial Aid**: Information on scholarships and educational grants.
#   - **Strategic Advice**: Estimating admission chances based on cutoffs, ranks, and scores.


#   ### Operational Guidelines
#   1. **Strict Career Focus**: If the user asks about topics unrelated to education or career (e.g., cooking, general knowledge, entertainment), politely inform them that your expertise is limited to career guidance.
#   2. **Contextual Accuracy**: Use the provided `Context` (Internal Knowledge Base and Web Results) as your primary source of truth.
#   3. **Beautiful Markdown Formatting**: Always format your answers for high visual appeal and premium readability:
#     - Use **Markdown Headings** (e.g., `### Section Title`) for different parts of the answer.
#     - Use **Bold text** for key terms, important dates, and specific college/exam names.
#     - Use **Tables** to compare colleges, cutoffs, or salaries where appropriate.
#     - Use **Bullet points or numbered lists** for clear steps or features.
#     - Use **Horizontal rules** (`---`) to separate distinct sections of information.
#     - Use **Blockquotes** (`>`) for important tips or warnings.
#     - Use **Emojis** sparingly but effectively to make the response more student-friendly and engaging (e.g., 🧭, 🎓, 💼, 📅).
#   4. **Citations**: If the context provides specific sources or URLs, mention them clearly as clickable links in Markdown where possible.
#   5. **Encouraging Tone**: Maintain a professional, encouraging, and mentoring tone.
#   6. **Admission Logic**: When asked about admission chances, use the ranks and cutoffs provided in the context to give realistic estimates.

#   ### Output Structure Example:
#   - **Summary**: A brief overview of the answer.
#   - **Key Details**: The core information requested.
#   - **Next Steps/Actionable Advice**: What the user should do now.

#   Always prioritize the most recent information (marked as [Web] or updated dates) when conflicting data exists.

#   """


#       user_prompt = f"""
#   Context:
#   {context}

#   Question:
#   {query}

#   Give a clear, structured, student-friendly answer.
#   """

#       response = client.chat.completions.create(
#           model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
#           messages=[
#               {"role": "system", "content": system_prompt},
#               {"role": "user", "content": user_prompt}
#           ],
#           temperature=0.3,
#           stream=False
#       )

#       return response.choices[0].message.content