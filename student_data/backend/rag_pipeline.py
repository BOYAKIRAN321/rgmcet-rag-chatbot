import os
import pathlib
import requests
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

class HF_API_Embeddings:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

    def embed_query(self, text):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.post(self.api_url, headers=headers, json={"inputs": text, "options": {"wait_for_model": True}}, timeout=60)
        res.raise_for_status()
        emb = res.json()
        # HF returns list, sometimes nested
        if isinstance(emb[0], list):
            return emb[0]
        return emb

    def embed_documents(self, texts):
        return [self.embed_query(t) for t in texts]

    def __call__(self, text):
        return self.embed_query(text)

vector_db = None
llm = None

def load_models():
    global vector_db, llm
    if vector_db is not None:
        return
    print("Loading FAISS with HF API embeddings...")
    embeddings = HF_API_Embeddings()
    BASE_DIR = pathlib.Path(__file__).parent.parent
    DB_PATH = BASE_DIR / "faiss_index"
    vector_db = FAISS.load_local(str(DB_PATH), embeddings, allow_dangerous_deserialization=True)
    vector_db.embedding_function = embeddings

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )
    print("Models ready!")

def run_rag(query):
    load_models()
    docs = vector_db.similarity_search(query, k=2)
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"You are RGMCET assistant. Context: {context}\n\nQuestion: {query}\nAnswer clearly:"
    result = llm.invoke(prompt)
    return result.content
