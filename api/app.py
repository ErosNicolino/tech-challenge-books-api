from flask import Flask, jsonify, request
import pandas as pd
import os

app = Flask(__name__)

# Caminho seguro para o CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, '../data/books.csv')

# Carrega o CSV
books_df = pd.read_csv(CSV_PATH)
books = books_df.to_dict(orient='records')

@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "total_books": len(books)})

@app.route('/api/v1/books', methods=['GET'])
def list_books():
    return jsonify(books)

@app.route('/api/v1/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    if 0 <= book_id < len(books):
        return jsonify(books[book_id])
    else:
        return jsonify({"error": "Book not found"}), 404

@app.route('/api/v1/books/search', methods=['GET'])
def search_books():
    title = request.args.get('title', '').lower()
    category = request.args.get('category', '').lower()
    results = [b for b in books if title in b['title'].lower() and category in b['category'].lower()]
    return jsonify(results)

@app.route('/api/v1/categories', methods=['GET'])
def list_categories():
    categories = sorted(list(set(b['category'] for b in books)))
    return jsonify(categories)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
