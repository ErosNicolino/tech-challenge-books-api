# Tech Challenge - API Books

## Descrição do Projeto

Este projeto é parte do **Tech Challenge** e consiste em uma **API RESTful em Flask** que fornece dados de livros extraídos do site [Books to Scrape](https://books.toscrape.com/).

A API é projetada para ser escalável e pronta para consumo por cientistas de dados, sistemas de recomendação de livros ou aplicações web. Possui endpoints para listar, buscar e consultar detalhes de livros, listar categorias, verificar a saúde da API e endpoints ML-ready com autenticação JWT.

---

## Estrutura do Projeto

```
tech-challenge-books-api/
│
├── .venv/                  # Ambiente virtual (não versionar)
├── api/
│   └── app.py              # API Flask principal
├── data/
│   └── books.csv           # CSV com dados coletados
├── scripts/
│   └── scrape_books.py     # Script de web scraping
├── static/
│   └── style.css           # Arquivos estáticos da interface
├── templates/
│   └── index.html          # Página inicial da API
├── docs/
│   └── diagrama-visual.png # Diagrama do pipeline e arquitetura
├── tests/                  # Testes unitários (opcional)
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação do projeto
```

---

## Diagrama do Pipeline

![Diagrama do Pipeline](./docs/diagrama-visual.png)

---

## Pré-requisitos

* Python 3.10+
* [Git](https://git-scm.com/)
* [pip](https://pip.pypa.io/en/stable/)

---

## Instalação e Execução Local

1. **Clonar o repositório:**

```bash
git clone https://github.com/ErosNicolino/tech-challenge-books-api.git
cd tech-challenge-books-api
```

2. **Criar e ativar o ambiente virtual:**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Instalar dependências:**

```bash
pip install -r requirements.txt
```

4. **Executar a API:**

```bash
python api/app.py
```

A API estará disponível em **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**.

---

## Deploy Público

[Render Deployment](https://tech-challenge-books-api-mkqn.onrender.com)

---

## Documentação Interativa (Swagger)

[Swagger UI](https://tech-challenge-books-api-mkqn.onrender.com/apidocs)

---

## Endpoints da API

### Autenticação JWT

#### Login

```http
POST /api/v1/auth/login
```

**Request Body:**

```json
{
  "username": "admin",
  "password": "password123"
}
```

**Response:**

```json
{
  "access_token": "seu_token_jwt_aqui"
}
```

---

### Core Endpoints

#### Listar todos os livros

```http
GET /api/v1/books
```

**Query Params (opcional):**

* `page` → número da página
* `limit` → quantidade de livros por página

**Exemplo de Request:**

```bash
curl -X GET "https://tech-challenge-books-api-mkqn.onrender.com/api/v1/books?page=1&limit=5"
```

**Exemplo de Response:**

```json
{
  "books": [
    {
      "id": 1,
      "title": "A Light in the Attic",
      "price": "51.77",
      "rating": "Three",
      "availability": "In stock",
      "category": "Poetry",
      "image_url": "http://books.toscrape.com/media/cache/xx.jpg"
    }
  ],
  "page": 1,
  "total_pages": 50
}
```

#### Detalhes de um livro

```http
GET /api/v1/books/<id>
```

**Exemplo de Request:**

```bash
curl -X GET "https://tech-challenge-books-api-mkqn.onrender.com/api/v1/books/1"
```

**Exemplo de Response:**

```json
{
  "id": 1,
  "title": "A Light in the Attic",
  "price": "51.77",
  "rating": "Three",
  "availability": "In stock",
  "category": "Poetry",
  "description": "A collection of poetry and illustrations.",
  "image_url": "http://books.toscrape.com/media/cache/xx.jpg"
}
```

#### Buscar livros

```http
GET /api/v1/books/search?title=<title>&category=<category>
```

**Exemplo de Request:**

```bash
curl -X GET "https://tech-challenge-books-api-mkqn.onrender.com/api/v1/books/search?title=velvet&category=Historical%20Fiction"
```

**Exemplo de Response:**

```json
[
  {
    "id": 2,
    "title": "Tipping the Velvet",
    "price": "53.74",
    "rating": "One",
    "availability": "In stock",
    "category": "Historical Fiction",
    "image_url": "http://books.toscrape.com/media/cache/yy.jpg"
  }
]
```

#### Listar categorias

```http
GET /api/v1/categories
```

**Exemplo de Response:**

```json
[
  "Poetry",
  "Historical Fiction",
  "Science",
  "Travel"
]
```

#### Health Check

```http
GET /api/v1/health
```

**Exemplo de Response:**

```json
{
  "status": "ok",
  "books_count": 1000
}
```

---

### Endpoints Insights / Estatísticas

#### Estatísticas gerais

```http
GET /api/v1/stats/overview
```

**Exemplo de Response:**

```json
{
  "total_books": 1000,
  "average_price": 45.3,
  "rating_distribution": {"Three": 300, "Four": 250, "Two": 200, "Five": 150, "One": 100}
}
```

#### Estatísticas por categoria

```http
GET /api/v1/stats/categories
```

**Exemplo de Response:**

```json
{
  "Poetry": {"books_count": 150, "average_price": 47.2},
  "Science": {"books_count": 120, "average_price": 39.5}
}
```

#### Top rated books

```http
GET /api/v1/books/top-rated
```

**Exemplo de Response:**

```json
[
  {"id": 23, "title": "Best Book", "rating": "Five", "price": "60.0"}
]
```

#### Books by price range

```http
GET /api/v1/books/price-range?min=20&max=50
```

**Exemplo de Response:**

```json
[
  {"id": 10, "title": "Affordable Book", "price": "45.0"}
]
```

---

### Endpoints ML-ready

#### Features

```http
GET /api/v1/ml/features
```

**Exemplo de Response:**

```json
[
  {"price": 45.17, "rating_num": 2, "category_code": 47}
]
```

#### Training Data

```http
GET /api/v1/ml/training-data
```

**Exemplo de Response:**

```json
[
  {"price": 45.17, "category_code": 47, "rating_num": 2}
]
```

#### Predictions (JWT protected)

```http
POST /api/v1/ml/predictions
```

**Header:**

```
Authorization: Bearer <seu_token_jwt>
```

**Body JSON:**

```json
{
  "price": 25.0,
  "category_code": 3,
  "rating_num": 4
}
```

**Exemplo de Response:**

```json
{
  "predicted_price": 42.0
}
```

---

## Atualizando os Dados

```bash
python scripts/scrape_books.py
```

Depois:

```bash
git add data/books.csv
git commit -m "Update books data"
git push origin main
```

---

## Testes

```bash
pytest
```

---

## Contribuição

1. Fork do projeto
2. Criar branch feature: `git checkout -b minha-feature`
3. Commitar alterações: `git commit -m "Minha feature"`
4. Push para o branch: `git push origin minha-feature`
5. Abrir Pull Request

---

## Licença

Este projeto está licenciado sob a MIT License. Consulte o arquivo `LICENSE` para mais detalhes.

---

## Vídeo de Apresentação

Em andamento...


