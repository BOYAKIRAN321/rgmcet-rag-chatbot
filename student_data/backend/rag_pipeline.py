import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

# Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load FAISS - path fix
# Render lo root = student_data/
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = BASE_DIR / "faiss_index"

vector_db = FAISS.load_local(
    str(DB_PATH), 
    embeddings, 
    allow_dangerous_deserialization=True
)

# Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.2
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=False
)

def run_rag(query):
    result = qa_chain.invoke({"query": query})
    return result["result"]
