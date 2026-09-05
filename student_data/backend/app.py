from flask import Flask, request, jsonify, send_from_directory
from backend.rag_pipeline import run_rag
import os
import traceback

app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        query = data.get("query")
        if not query:
            return jsonify({"error": "Query required"}), 400
        
        print(f"Query: {query}")
        answer = run_rag(query)
        print(f"Answer: {answer[:100]}")
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"ERROR in /ask: {e}")
        traceback.print_exc()
        return jsonify({"answer": f"Server Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
