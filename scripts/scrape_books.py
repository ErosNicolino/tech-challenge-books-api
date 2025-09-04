"""
scrape_books.py
---------------
Script de web scraping para coletar informações de livros no site Books to Scrape.
O resultado final é salvo em data/books.csv.

Coleta:
- Título
- Preço
- Avaliação (rating)
- Disponibilidade
- Categoria
- URL da imagem
"""

import os
import csv
import time
import logging
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/"

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


def get_soup(url: str) -> BeautifulSoup:
    """Baixa uma página e retorna o objeto BeautifulSoup."""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def parse_book(article, category: str) -> Dict[str, str]:
    """Extrai informações de um livro a partir do HTML."""
    title = article.h3.a["title"]
    price = article.find("p", class_="price_color").text.strip()
    availability = article.find("p", class_="instock availability").text.strip()
    rating = article.p["class"][1] 
    image_url = BASE_URL + article.img["src"].replace("../", "")

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "category": category,
        "image_url": image_url
    }


def scrape_category(category_url: str, category_name: str) -> List[Dict[str, str]]:
    """Coleta todos os livros de uma categoria (com paginação)."""
    books = []
    page_url = category_url

    while True:
        logging.info(f"Coletando {category_name} -> {page_url}")
        soup = get_soup(page_url)

        articles = soup.select("article.product_pod")
        for article in articles:
            book = parse_book(article, category_name)
            books.append(book)

        # Verificar se existe próxima página
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            page_url = category_url.replace("index.html", next_btn["href"])
        else:
            break

        time.sleep(1)  # Respeitar o servidor

    return books


def scrape_books() -> List[Dict[str, str]]:
    """Coleta todos os livros de todas as categorias do site."""
    all_books = []

    logging.info("Iniciando scraping do site Books to Scrape...")
    soup = get_soup(BASE_URL)

    # Listar categorias
    categories = soup.select("div.side_categories ul li ul li a")

    for cat in categories:
        category_name = cat.text.strip()
        category_url = BASE_URL + cat["href"]
        books = scrape_category(category_url, category_name)
        all_books.extend(books)

    logging.info(f"Total de livros coletados: {len(all_books)}")
    return all_books


def save_to_csv(books: List[Dict[str, str]], filepath: str = "data/books.csv") -> None:
    """Salva os dados coletados em CSV."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

    logging.info(f"Arquivo CSV salvo em {filepath}")


if __name__ == "__main__":
    books_data = scrape_books()
    if books_data:
        save_to_csv(books_data)
