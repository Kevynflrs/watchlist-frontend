import streamlit as st

CUSTOM_CSS = """
<style>
.movie-title {
    font-weight: 600;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    margin-bottom: 0.1rem;
    height: 2.6rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.movie-meta {
    font-size: 0.8rem;
    color: #888;
    margin-bottom: 0.3rem;
}
.movie-score {
    display: inline-block;
    border-radius: 4px;
    padding: 0.1rem 0.4rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: white;
}
.score-high {
    background-color: #2E7D32;
}
.score-mid {
    background-color: #E65100;
}
.score-low {
    background-color: #C62828;
}
</style>
"""


def inject_custom_css() -> None:
    """Injecte le CSS custom dans la page (a appeler une seule fois, tot dans app.py)."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
