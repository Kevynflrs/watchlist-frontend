import streamlit as st

from api_client import get_train_status, import_csv

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
