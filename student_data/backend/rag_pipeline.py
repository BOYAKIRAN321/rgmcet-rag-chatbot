from langchain_ollama import OllamaLLM
import time

llm = OllamaLLM(model="mistral", temperature=0)

def run_rag(query):
    q = query.lower().strip()

    # 1. GREETING
    if q in ["hi", "hii", "hello", "hey", "good morning", "good evening"]:
        return "👋 Hi! Welcome to RGMCET Academic Assistant."

    if any(word in q for word in ["thank you", "thanks", "bye"]):
        return "😊 You're welcome!"

    # 2. 🔥 TOPPER / TOTAL / BACKLOGS - BEFORE SEARCH (Idhi main fix)
    if "total students" in q or "how many students" in q:
        from retriever import count_total_students
        return f"📊 Total Students: {count_total_students()}"

    if "topper" in q or "top rank" in q or "highest cgpa" in q or "topper of the class" in q:
        from retriever import get_topper
        return get_topper()

    if "highest backlogs" in q or "more backlogs" in q or "most backlogs" in q:
        from retriever import get_max_backlogs
        return get_max_backlogs()

    # 3. Ippudu search
    from retriever import retrieve_docs
    retrieval_start = time.time()
    docs = retrieve_docs(query)
    print("retrieved context is", docs)
    print(f"📂 Retrieval Time: {time.time() - retrieval_start:.4f} seconds")
    
    if docs == "general":
        return "Sorry, no records found. Ask with roll number."

    if isinstance(docs, str):
        return docs

    if isinstance(docs, list) and docs:
        if isinstance(docs[0], dict):
            context = str(docs)
        else:
            context = "\n\n".join(doc.page_content for doc in docs)
    else:
        return "⚠️ No data found."

    prompt = f"""
You are RGMCET Academic Assistant.
Use ONLY provided context. Do NOT invent marks.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""
    return llm.invoke(prompt)

if __name__ == "__main__":
    while True:
        q = input("Ask: ")
        if q.lower() == "exit":
            break
        print(run_rag(q))
