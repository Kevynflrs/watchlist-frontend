import streamlit as st

from api_client import (
    enrich_posters,
    get_train_status,
    import_catalogue_csv,
    import_csv,
    trigger_train,
)


def render_sidebar() -> None:
    """Affiche l'integralite de la sidebar (statut, upload, actions admin)."""
    with st.sidebar:
        _render_model_status()
        st.divider()
        _render_import_section()
        st.divider()
        _render_catalogue_import_section()
        st.divider()
        _render_actions_section()


def _render_catalogue_import_section() -> None:
    """Affiche l'upload du CSV catalogue TMDB, avec le choix fill_missing_only."""
    st.header("Import du catalogue")

    catalogue_file = st.file_uploader(
        "Fichier CSV TMDB (Kaggle)", type="csv", key="catalogue_uploader"
    )

    fill_missing_only = st.toggle(
        "Compléter seulement les champs vides",
        value=True,
        key="fill_missing_only_toggle",
        help="Activé : ne remplit que les champs vides en base. Désactivé : écrase toutes les données existantes.",
    )

    if catalogue_file is not None and st.button("Importer le catalogue"):
        with st.spinner("Import du catalogue en cours..."):
            try:
                result = import_catalogue_csv(
                    file_bytes=catalogue_file.getvalue(),
                    filename=catalogue_file.name,
                    fill_missing_only=fill_missing_only,
                )
            except Exception as exc:
                st.error(f"Échec de l'import : {exc}")
            else:
                st.cache_data.clear()
                st.success(
                    f"{result.get('inserted', 0)} ajoutés, "
                    f"{result.get('updated', 0)} mis à jour, "
                    f"{result.get('unchanged', 0)} inchangés "
                    f"({result.get('skipped_duplicates', 0)} doublons ignorés)"
                )


def _render_model_status() -> None:
    """Affiche l'etat courant du modele (entraine ou non, accuracy)."""
    st.header("État du modèle")

    try:
        status = get_train_status()
    except Exception:
        st.error("Backend injoignable. Vérifie que l'API tourne.")
        return

    if status.get("model_exists"):
        st.success("Modèle entraîné et disponible")
        accuracy = status.get("metrics", {}).get("accuracy")
        if accuracy is not None:
            st.metric("Accuracy", f"{accuracy:.1%}")
    else:
        st.warning("Aucun modèle entraîné pour le moment")


def _render_import_section() -> None:
    """Affiche les uploaders watched.csv / ratings.csv et leurs boutons d'import."""
    st.header("Import de données")

    watched_file = st.file_uploader("Fichier watched.csv", type="csv", key="watched_uploader")
    if watched_file is not None and st.button("Importer watched.csv"):
        _handle_import("watched/import/watched", watched_file)

    ratings_file = st.file_uploader("Fichier ratings.csv", type="csv", key="ratings_uploader")
    if ratings_file is not None and st.button("Importer ratings.csv"):
        _handle_import("watched/import/ratings", ratings_file)


def _handle_import(endpoint: str, uploaded_file) -> None:
    """Factorise l'appel d'import + gestion d'erreur, partagee par les 2 uploaders."""
    with st.spinner("Import en cours..."):
        try:
            result = import_csv(
                endpoint=endpoint,
                file_bytes=uploaded_file.getvalue(),
                filename=uploaded_file.name,
            )
        except Exception as exc:
            st.error(f"Échec de l'import : {exc}")
        else:
            st.success(
                f"{result.get('inserted', 0)} ajoutés, {result.get('updated', 0)} mis à jour"
            )


def _render_actions_section() -> None:
    """Affiche les boutons de re-entrainement et d'enrichissement des affiches."""
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
