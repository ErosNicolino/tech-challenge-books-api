import os
import logging
import subprocess
from flask import Flask, jsonify, request, abort, render_template
from flasgger import Swagger
import pandas as pd
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)

# ===== Configuração base =====
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# ===== Config JWT =====
app.config["JWT_SECRET_KEY"] = "fvIenJ1ht1Vszmp15qZOGyK-flTC_2l_hshQ8GQu1ME"
jwt = JWTManager(app)

# ===== Configuração Swagger =====
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "Tech Challenge - API Books",
        "description": "API pública para consulta de livros extraídos do site Books to Scrape.",
        "version": "1.0.0",
        "contact": {
            "responsible": "Eros Nicolino",
            "email": "erosnicolino@icloud.com",
            "url": "https://github.com/ErosNicolino"
        },
        "termsOfService": "https://books.toscrape.com/"
    },
    "host": "tech-challenge-books-api-mkqn.onrender.com",
    "basePath": "/",
    "schemes": ["https"],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'"
        }
    }
})

# ===== Configuração de Logs =====
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("API iniciada com sucesso.")

# ===== Página inicial =====
@app.route("/")
def home():
    logging.info("Rota '/' acessada.")
    return render_template("index.html")

# ===== Carregamento do CSV =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/books.csv')

try:
    books_df = pd.read_csv(CSV_PATH, encoding='utf-8')
except FileNotFoundError:
    logging.error(f"Arquivo CSV não encontrado em {CSV_PATH}")
    books_df = pd.DataFrame()

if not books_df.empty and 'price' in books_df.columns:
    books_df['price'] = books_df['price'].str.replace('Â£', '£', regex=False)

if 'id' not in books_df.columns:
    books_df.insert(0, 'id', range(1, len(books_df) + 1))

# ===== Usuários de teste =====
USERS = {"admin": "password123"}

# ===== Rota de login =====
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    logging.info("Rota '/api/v1/auth/login' acessada.")
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logging.warning("Tentativa de login com campos vazios.")
        return jsonify({"msg": "Missing username or password"}), 400

    if USERS.get(username) != password:
        logging.warning(f"Tentativa de login inválida: {username}")
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    logging.info(f"Usuário '{username}' autenticado com sucesso.")
    return jsonify(access_token=access_token, refresh_token=refresh_token)

# ===== Refresh JWT =====
@app.route("/api/v1/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    logging.info(f"Token de acesso renovado para {current_user}.")
    return jsonify(access_token=new_access_token)

# ===== Scraping Trigger protegido =====
@app.route("/api/v1/scraping/trigger", methods=["POST"])
@jwt_required()
def trigger_scraping():
    current_user = get_jwt_identity()
    logging.info(f"Rota '/api/v1/scraping/trigger' acessada por {current_user}.")
    try:
        subprocess.run(["python", "scripts/scrape_books.py"], check=True)
        logging.info("Scraping concluído com sucesso.")
        return jsonify({"msg": "Scraping concluído com sucesso."})
    except subprocess.CalledProcessError as e:
        logging.error(f"Erro no scraping: {e}")
        return jsonify({"error": "Falha ao executar scraping"}), 500

# ===== Endpoints Core =====
@app.route("/api/v1/books", methods=["GET"])
def get_books():
    logging.info("Rota '/api/v1/books' acessada.")
    return jsonify(books_df.to_dict(orient="records"))

@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    logging.info(f"Rota '/api/v1/books/{book_id}' acessada.")
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        logging.warning(f"Livro com ID {book_id} não encontrado.")
        abort(404, description="Book not found")
    return jsonify(book.to_dict(orient="records")[0])

@app.route("/api/v1/books/search", methods=["GET"])
def search_books():
    title = request.args.get("title", "").lower()
    category = request.args.get("category", "").lower()
    logging.info(f"Rota '/api/v1/books/search' acessada com filtros: title={title}, category={category}")

    filtered = books_df
    if title:
        filtered = filtered[filtered['title'].str.lower().str.contains(title)]
    if category:
        filtered = filtered[filtered['category'].str.lower().str.contains(category)]

    return jsonify(filtered.to_dict(orient="records"))

@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    logging.info("Rota '/api/v1/categories' acessada.")
    categories = books_df['category'].dropna().unique().tolist()
    return jsonify(categories)

@app.route("/api/v1/health", methods=["GET"])
def health():
    logging.info("Rota '/api/v1/health' acessada.")
    return jsonify({"status": "ok", "books_count": len(books_df)})

# ===== Endpoints Insights =====
@app.route('/api/v1/stats/overview', methods=['GET'])
def stats_overview():
    logging.info("Rota '/api/v1/stats/overview' acessada.")
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

@app.route('/api/v1/stats/categories', methods=['GET'])
def stats_categories():
    logging.info("Rota '/api/v1/stats/categories' acessada.")
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

@app.route('/api/v1/books/top-rated', methods=['GET'])
def top_rated_books():
    logging.info("Rota '/api/v1/books/top-rated' acessada.")
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    top_books = df.sort_values(by='rating_num', ascending=False).head(10)
    return jsonify(top_books.to_dict(orient='records'))

@app.route('/api/v1/books/price-range', methods=['GET'])
def books_price_range():
    min_price = float(request.args.get('min', 0))
    max_price = float(request.args.get('max', 1000))
    logging.info(f"Rota '/api/v1/books/price-range' acessada. Filtros: min={min_price}, max={max_price}")

    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    filtered = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
    return jsonify(filtered.to_dict(orient='records'))

# ===== Endpoints ML-ready =====
@app.route('/api/v1/ml/features', methods=['GET'])
def ml_features():
    logging.info("Rota '/api/v1/ml/features' acessada.")
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    df['category_code'] = df['category'].astype('category').cat.codes
    features = df[['price','rating_num','category_code']]
    return jsonify(features.to_dict(orient='records'))

@app.route('/api/v1/ml/training-data', methods=['GET'])
def ml_training_data():
    logging.info("Rota '/api/v1/ml/training-data' acessada.")
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    df['category_code'] = df['category'].astype('category').cat.codes
    training_data = df[['price','category_code','rating_num']]
    return jsonify(training_data.to_dict(orient='records'))

@app.route('/api/v1/ml/predictions', methods=['POST'])
@jwt_required()
def ml_predictions():
    current_user = get_jwt_identity()
    logging.info(f"Rota '/api/v1/ml/predictions' acessada por {current_user}.")
    data = request.get_json()
    # Placeholder: implementar modelo real futuramente
    prediction = {"predicted_price": 42.0}
    return jsonify(prediction)

# ===== Execução local =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"API rodando localmente na porta {port}.")
    app.run(host="0.0.0.0", port=port)
