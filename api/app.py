import os
from flask import Flask, jsonify, request, abort, render_template
import pandas as pd

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# ===== Rota raiz (HTML) =====
@app.route("/")
def home():
    return render_template("index.html")

# Caminho absoluto do CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/books.csv')

# Carregar CSV
try:
    books_df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    print(f"Arquivo CSV não encontrado em {CSV_PATH}")
    books_df = pd.DataFrame()

# Adicionar ID se não existir
if 'id' not in books_df.columns:
    books_df.insert(0, 'id', range(1, len(books_df) + 1))

# ===== Endpoint de info da API =====
@app.route("/api/v1", methods=["GET"])
def api_info():
    return {
        "message": "API Books Tech Challenge is running!",
        "endpoints": {
            "/api/v1/books": "List all books",
            "/api/v1/books/<id>": "Get book details by ID",
            "/api/v1/books/search": "Search books by title and/or category",
            "/api/v1/categories": "List all categories",
            "/api/v1/health": "API health check"
        }
    }

# ===== Listar todos os livros =====
@app.route("/api/v1/books", methods=["GET"])
def get_books():
    return jsonify(books_df.to_dict(orient="records"))

# ===== Detalhe de um livro =====
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        abort(404, description="Book not found")
    return jsonify(book.to_dict(orient="records")[0])

# ===== Buscar livros =====
@app.route("/api/v1/books/search", methods=["GET"])
def search_books():
    title = request.args.get("title", "").lower()
    category = request.args.get("category", "").lower()
    
    filtered = books_df
    if title:
        filtered = filtered[filtered['title'].str.lower().str.contains(title)]
    if category:
        filtered = filtered[filtered['category'].str.lower().str.contains(category)]
    
    return jsonify(filtered.to_dict(orient="records"))

# ===== Listar categorias =====
@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    categories = books_df['category'].dropna().unique().tolist()
    return jsonify(categories)

# ===== Health check =====
@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "books_count": len(books_df)})

# ===== Rodar no Heroku =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
