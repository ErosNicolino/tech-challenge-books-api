# Tech Challenge — Books API

API pública com pipeline de dados a partir de https://books.toscrape.com/.

## Estrutura inicial
- api/ → código da API
- scripts/ → web scraping
- data/ → datasets locais (CSV)
- tests/ → testes automatizados

## Como rodar
1. Criar ambiente virtual
2. Instalar dependências (`pip install -r requirements.txt`)
3. Executar a API: `uvicorn api.main:app --reload`

## Endpoints (rascunho)
- GET /api/v1/health
