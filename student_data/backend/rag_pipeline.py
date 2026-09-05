import pathlib
import os
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
import requests
import numpy as np

# HF API Embeddings - No torch needed!
class HF_API_Embeddings:
    def __init__(self):
        self.token = os.environ.get("HF_TOKEN")
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"

    def embed_documents(self, texts):
        headers = {"Authorization": f"Bearer {self.token}"}
        embeddings = []
        for text in texts:
            resp = requests.post(self.api_url, headers=headers, json={"inputs": text, "options": {"wait_for_model": True}})
            embeddings.append(np.array(resp.json()).mean(axis=0).tolist() if isinstance(resp.json()[0], list) else resp.json())
        return embeddings

    def embed_query(self, text):
        return self.embed_documents([text])[0]

    def __call__(self, text):
        return self.embed_query(text)

vector_db = None
llm = None

def load_models():
    global vector_db, llm
    if vector_db is not None:
        return

    embeddings = HF_API_Embeddings()
    BASE = pathlib.Path(__file__).parent.parent # student_data folder

    # Nuvvu ekkada pettina auto-find chestadi!
    possible_paths = [
        BASE / "faiss_index",
        BASE,
        pathlib.Path("student_data/faiss_index"),
        pathlib.Path("student_data"),
        pathlib.Path("faiss_index"),
    ]

    DB_PATH = None
    for p in possible_paths:
        if (p / "index.faiss").exists():
            DB_PATH = p
            print(f"✅ Found FAISS at: {DB_PATH}")
            break

    if DB_PATH is None:
        raise FileNotFoundError("index.faiss not found anywhere!")

    vector_db = FAISS.load_local(str(DB_PATH), embeddings, allow_dangerous_deserialization=True)
    vector_db.embedding_function = embeddings

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.2
    )
    print("✅ Models loaded successfully!")

def get_answer(query):
    load_models()
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([d.page_content for d in docs])
    prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer based on context:"
    response = llm.invoke(prompt)
    return response.content, docs
