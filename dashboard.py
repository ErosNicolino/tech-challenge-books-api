import streamlit as st
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import os
import re

# ===== Configurações do Streamlit =====
st.set_page_config(
    page_title="Dashboard - API Books",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== Branding =====
PRIMARY_COLOR = "#FF004D"   
SECONDARY_COLOR = "#2B2B2B" 
TEXT_COLOR = "#FFFFFF"      
GRAPH_TEXT_COLOR = "#000000" 

st.markdown(f"""
<style>
    /* Fundo do app */
    .stApp {{
        background-color: {SECONDARY_COLOR};
        color: {TEXT_COLOR};
    }}
    /* Títulos, subtítulos e textos gerais */
    h1, h2, h3, h4, .stMarkdown p {{
        color: {TEXT_COLOR};
    }}]
    /* Textos das tabelas Streamlit */
    .stDataFrame div {{
        color: {TEXT_COLOR};
    }}
    /* Barra lateral */
    .stSidebar {{
        background-color: #1f1f1f;
        color: {TEXT_COLOR};
    }}
</style>
""", unsafe_allow_html=True)

st.title("Dashboard - API Books")
st.markdown("Visualização interativa e métricas da API, filtragem de livros e gráficos interativos.")

# ===== Função para carregar CSV =====
@st.cache_data
def load_books():
    csv_path = os.path.join(os.path.dirname(__file__), "data", "books.csv")
    if not os.path.exists(csv_path):
        st.warning("Arquivo books.csv não encontrado. Execute o scraping antes.")
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path, encoding="utf-8")
    
    # Limpa preços: remove qualquer caractere que não seja número ou ponto
    if 'price' in df.columns:
        df['price'] = df['price'].apply(lambda x: float(re.sub(r'[^0-9.]', '', str(x))))
    
    # Adiciona coluna numérica para rating
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    if 'rating' in df.columns:
        df['rating_num'] = df['rating'].map(rating_map)
    
    return df

books_df = load_books()
if books_df.empty:
    st.stop()

# ===== Sidebar filtros =====
st.sidebar.header("Filtros Interativos")
price_min, price_max = st.sidebar.slider(
    "Faixa de Preço (£):",
    float(books_df['price'].min()),
    float(books_df['price'].max()),
    (float(books_df['price'].min()), float(books_df['price'].max()))
)
selected_category = st.sidebar.selectbox(
    "Categoria:",
    ["Todas"] + books_df['category'].dropna().unique().tolist()
)

# ===== Aplicar filtros =====
filtered_df = books_df[(books_df['price'] >= price_min) & (books_df['price'] <= price_max)]
if selected_category != "Todas":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]

# ===== Estatísticas gerais =====
st.subheader("Estatísticas Gerais")
col1, col2, col3 = st.columns(3)
col1.metric("Total de Livros", len(filtered_df))
col2.metric("Preço Médio", f"£{filtered_df['price'].mean():.2f}" if not filtered_df.empty else "0")
col3.metric("Categorias Ativas", filtered_df['category'].nunique())

# ===== Distribuição de Ratings =====
st.subheader("Distribuição de Ratings")
fig, ax = plt.subplots(figsize=(5,3))
sns.countplot(x='rating', data=filtered_df, color=PRIMARY_COLOR, ax=ax)
ax.set_facecolor(SECONDARY_COLOR)
ax.set_title("Distribuição de Ratings", fontsize=10, color=GRAPH_TEXT_COLOR)
ax.set_xlabel("Rating", fontsize=9, color=GRAPH_TEXT_COLOR)
ax.set_ylabel("Quantidade", fontsize=9, color=GRAPH_TEXT_COLOR)
ax.tick_params(colors=GRAPH_TEXT_COLOR, labelsize=8)
st.pyplot(fig, clear_figure=True)

# ===== Distribuição de Preços =====
st.subheader("Distribuição de Preços")
fig, ax = plt.subplots(figsize=(5,3))
sns.histplot(filtered_df['price'], bins=12, color=PRIMARY_COLOR, ax=ax)
ax.set_facecolor(SECONDARY_COLOR)
ax.set_title("Histograma de Preços", fontsize=10, color=GRAPH_TEXT_COLOR)
ax.set_xlabel("Preço (£)", fontsize=9, color=GRAPH_TEXT_COLOR)
ax.set_ylabel("Quantidade", fontsize=9, color=GRAPH_TEXT_COLOR)
ax.tick_params(colors=GRAPH_TEXT_COLOR, labelsize=8)
st.pyplot(fig, clear_figure=True)

# ===== Top 10 Livros por Preço =====
st.subheader("Top 10 Livros por Preço")
top_price = filtered_df.sort_values(by="price", ascending=False).head(10)
st.dataframe(top_price[['title','category','price','rating']], width='stretch')

# ===== Top 10 Livros por Rating =====
st.subheader("Top 10 Livros por Rating")
top_rating = filtered_df.sort_values(by='rating_num', ascending=False).head(10)
st.dataframe(top_rating[['title','category','price','rating']], width='stretch')

# ===== Métricas da API =====
st.subheader("Métricas da API")
API_BASE = "https://tech-challenge-books-api-mkqn.onrender.com/api/v1"
try:
    health = requests.get(f"{API_BASE}/health").json()
    st.json(health)
except:
    st.error("Não foi possível acessar a API /health.")

# ===== Estatísticas por Categoria via API =====
st.subheader("Estatísticas por Categoria")
try:
    cat_stats = requests.get(f"{API_BASE}/stats/categories").json()
    cat_df = pd.DataFrame.from_dict(cat_stats, orient='index')
    st.bar_chart(cat_df[['books_count', 'average_price']])
except:
    st.warning("Não foi possível acessar estatísticas por categoria.")

st.markdown("---")
st.markdown("Dashboard - FIAP | Desenvolvido por **Eros Nicolino**")
