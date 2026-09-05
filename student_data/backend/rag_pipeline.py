import os
import pathlib
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

BASE_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = BASE_DIR / "faiss_index"

vector_db = FAISS.load_local(str(DB_PATH), embeddings, allow_dangerous_deserialization=True)

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.2
)

def run_rag(query):
    docs = vector_db.similarity_search(query, k=3)
    context = "\n\n".join([d.page_content for d in docs])
    prompt = f"You are RGMCET assistant. Context: {context}\n\nQuestion: {query}\nAnswer:"
    result = llm.invoke(prompt)
    return result.content
