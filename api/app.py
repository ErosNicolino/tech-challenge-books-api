import os
from flask import Flask, jsonify, request, abort, render_template
from flasgger import Swagger
import pandas as pd

# ===== Configuração base =====
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# ===== Configuração do Swagger =====
swagger = Swagger(app, template={
    "info": {
        "title": "Tech Challenge - API Books",
        "description": "API pública para consulta de livros extraídos do site Books to Scrape.",
        "version": "1.0.0",
        "contact": {
            "responsible": "Nicolino",
            "email": "seuemail@exemplo.com",
            "url": "https://github.com/seuusuario"
        },
        "termsOfService": "https://books.toscrape.com/",
    },
    "host": "tech-challenge-books-api-mkqn.onrender.com", 
    "basePath": "/", 
    "schemes": ["https"] 
})

# ===== Página inicial (HTML) =====
@app.route("/")
def home():
    """Página inicial da API"""
    return render_template("index.html")

# ===== Caminho e carregamento do CSV =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/books.csv')

try:
    books_df = pd.read_csv(CSV_PATH, encoding='utf-8')
except FileNotFoundError:
    print(f"Arquivo CSV não encontrado em {CSV_PATH}")
    books_df = pd.DataFrame()

# Corrigir símbolo de libra
if not books_df.empty and 'price' in books_df.columns:
    books_df['price'] = books_df['price'].str.replace('Â£', '£', regex=False)

# Adicionar ID se não existir
if 'id' not in books_df.columns:
    books_df.insert(0, 'id', range(1, len(books_df) + 1))

# ===== Rota de informações gerais =====
@app.route("/api/v1", methods=["GET"])
def api_info():
    """
    Informações gerais sobre a API.
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API em funcionamento.
    """
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
    """
    Lista todos os livros disponíveis.
    ---
    tags:
      - Livros
    responses:
      200:
        description: Lista de livros carregada com sucesso.
        examples:
          application/json:
            [
              {
                "id": 1,
                "title": "A Light in the Attic",
                "price": "£51.77",
                "rating": "Three",
                "category": "Poetry",
                "availability": "In stock"
              }
            ]
    """
    return jsonify(books_df.to_dict(orient="records"))

# ===== Detalhar um livro específico =====
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """
    Retorna detalhes de um livro pelo ID.
    ---
    tags:
      - Livros
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
        description: ID do livro.
    responses:
      200:
        description: Detalhes do livro retornados com sucesso.
      404:
        description: Livro não encontrado.
    """
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        abort(404, description="Book not found")
    return jsonify(book.to_dict(orient="records")[0])

# ===== Buscar livros por título e/ou categoria =====
@app.route("/api/v1/books/search", methods=["GET"])
def search_books():
    """
    Busca livros por título e/ou categoria.
    ---
    tags:
      - Livros
    parameters:
      - name: title
        in: query
        type: string
        required: false
        description: Título (ou parte) do livro.
      - name: category
        in: query
        type: string
        required: false
        description: Categoria do livro.
    responses:
      200:
        description: Lista de livros filtrados com sucesso.
    """
    title = request.args.get("title", "").lower()
    category = request.args.get("category", "").lower()
    
    filtered = books_df
    if title:
        filtered = filtered[filtered['title'].str.lower().str.contains(title)]
    if category:
        filtered = filtered[filtered['category'].str.lower().str.contains(category)]
    
    return jsonify(filtered.to_dict(orient="records"))

# ===== Listar todas as categorias =====
@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    """
    Lista todas as categorias disponíveis.
    ---
    tags:
      - Categorias
    responses:
      200:
        description: Lista de categorias carregada com sucesso.
        examples:
          application/json:
            ["Poetry", "Travel", "Mystery"]
    """
    categories = books_df['category'].dropna().unique().tolist()
    return jsonify(categories)

# ===== Health Check =====
@app.route("/api/v1/health", methods=["GET"])
def health():
    """
    Verifica o status da API e contagem de livros.
    ---
    tags:
      - Sistema
    responses:
      200:
        description: API saudável e funcional.
        examples:
          application/json:
            {"status": "ok", "books_count": 1000}
    """
    return jsonify({"status": "ok", "books_count": len(books_df)})

# ===== Execução local =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
