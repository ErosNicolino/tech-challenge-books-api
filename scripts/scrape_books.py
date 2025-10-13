"""
scrape_books.py
---------------
Script de Web Scraping para coletar informações de livros do site Books to Scrape.
Os dados são armazenados no arquivo data/books.csv.

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

# ===== Constantes =====
BASE_URL = "https://books.toscrape.com/"
CATALOGUE_URL = BASE_URL + "catalogue/"
CSV_FILEPATH = "data/books.csv"
DELAY_BETWEEN_REQUESTS = 1  # em segundos

# ===== Configuração do Logging =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)


# ===== Funções de scraping =====
def get_soup(url: str) -> BeautifulSoup:
    """
    Faz requisição HTTP para a URL fornecida e retorna um objeto BeautifulSoup.

    Args:
        url (str): URL da página a ser baixada.

    Returns:
        BeautifulSoup: Objeto de parsing HTML.
    """
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def parse_book(article: BeautifulSoup, category: str) -> Dict[str, str]:
    """
    Extrai informações de um livro a partir do HTML.

    Args:
        article (BeautifulSoup): Elemento HTML do livro.
        category (str): Nome da categoria do livro.

    Returns:
        Dict[str, str]: Dicionário com os dados do livro.
    """
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
    """
    Coleta todos os livros de uma categoria, incluindo paginação.

    Args:
        category_url (str): URL da categoria.
        category_name (str): Nome da categoria.

    Returns:
        List[Dict[str, str]]: Lista de livros da categoria.
    """
    books = []
    page_url = category_url

    while True:
        logging.info(f"Coletando livros da categoria '{category_name}' -> {page_url}")
        soup = get_soup(page_url)

        articles = soup.select("article.product_pod")
        for article in articles:
            books.append(parse_book(article, category_name))

        # Verifica se há próxima página
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            page_url = category_url.replace("index.html", next_btn["href"])
        else:
            break

        time.sleep(DELAY_BETWEEN_REQUESTS)

    return books


def scrape_books() -> List[Dict[str, str]]:
    """
    Coleta todos os livros de todas as categorias do site.

    Returns:
        List[Dict[str, str]]: Lista completa de livros coletados.
    """
    all_books = []
    logging.info("Iniciando scraping do site Books to Scrape...")
    soup = get_soup(BASE_URL)

    categories = soup.select("div.side_categories ul li ul li a")
    for cat in categories:
        category_name = cat.text.strip()
        category_url = BASE_URL + cat["href"]
        all_books.extend(scrape_category(category_url, category_name))

    logging.info(f"Total de livros coletados: {len(all_books)}")
    return all_books


def save_to_csv(books: List[Dict[str, str]], filepath: str = CSV_FILEPATH) -> None:
    """
    Salva os livros coletados em um arquivo CSV.

    Args:
        books (List[Dict[str, str]]): Lista de livros a serem salvos.
        filepath (str): Caminho do arquivo CSV.
    """
    if not books:
        logging.warning("Nenhum livro para salvar.")
        return

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=books[0].keys())
        writer.writeheader()
        writer.writerows(books)

    logging.info(f"Arquivo CSV salvo em {filepath}")


# ===== Execução principal =====
if __name__ == "__main__":
    books_data = scrape_books()
    if books_data:
        save_to_csv(books_data)
