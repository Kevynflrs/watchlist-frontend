import requests
import streamlit as st

from api_client import get_recommendations


def get_score_css_class(score: float) -> str:
    """Determine la classe CSS a appliquer selon le score de prediction."""
    if score >= 0.75:
        return "score-high"
    if score >= 0.50:
        return "score-mid"
    return "score-low"


def render_row(categorie: str) -> None:
    """Affiche une rangee de films recommandes, decoupee en lignes de 6.
    Le panneau de synopsis s'affiche juste sous la ligne du film selectionne.
    """
    try:
        films = get_recommendations(categorie=categorie, limit=18)
    except requests.exceptions.Timeout:
        st.warning(f"Le backend met du temps à répondre pour « {categorie} ». Il est peut-être occupé (import ou enrichissement en cours). Réessaie dans un instant.")
        return
    
    except Exception as exc:
        st.error(f"Impossible de charger les recommandations : {exc}")
        return

    st.subheader(categorie)

    if not films:
        st.info("Aucune recommandation disponible pour cette catégorie.")
        return

    session_key = f"selected_film_{categorie}"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    selected_i = st.session_state[session_key]

    for start in range(0, len(films), 6):
        line_films = films[start : start + 6]
        cols = st.columns(6)

        for offset, film in enumerate(line_films):
            i = start + offset
            with cols[offset]:
                _render_movie_card(film, categorie, i, session_key)

        if selected_i is not None and start <= selected_i < start + 6:
            _render_synopsis_panel(films[selected_i], categorie, start, session_key)


def _render_movie_card(film: dict, categorie: str, i: int, session_key: str) -> None:
    """Affiche une carte film individuelle (affiche, titre, meta, score, bouton)."""
    poster_url = film.get("poster_url") or "https://placehold.co/200x300?text=Pas+d%27affiche"
    st.image(poster_url, use_container_width=True)

    annee = film.get("year", "?")
    genres = film.get("genres") or []
    genre_str = ", ".join(genres) if genres else "Genre inconnu"
    score = film.get("score_prediction", 0)
    score_class = get_score_css_class(score)

    st.markdown(
        f'<div class="movie-title">{film.get("title", "Titre inconnu")}</div>'
        f'<div class="movie-meta">{annee} · {genre_str}</div>'
        f'<span class="movie-score {score_class}">{score:.0%}</span>',
        unsafe_allow_html=True,
    )

    if st.button("Synopsis", key=f"btn_{categorie}_{i}"):
        st.session_state[session_key] = i
        st.rerun()


def _render_synopsis_panel(film: dict, categorie: str, start: int, session_key: str) -> None:
    """Affiche le panneau de synopsis pleine largeur pour le film selectionne."""
    with st.container(border=True):
        st.markdown(f"**{film.get('title', 'Titre inconnu')}**")
        st.write(film.get("overview", "Pas de synopsis disponible."))
        if st.button("Fermer", key=f"close_{categorie}_{start}"):
            st.session_state[session_key] = None
            st.rerun()
