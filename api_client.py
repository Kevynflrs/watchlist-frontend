import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@st.cache_data(ttl=300)
def get_recommendations(categorie: str, limit: int = 20) -> list[dict]:
    """Recupere les recommandations pour une categorie donnee.

    Cache de 5 minutes : les recos ne changent qu'apres un re-entrainement,
    pas besoin de retaper le backend a chaque interaction UI.
    """
    response = requests.get(
        f"{BACKEND_URL}/recommend/",
        params={"categorie": categorie, "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600)
def get_categories() -> list[str]:
    """Recupere la liste des categories disponibles.

    Cache d'1 heure : les categories sont quasi-statiques (definies cote ML).
    """
    response = requests.get(f"{BACKEND_URL}/recommend/categories", timeout=10)
    response.raise_for_status()
    return response.json()


def get_train_status() -> dict:
    """Recupere l'etat courant du modele (entraine ou non, accuracy...).

    PAS de cache ici : cette info doit toujours refleter l'etat reel,
    notamment juste apres un clic sur 'Re-entrainer'.
    """
    response = requests.get(f"{BACKEND_URL}/train/status", timeout=10)
    response.raise_for_status()
    return response.json()
