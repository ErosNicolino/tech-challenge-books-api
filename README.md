# Tech Challenge - API Books

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)  
[![Heroku](https://img.shields.io/badge/Deploy-Heroku-purple.svg)](https://tech-challenge-books-api-162d6be10e8a.herokuapp.com)  

## Descrição do Projeto
Este projeto faz parte do **Tech Challenge** e consiste em uma **API RESTful em Flask** que disponibiliza dados de livros extraídos do site [Books to Scrape](https://books.toscrape.com/).  

O objetivo é fornecer uma API escalável e pronta para consumo por cientistas de dados ou sistemas de recomendação de livros.

---

## Estrutura do Projeto

```
tech-challenge-books-api/
│
├── api/
│   └── app.py              # API Flask
├── scripts/
│   └── scrape_books.py     # Web scraping para gerar CSV
├── data/
│   └── books.csv           # CSV com os livros
├── tests/                  # Testes unitários
├── requirements.txt        # Dependências do projeto
├── Procfile                # Para deploy no Heroku
└── README.md               # Este arquivo
```

---

## Pré-requisitos

- Python **3.10+**  
- [Git](https://git-scm.com/)  
- [pip](https://pip.pypa.io/)  

---

## Rodando Localmente

1. **Clone o repositório:**
```bash
git clone <seu-repo-url>
cd tech-challenge-books-api
```

2. **Crie e ative o ambiente virtual:**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Rode a API:**
```bash
python api/app.py
```

A API estará disponível em **http://127.0.0.1:5000/**.

---

## Endpoints da API

### Rota raiz
```http
GET /
```
**Response:**
```json
{
  "message": "API Books Tech Challenge is running!",
  "endpoints": {
    "/api/v1/books": "List all books",
    "/api/v1/books/<id>": "Get book details by ID",
    "/api/v1/books/search": "Search books by title and/or category",
    "/api/v1/categories": "List all categories",
    "/api/v1/health": "API health check"
  }
}
```

### Listar todos os livros
```http
GET /api/v1/books
```
Exemplo:  
[https://tech-challenger-fiap-a3208a7afd55.herokuapp.com/api/v1/books](https://tech-challenger-fiap-a3208a7afd55.herokuapp.com/api/v1/books)

---

### Detalhes de um livro
```http
GET /api/v1/books/<id>
```

---

### Buscar livros por título ou categoria
```http
GET /api/v1/books/search?title=<title>&category=<category>
```

---

### Listar todas as categorias
```http
GET /api/v1/categories
```

---

### Health Check
```http
GET /api/v1/health
```
**Response:**
```json
{
  "status": "ok",
  "books_count": 1000
}
```

---

## Atualizando os Dados

Execute o script de scraping:
```bash
python scripts/scrape_books.py
```

Isso irá atualizar o arquivo `data/books.csv` com os dados mais recentes.  
Depois, reinicie a API localmente ou faça push para o Heroku:

```bash
git add data/books.csv
git commit -m "Update books data"
git push heroku main
```

---

## Testes

Para rodar os testes unitários:
```bash
pytest
```

---

## Deploy Público

A API está disponível no Heroku:  
🔗 [https://tech-challenger-fiap-a3208a7afd55.herokuapp.com](https://tech-challenger-fiap-a3208a7afd55.herokuapp.com)

---

## Contribuição

Contribuições são bem-vindas!  
1. Faça um fork do projeto  
2. Crie uma branch (`git checkout -b minha-feature`)  
3. Commit suas mudanças (`git commit -m "Minha feature"`)  
4. Push para a branch (`git push origin minha-feature`)  
5. Abra um Pull Request  

---

## Licença

Este projeto está licenciado sob a licença **MIT** – veja o arquivo [LICENSE](LICENSE) para mais detalhes.
