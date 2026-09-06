import os
import re
import pathlib
import requests
from langchain_community.vectorstores import FAISS

class HF_API_Embeddings:
    def __init__(self):
        self.token = os.environ.get("HF_TOKEN")
        self.url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    def embed_documents(self, texts):
        headers = {"Authorization": f"Bearer {self.token}"}
        result = []
        for t in texts:
            try:
                r = requests.post(self.url, headers=headers, json={"inputs": t, "options": {"wait_for_model": True}}, timeout=30)
                data = r.json()
                if isinstance(data[0], float): result.append(data)
                elif isinstance(data[0], list): result.append(data[0])
                else: result.append([0.0]*384)
            except: result.append([0.0]*384)
        return result
    def embed_query(self, text): return self.embed_documents([text])[0]
    def __call__(self, text): return self.embed_query(text)

vector_db = None
llm = None

def load_models():
    global vector_db, llm
    if vector_db is not None: return
    from langchain_groq import ChatGroq
    embeddings = HF_API_Embeddings()
    BASE = pathlib.Path(__file__).parent.parent
    DB_PATH = None
    for p in [BASE / "faiss_index", BASE]:
        if (p / "index.faiss").exists():
            DB_PATH = p; print(f"✅ FAISS FOUND at {DB_PATH}"); break
    if DB_PATH is None: raise FileNotFoundError("index.faiss not found!")
    vector_db = FAISS.load_local(str(DB_PATH), embeddings, allow_dangerous_deserialization=True)
    vector_db.embedding_function = embeddings
    llm = ChatGroq(model="openai/gpt-oss-120b", groq_api_key=os.environ.get("GROQ_API_KEY"), temperature=0.1)
    print("✅ Models loaded!")

def get_answer(query):
    load_models()
    # Roll number ni direct ga vetuku
    match = re.search(r'\b\d{2}[A-Z0-9]+[A-Z0-9]{4,}\b', query.upper())
    roll = match.group(0) if match else "".join(filter(str.isalnum, query)).upper()
    
    # Normal similarity search
    docs = vector_db.similarity_search(query, k=10)
    
    # Extra: roll number unna docs ni filter chey
    matched = [d for d in docs if roll in d.page_content.upper() or query.upper() in d.page_content.upper()]
    
    # If matched docs unnayi, vaatike vadali
    if matched:
        docs = matched
    
    context = "\n\n".join([d.page_content for d in docs])
    
    # Prompt kuda strict ga marchu
    prompt = f"""You are RGMCET assistant. Answer ONLY from Context.
If roll number {roll} is in context, give full details. Don't say not found if it's there.

Context:
{context}

Question: {query}

Answer:"""
    
    resp = llm.invoke(prompt)
    return resp.content, docs

# Alias for old app.py
def run_rag(query):
    ans, docs = get_answer(query)
    return ans
