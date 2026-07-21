import streamlit as st

st.set_page_config(
    page_title="Ma Watchlist",
    page_icon=":movie_camera:",
    layout="wide",
)

# CSS custom pour les cartes de films injecte ici car il doit s'appliquer a toute la page, des le demarrage.
CUSTOM_CSS = """
<style>
.movie-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    margin-bottom: 0.1rem;
}
.movie-meta {
    font-size: 0.8rem;
    color: #888;
    margin-bottom: 0.3rem;
}
.movie-score {
    display: inline-block;
    background-color: #E50914;
    color: white;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.75rem;
    font-weight: 600;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)