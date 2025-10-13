import os
from flask import Flask, jsonify, request, abort, render_template
from flasgger import Swagger
import pandas as pd
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

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
            "responsible": "Nicolino",
            "email": "seuemail@exemplo.com",
            "url": "https://github.com/seuusuario"
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

# ===== Página inicial =====
@app.route("/")
def home():
    """Home page of the API"""
    return render_template("index.html")

# ===== Carregamento do CSV =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/books.csv')

try:
    books_df = pd.read_csv(CSV_PATH, encoding='utf-8')
except FileNotFoundError:
    print(f"Arquivo CSV não encontrado em {CSV_PATH}")
    books_df = pd.DataFrame()

if not books_df.empty and 'price' in books_df.columns:
    books_df['price'] = books_df['price'].str.replace('Â£','£', regex=False)

if 'id' not in books_df.columns:
    books_df.insert(0, 'id', range(1, len(books_df) + 1))

# ===== Usuários de teste =====
USERS = {"admin": "password123"}

# ===== Rota de login =====
@app.route("/api/v1/auth/login", methods=["POST"])
def login():
    """
    User login to get JWT token
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: admin
            password:
              type: string
              example: password123
    responses:
      200:
        description: JWT token returned
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    if USERS.get(username) != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# ===== Endpoints Core =====
@app.route("/api/v1/books", methods=["GET"])
def get_books():
    """
    List all books
    ---
    tags:
      - Books
    responses:
      200:
        description: List of books
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              price:
                type: string
              rating:
                type: string
              category:
                type: string
              availability:
                type: string
    """
    return jsonify(books_df.to_dict(orient="records"))

@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    """
    Get book details by ID
    ---
    tags:
      - Books
    parameters:
      - name: book_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Book details
        schema:
          type: object
          properties:
            id: {type: integer}
            title: {type: string}
            price: {type: string}
            rating: {type: string}
            category: {type: string}
            availability: {type: string}
      404:
        description: Book not found
    """
    book = books_df[books_df['id'] == book_id]
    if book.empty:
        abort(404, description="Book not found")
    return jsonify(book.to_dict(orient="records")[0])

@app.route("/api/v1/books/search", methods=["GET"])
def search_books():
    """
    Search books by title or category
    ---
    tags:
      - Books
    parameters:
      - name: title
        in: query
        type: string
        required: false
      - name: category
        in: query
        type: string
        required: false
    responses:
      200:
        description: Filtered books
        schema:
          type: array
    """
    title = request.args.get("title", "").lower()
    category = request.args.get("category", "").lower()
    
    filtered = books_df
    if title:
        filtered = filtered[filtered['title'].str.lower().str.contains(title)]
    if category:
        filtered = filtered[filtered['category'].str.lower().str.contains(category)]
    
    return jsonify(filtered.to_dict(orient="records"))

@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    """
    List all categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories
        schema:
          type: array
          items:
            type: string
    """
    categories = books_df['category'].dropna().unique().tolist()
    return jsonify(categories)

@app.route("/api/v1/health", methods=["GET"])
def health():
    """
    API Health Check
    ---
    tags:
      - System
    responses:
      200:
        description: Status and books count
        schema:
          type: object
          properties:
            status: {type: string}
            books_count: {type: integer}
    """
    return jsonify({"status": "ok", "books_count": len(books_df)})

# ===== Endpoints Insights =====
@app.route('/api/v1/stats/overview', methods=['GET'])
def stats_overview():
    """
    General statistics overview
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Overview stats
    """
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
    """
    Statistics by category
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Category stats
    """
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
    """
    Top rated books
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Top 10 rated books
    """
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    df = books_df.copy()
    rating_map = {"One":1,"Two":2,"Three":3,"Four":4,"Five":5}
    df['rating_num'] = df['rating'].map(rating_map)
    top_books = df.sort_values(by='rating_num', ascending=False).head(10)
    return jsonify(top_books.to_dict(orient='records'))

@app.route('/api/v1/books/price-range', methods=['GET'])
def books_price_range():
    """
    Books by price range
    ---
    tags:
      - Statistics
    parameters:
      - name: min
        in: query
        type: number
        required: false
        default: 0
      - name: max
        in: query
        type: number
        required: false
        default: 1000
    responses:
      200:
        description: Books filtered by price range
    """
    if books_df.empty:
        return jsonify({"error": "No data available"}), 404
    min_price = float(request.args.get('min', 0))
    max_price = float(request.args.get('max', 1000))
    df = books_df.copy()
    df['price'] = df['price'].str.replace('£','').astype(float)
    filtered = df[(df['price'] >= min_price) & (df['price'] <= max_price)]
    return jsonify(filtered.to_dict(orient='records'))

# ===== Endpoints ML-ready =====
@app.route('/api/v1/ml/features', methods=['GET'])
def ml_features():
    """
    ML Features
    ---
    tags:
      - ML
    responses:
      200:
        description: Features for ML
    """
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
    """
    ML Training Dataset
    ---
    tags:
      - ML
    responses:
      200:
        description: Training data for ML
    """
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
    """
    ML Predictions (JWT protected)
    ---
    tags:
      - ML
    security:
      - Bearer: []
    parameters:
      - name: features
        in: body
        required: true
        schema:
          type: object
          properties:
            price:
              type: number
              example: 25.0
            category_code:
              type: integer
              example: 3
            rating_num:
              type: integer
              example: 4
    responses:
      200:
        description: Predicted value
        schema:
          type: object
          properties:
            predicted_price:
              type: number
              example: 42.0
      401:
        description: Unauthorized, missing or invalid token
    """
    data = request.get_json()
    prediction = {"predicted_price": 42.0}
    return jsonify(prediction)

# ===== Execução local =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
