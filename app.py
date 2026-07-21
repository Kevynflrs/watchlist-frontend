import streamlit as st

from api_client import get_categories
from grid import render_row
from sidebar import render_sidebar
from style import inject_custom_css

st.set_page_config(
    page_title="Ma Watchlist",
    page_icon=":movie_camera:",
    layout="wide",
)

inject_custom_css()
render_sidebar()

FALLBACK_CATEGORIES = ["Blockbuster", "Grand Public", "Film d'Auteur"]

st.title("Ma Watchlist")

try:
    categories = get_categories()
except Exception:
    st.warning("Catégories par défaut affichées (backend injoignable pour /recommend/categories).")
    categories = FALLBACK_CATEGORIES

for i, categorie in enumerate(categories):
    render_row(categorie)
    if i < len(categories) - 1:
        st.divider()
