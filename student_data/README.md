# Student-Retrieval-chatbot-using-RAG-and-LLM

![Uploading image.png…]()

# 🎓 Student Retrieval Chatbot using RAG, FAISS & LLM

## 📌 Project Overview

The Student Retrieval Chatbot is an AI-powered question answering system built using Retrieval-Augmented Generation (RAG).  
It allows users to query student-related academic information such as CGPA, subjects, backlogs, and semester details.

Instead of relying solely on a Large Language Model (LLM), the system retrieves relevant data from a structured knowledge base using semantic search and then generates context-aware responses.

---

## 🧠 Core Technologies Used

- 🔹 Large Language Model (LLM) – Groq (LLaMA-based model)
- 🔹 FAISS – Facebook AI Similarity Search (Vector Database)
- 🔹 RAG Architecture (Retrieval-Augmented Generation)
- 🔹 Python (Backend)
- 🔹 HTML, CSS, JavaScript (Frontend)
- 🔹 Embedding Models for Semantic Search

---

## ⚙️ System Architecture

1. Data Ingestion  
   - Student data and academic documents are processed.
   - Text is extracted and chunked.

2. Embedding Generation  
   - Text chunks are converted into vector embeddings.

3. Vector Storage  
   - Embeddings are stored in FAISS for efficient similarity search.

4. Query Processing  
   - User question is converted into embedding.
   - FAISS retrieves top relevant chunks.

5. Response Generation  
   - Retrieved context + user query is passed to LLM.
   - LLM generates accurate, context-based response.

---

## 🔍 Why RAG?

Traditional LLMs may hallucinate or generate generic answers.  
By integrating FAISS-based retrieval:

- Responses are grounded in actual data.
- Accuracy improves significantly.
- Hallucination is reduced.
- System becomes scalable and domain-specific.

---

## 🚀 Key Features

✔ Student data retrieval by semester  
✔ CGPA and backlog analysis  
✔ Semantic search-based question answering  
✔ Fast vector similarity search using FAISS  
✔ Clean frontend chat interface  
✔ Secure environment variable handling for API keys  

---

## 🛠 Example Query

User: "What is the CGPA of II Year II Sem?"  
System:
1. Retrieves relevant student record from FAISS
2. Sends context to LLM
3. Generates structured response

---

## 📊 Technical Highlights

- Implemented end-to-end RAG pipeline
- Designed modular backend architecture
- Optimized chunking strategy for better retrieval
- Integrated Groq LLM API securely
- Built custom retriever and embedding pipeline

---

## 🎯 Future Improvements

- Add authentication system
- Deploy on cloud (AWS / Render / Railway)
- Add multi-user student database
- Improve retrieval ranking using hybrid search

---

## 👩‍💻 Author

Developed as part of an AI-based academic retrieval system project.
