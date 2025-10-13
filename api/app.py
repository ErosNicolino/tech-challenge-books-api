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
    return {
        "message": "API Books Tech Challenge is running!",
        "endpoints": {
            "/api/v1/books": "List all books",
            "/api/v1/books/<id>": "Get book details by ID",
            "/api/v1/books/search": "Search books by title and/or category",
            "/api/v1/categories": "List all categories",
            "/api/v1/health": "API health check",
            "/api/v1/stats/overview": "General statistics",
            "/api/v1/stats/categories": "Statistics by category",
            "/api/v1/books/top-rated": "Top rated books",
            "/api/v1/books/price-range": "Books by price range",
            "/api/v1/ml/features": "ML features",
            "/api/v1/ml/training-data": "ML training dataset",
            "/api/v1/ml/predictions": "ML predictions"
        }
    }

# ===== Listar todos os livros =====
@app.route("/api/v1/books", methods=["GET"])
def get_books():
    return jsonify(books_df.to_dict(orient="records"))

# ===== Detalhar um livro específico =====
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        abort(404, description="Book not found")
    return jsonify(book.to_dict(orient="records")[0])

# ===== Buscar livros por título e/ou categoria =====
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

# ===== Listar todas as categorias =====
@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    categories = books_df['category'].dropna().unique().tolist()
    return jsonify(categories)

# ===== Health Check =====
@app.route("/api/v1/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "books_count": len(books_df)})

# ===== ENDPOINTS OPCIONAIS / AVANÇADOS =====

# Estatísticas gerais
@app.route('/api/v1/stats/overview', methods=['GET'])
def stats_overview():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    total_books = len(df)
    average_price = df['price'].str.replace('£','').astype(float).mean()
    rating_distribution = df['rating'].value_counts().to_dict()
    return jsonify({
        "total_books": total_books,
        "average_price": round(average_price, 2),
        "rating_distribution": rating_distribution
    })

# Estatísticas por categoria
@app.route('/api/v1/stats/categories', methods=['GET'])
def stats_categories():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    category_stats = df.groupby('category').agg({
        'title': 'count',
        'price': 'mean'
    }).rename(columns={'title': 'books_count', 'price': 'average_price'})
    category_stats['average_price'] = category_stats['average_price'].round(2)
    return jsonify(category_stats.to_dict(orient='index'))

# Top rated books
@app.route('/api/v1/books/top-rated', methods=['GET'])
def top_rated_books():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    rating_map = {"One": 1, "Two":2, "Three":3, "Four":4, "Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    top_books = df.sort_values(by='rating_num', ascending=False).head(10)
    return jsonify(top_books.to_dict(orient='records'))

# Livros por faixa de preço
@app.route('/api/v1/books/price-range', methods=['GET'])
def books_price_range():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    min_price = float(request.args.get('min', 0))
    max_price = float(request.args.get('max', 1000))
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    filtered = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
    return jsonify(filtered.to_dict(orient='records'))

# ML-Ready: Features
@app.route('/api/v1/ml/features', methods=['GET'])
def ml_features():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    df['category_code'] = df['category'].astype('category').cat.codes
    features = df[['price', 'rating_num', 'category_code']]
    return jsonify(features.to_dict(orient='records'))

# ML-Ready: Training Data
@app.route('/api/v1/ml/training-data', methods=['GET'])
def ml_training_data():
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    df['category_code'] = df['category'].astype('category').cat.codes
    training_data = df[['price', 'category_code', 'rating_num']]
    return jsonify(training_data.to_dict(orient='records'))

# ML-Ready: Predictions (placeholder)
@app.route('/api/v1/ml/predictions', methods=['POST'])
def ml_predictions():
    data = request.get_json()
    prediction = {"predicted_price": 42.0}
    return jsonify(prediction)

# ===== Execução local =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
