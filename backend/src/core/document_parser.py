import os
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentParser:

    def __init__(self):
        pass

    def parse_pdf(self, pdf_path: str) -> list:
        if not os.path.exists(pdf_path):
            print(f"Document not found: {pdf_path}")
            return []
            
        loader = PyPDFLoader(pdf_path)
        doc = loader.load()
        return doc

    def parse_csv(self, csv_path: str) -> list:
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            return []
            
        df = pd.read_csv(csv_path)
        table_markdown = df.to_markdown(index=False)
        return [Document(page_content=table_markdown, metadata={"source": csv_path})]

    def parse_excel(self, excel_path: str) -> list:
        if not os.path.exists(excel_path):
            print(f"File not found: {excel_path}")
            return []
            
        df = pd.read_excel(excel_path)
        table_markdown = df.to_markdown(index=False)
        return [Document(page_content=table_markdown, metadata={"source": excel_path})]

    def parse_txt(self, txt_path: str) -> list:
        if not os.path.exists(txt_path):
            print(f"File not found: {txt_path}")
            return []
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return [Document(page_content=content, metadata={"source": txt_path})]

    def generate_chunks(self, documents: list) -> list:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", " ", ""]
        )
        return splitter.split_documents(documents)