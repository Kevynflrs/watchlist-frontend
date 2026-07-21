import streamlit as st

from api_client import (
    enrich_posters,
    get_categories,
    get_recommendations,
    get_train_status,
    import_csv,
    trigger_train,
)

st.set_page_config(
    page_title="Ma Watchlist",
    page_icon=":movie_camera:",
    layout="wide",
)

# CSS custom pour les cartes de films injecte ici car il doit s'appliquer a toute la page, des le demarrage.
CUSTOM_CSS = """
<style>
[data-testid="stImage"] img {
    height: 280px;
    width: 100%;
    object-fit: cover;
    border-radius: 6px;
}
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
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.header("État du modèle")

    try:
        status = get_train_status()
    except Exception:
        st.error("Backend injoignable. Vérifie que l'API tourne.")
    else:
        if status.get("model_exists"):
            st.success("Modèle entraîné et disponible")
            accuracy = status.get("metrics", {}).get("accuracy")
            if accuracy is not None:
                st.metric("Accuracy", f"{accuracy:.1%}")
        else:
            st.warning("Aucun modèle entraîné pour le moment")

    st.divider()
    st.header("Import de données")

    watched_file = st.file_uploader("Fichier watched.csv", type="csv", key="watched_uploader")
    if watched_file is not None and st.button("Importer watched.csv"):
        with st.spinner("Import en cours..."):
            try:
                result = import_csv(
                    endpoint="watched/import/watched",
                    file_bytes=watched_file.getvalue(),
                    filename=watched_file.name,
                )
            except Exception as exc:
                st.error(f"Échec de l'import : {exc}")
            else:
                st.success(
                    f"{result.get('inserted', 0)} ajoutés, {result.get('updated', 0)} mis à jour"
                )

    ratings_file = st.file_uploader("Fichier ratings.csv", type="csv", key="ratings_uploader")
    if ratings_file is not None and st.button("Importer ratings.csv"):
        with st.spinner("Import en cours..."):
            try:
                result = import_csv(
                    endpoint="watched/import/ratings",
                    file_bytes=ratings_file.getvalue(),
                    filename=ratings_file.name,
                )
            except Exception as exc:
                st.error(f"Échec de l'import : {exc}")
            else:
                st.success(
                    f"{result.get('inserted', 0)} ajoutés, {result.get('updated', 0)} mis à jour"
                )

    st.divider()
    st.header("Actions")

    if st.button("Ré-entraîner"):
        with st.spinner("Entraînement en cours..."):
            try:
                result = trigger_train()
            except Exception as exc:
                st.error(f"Échec de l'entraînement : {exc}")
            else:
                st.cache_data.clear()
                accuracy = result.get("accuracy")
                if accuracy is not None:
                    st.success(f"Modèle ré-entraîné (accuracy : {accuracy:.1%})")
                else:
                    st.success("Modèle ré-entraîné")

    if st.button("Compléter les affiches"):
        with st.spinner("Enrichissement en cours..."):
            try:
                result = enrich_posters(limit=100)
            except Exception as exc:
                st.error(f"Échec de l'enrichissement : {exc}")
            else:
                st.cache_data.clear()
                st.success(f"{result.get('updated', 0)} affiches complétées")


def render_row(categorie: str) -> None:
    """Affiche une rangee de films recommandes, decoupee en lignes de 6.
    Le panneau de synopsis s'affiche juste sous la ligne du film selectionne.
    """
    try:
        films = get_recommendations(categorie=categorie, limit=18)
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

    # On decoupe la liste en paquets de 6 : un paquet = une ligne visuelle.
    for start in range(0, len(films), 6):
        line_films = films[start : start + 6]
        cols = st.columns(6)

        for offset, film in enumerate(line_films):
            i = start + offset  # index global, pour des cles de bouton uniques
            with cols[offset]:
                poster_url = (
                    film.get("poster_url") or "https://placehold.co/200x300?text=Pas+d%27affiche"
                )
                st.image(poster_url, use_container_width=True)

                annee = film.get("year", "?")
                genres = film.get("genres") or []
                genre_str = ", ".join(genres) if genres else "Genre inconnu"
                score = film.get("score_prediction", 0)

                st.markdown(
                    f'<div class="movie-title">{film.get("title", "Titre inconnu")}</div>'
                    f'<div class="movie-meta">{annee} · {genre_str}</div>'
                    f'<span class="movie-score">{score:.0%}</span>',
                    unsafe_allow_html=True,
                )

                if st.button("Synopsis", key=f"btn_{categorie}_{i}"):
                    st.session_state[session_key] = i
                    st.rerun()

        # Le film selectionne fait-il partie de CETTE ligne (start a start+5) ? Si oui, panneau affiche ici, avant de passer a la ligne suivante.
        if selected_i is not None and start <= selected_i < start + 6:
            film = films[selected_i]
            with st.container(border=True):
                st.markdown(f"**{film.get('title', 'Titre inconnu')}**")
                st.write(film.get("overview", "Pas de synopsis disponible."))
                if st.button("Fermer", key=f"close_{categorie}_{start}"):
                    st.session_state[session_key] = None
                    st.rerun()


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
