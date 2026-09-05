import os
import json
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNK_PATH = BASE_DIR / "DATA" / "chunks"
META_PATH = BASE_DIR / "DATA" / "metadata"
FAISS_PATH = BASE_DIR / "DATA" / "faiss_index"
FAISS_PATH.mkdir(parents=True, exist_ok=True)

def load_documents():
    documents = []
    if not CHUNK_PATH.exists():
        print("❌ CHUNK_PATH not found:", CHUNK_PATH)
        return documents
    for file in os.listdir(CHUNK_PATH):
        if file.endswith(".txt"):
            chunk_file = CHUNK_PATH / file
            meta_file = META_PATH / file.replace(".txt", ".json")
            with open(chunk_file, "r", encoding="utf-8") as f:
                content = f.read()
            metadata = {}
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as mf:
                    metadata = json.load(mf)
            documents.append(Document(page_content=content, metadata=metadata))
    return documents

def create_faiss_index(documents):
    print("🔎 Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(FAISS_PATH))
    print(f"✅ FAISS index saved at {FAISS_PATH}")

if __name__ == "__main__":
    docs = load_documents()
    print(f"📄 Loaded {len(docs)} chunks")
    if docs:
        create_faiss_index(docs)
    else:
        print("⚠ No documents found. Check DATA/chunks folder.")
