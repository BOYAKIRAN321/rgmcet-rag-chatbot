from flask import Flask, request, jsonify
from flask_cors import CORS
from .rag_pipeline import get_answer, run_rag

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def home():
    return jsonify({"status":"RGMCET RAG Chatbot is Running!"})

@app.route("/ask", methods=["POST", "OPTIONS"])
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json
    query = data.get("query", "") or data.get("message", "")
    if not query:
        return jsonify({"answer": "Please ask a question"}), 400
    try:
        answer, docs = get_answer(query)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
