from flask import Flask, request, jsonify, send_from_directory
from rag_pipeline import run_rag
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
# Serve index.html
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Serve other static files (CSS, JS)
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Query required"}), 400

    answer = run_rag(query)
    print("heyy hii",answer)

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
