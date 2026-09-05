import os
import pathlib
import requests
from langchain_community.vectorstores import FAISS

# Simple HF API - No numpy, no crash!
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
                # HF returns list of floats
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    # average if 2D
                    emb = [sum(col)/len(col) for col in zip(*data)] if isinstance(data[0][0], list) else data
                    # simple mean
                    if len(data[0]) > 0 and isinstance(data[0][0], float):
                        result.append(data[0] if len(data) == 1 else [sum(x)/len(x) for x in zip(*data)])
                    else:
                        result.append(data)
                else:
                    result.append(data)
            except Exception as e:
                print(f"Embed error: {e}")
                result.append([0.0]*384)
        return result

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

    from langchain_groq import ChatGroq

    embeddings = HF_API_Embeddings()
    BASE = pathlib.Path(__file__).parent.parent

    # Check both places where you uploaded
    for path in [BASE / "faiss_index", BASE, pathlib.Path("student_data/faiss_index"), pathlib.Path("student_data")]:
        if (path / "index.faiss").exists():
            DB_PATH = path
            print(f"✅ FAISS FOUND at {DB_PATH}")
            break
    else:
        raise FileNotFoundError("index.faiss not found!")

    vector_db = FAISS.load_local(str(DB_PATH), embeddings, allow_dangerous_deserialization=True)
    vector_db.embedding_function = embeddings

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        temperature=0.1
    )
    print("✅ Models loaded!")

def get_answer(query):
    load_models()
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([d.page_content for d in docs])
    prompt = f"Use this context to answer:\n{context}\n\nQuestion: {query}"
    resp = llm.invoke(prompt)
    return resp.content, docs
