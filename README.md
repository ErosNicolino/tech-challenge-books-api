# Tech Challenge - API Books

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-green.svg)](https://flask.palletsprojects.com/)
[![Deploy](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://tech-challenge-books-api-mkqn.onrender.com)

## Descrição do Projeto
Este projeto é parte do **Tech Challenge** e consiste em uma **API RESTful em Flask** que fornece dados de livros extraídos do site [Books to Scrape](https://books.toscrape.com/).  

A API é projetada para ser escalável e pronta para consumo por cientistas de dados, sistemas de recomendação de livros ou aplicações web. Possui endpoints para listar, buscar e consultar detalhes de livros, bem como listar categorias e verificar a saúde da API.

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
├── tests/                  # Testes unitários (opcional)
├── requirements.txt        # Dependências do projeto
├── Procfile                # Configuração para deploy no Render
└── README.md               # Documentação do projeto
```

---

## Pré-requisitos

- Python 3.10+  
- [Git](https://git-scm.com/)  
- [pip](https://pip.pypa.io/en/stable/)  

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

A API estará disponível em **http://127.0.0.1:5000/**.

---

## Deploy Público

A API está hospedada no Render:  
[https://tech-challenge-books-api-mkqn.onrender.com](https://tech-challenge-books-api-mkqn.onrender.com)

---

## Documentação Interativa (Swagger)

A documentação interativa da API pode ser acessada aqui:  
[https://tech-challenge-books-api-mkqn.onrender.com/apidocs](https://tech-challenge-books-api-mkqn.onrender.com/apidocs)

---

## Endpoints da API

### 1. Página inicial
```http
GET /
```
Retorna a página inicial da API.

---

### 2. Informações gerais da API
```http
GET /api/v1
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

---

### 3. Listar todos os livros
```http
GET /api/v1/books
```
Retorna todos os livros da base de dados.

---

### 4. Detalhes de um livro
```http
GET /api/v1/books/<id>
```
Retorna os detalhes de um livro específico pelo ID.

---

### 5. Buscar livros
```http
GET /api/v1/books/search?title=<title>&category=<category>
```
Permite buscar livros por título e/ou categoria.

---

### 6. Listar categorias
```http
GET /api/v1/categories
```
Retorna todas as categorias de livros disponíveis.

---

### 7. Health Check
```http
GET /api/v1/health
```
Verifica o status da API e retorna a quantidade total de livros.

**Response:**
```json
{
  "status": "ok",
  "books_count": 1000
}
```

---

## Atualizando os Dados

Para atualizar o CSV de livros:

```bash
python scripts/scrape_books.py
```

Depois, reinicie a API localmente ou faça push para o Render:

```bash
git add data/books.csv
git commit -m "Update books data"
git push origin main
```

---

## Testes

Para rodar os testes unitários:

```bash
pytest
```

---

## Contribuição

Contribuições são bem-vindas:

1. Faça um fork do projeto  
2. Crie uma branch (`git checkout -b minha-feature`)  
3. Commit suas mudanças (`git commit -m "Minha feature"`)  
4. Push para a branch (`git push origin minha-feature`)  
5. Abra um Pull Request  

---

## Licença

Este projeto está licenciado sob a licença **MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

---

## Vídeo de Apresentação

- Duração sugerida: 3–12 minutos  
- Mostrar a API rodando online (link Render)  
- Demonstrar alguns endpoints funcionando e o Swagger  
- Explicar a arquitetura do pipeline e boas práticas  
- Hospedar no YouTube ou Google Drive e adicionar o link aqui  

> **Exemplo de link de vídeo:**  
> [Apresentação Tech Challenge - API Books](#)

