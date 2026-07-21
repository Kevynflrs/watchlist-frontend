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

with st.sidebar:
    st.header("État du modèle")

    try:
        status = get_train_status()
    except Exception:
        st.error("Backend injoignable. Vérifie que l'API tourne.")
    else:
        if status.get("model_saved"):
            st.success("Modèle entraîné et disponible")
            accuracy = status.get("accuracy")
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
    """Affiche une rangee de films recommandes pour une categorie donnee.

    Grille de 6 colonnes ; les films au-dela de 6 retombent sur les
    colonnes suivantes grace a l'operateur modulo (i % 6).
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

    cols = st.columns(6)

    for i, film in enumerate(films):
        col = cols[i % 6]
        with col:
            poster_url = (
                film.get("poster_url") or "https://placehold.co/200x300?text=Pas+d%27affiche"
            )
            st.image(poster_url, use_container_width=True)

            annee = film.get("annee", "?")
            genre = film.get("genre", "")
            score = film.get("score", 0)

            st.markdown(
                f'<div class="movie-title">{film.get("titre", "Titre inconnu")}</div>'
                f'<div class="movie-meta">{annee} · {genre}</div>'
                f'<span class="movie-score">{score:.0%}</span>',
                unsafe_allow_html=True,
            )

            with st.expander("Synopsis"):
                st.write(film.get("synopsis", "Pas de synopsis disponible."))


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
