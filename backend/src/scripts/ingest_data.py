import os
import uuid

from src.core.document_parser import DocumentParser
from src.services.azure_openai import OpenAIClient
from src.services.vector_db import PineconeClient
from utils.logger import get_logger

logger = get_logger(__name__)

def ingest_directory(directory_path: str, index_name: str):
    if not os.path.exists(directory_path):
        logger.error(f"Directory not found: {directory_path}")
        return

    if not os.path.isabs(directory_path):
        logger.warning(f"Path is not absolute. Converting {directory_path} to absolute path.")
        directory_path = os.path.abspath(directory_path)

    logger.info(f"Starting data ingestion from directory: {directory_path}")

    parser = DocumentParser()
    openai_client = OpenAIClient()
    pinecone_client = PineconeClient(index_name=index_name)

    all_raw_documents = []

    # 1. Load and Parse files
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()

            logger.info(f"Processing file: {file_path}")
            
            try:
                docs = []
                if ext == ".pdf":
                    docs = parser.parse_pdf(file_path)
                elif ext == ".csv":
                    docs = parser.parse_csv(file_path)
                elif ext in [".xlsx", ".xls"]:
                    docs = parser.parse_excel(file_path)
                elif ext == ".txt":
                    docs = parser.parse_txt(file_path)
                else:
                    logger.warning(f"Unsupported file extension {ext} for {file}. Skipping.")
                    continue
                
                if docs:
                    all_raw_documents.extend(docs)
                    logger.info(f"Extracted {len(docs)} document chunks/pages from {file}")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")

    if not all_raw_documents:
        logger.warning(f"No valid documents found to ingest in {directory_path}.")
        return

    # 2. Chunk documents
    logger.info(f"Splitting {len(all_raw_documents)} loaded documents into chunks...")
    chunked_docs = parser.generate_chunks(all_raw_documents)
    logger.info(f"Generated {len(chunked_docs)} total chunks.")

    # 3. Generate embeddings and prepare for Pinecone
    records = []
    logger.info("Generating embeddings and formatting for Pinecone upsert...")
    
    for idx, chunk in enumerate(chunked_docs):
        text = chunk.page_content
        metadata = chunk.metadata.copy()
        
        # Add chunk text to metadata so we can retrieve it later
        metadata["text"] = text

        try:
            embedding = openai_client.generate_embedding(text)
            
            # Use doc_id as expected by PineconeClient
            record = {
                "doc_id": f"chunk-{uuid.uuid4()}",
                "embedding": embedding,
                "metadata": metadata
            }
            records.append(record)
        except Exception as e:
            logger.error(f"Failed to generate embedding for chunk {idx+1}: {e}")

    # 4. Upsert to vector DB
    if records:
        logger.info(f"Upserting {len(records)} vector records to Pinecone...")
        pinecone_client.upsert_from_json(records, batch_size=50)
        logger.info("Ingestion completed successfully.")
    else:
        logger.warning("No records to upsert.")