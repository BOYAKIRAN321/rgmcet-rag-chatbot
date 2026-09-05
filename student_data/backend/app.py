from flask import Flask, request, jsonify
from flask_cors import CORS
from.rag_pipeline import get_answer, run_rag

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"status": "RGMCET RAG Chatbot is Running!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "") or data.get("message", "")
    if not query:
        return jsonify({"error": "No query"}), 400
    try:
        answer, docs = get_answer(query)
        sources = [d.page_content[:200] for d in docs]
        return jsonify({"answer": answer, "sources": sources})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
