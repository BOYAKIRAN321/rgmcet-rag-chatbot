from rag_pipeline import build_rag_chain

print("\n🎓 Student Academic RAG System Ready!")
print("Tip: Include student hall ticket number in your question.\n")

while True:
    query = input("Ask a question: ")

    if query.lower() == "exit":
        break

    qa_chain = build_rag_chain(query)   # ✅ pass query here
    answer = qa_chain.invoke({"query": query})["result"]

    print("\n📘 Answer:\n", answer, "\n")
