# Watchlist Frontend

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/Kevynflrs/watchlist-frontend/actions/workflows/ci.yml/badge.svg)](https://github.com/TON-USER/watchlist-frontend/actions)
[![Streamlit](https://img.shields.io/badge/streamlit-app-FF4B4B.svg)](https://streamlit.io)

## Description

Interface Streamlit type "Netflix de ma watchlist personnelle" : une grille de films organisée par catégorie (Blockbuster, Grand Public, Film d'Auteur), avec affiche, titre, genres, score de recommandation coloré, et synopsis consultable.

Ce frontend ne fait aucun calcul lui-même il consomme uniquement l'API du backend [`watchlist-backend`](../watchlist-backend) via des appels HTTP. Streamlit a été préféré à un outil comme Grafana car il permet de construire une interface interactive sur-mesure (upload de fichiers, boutons d'action, grille personnalisée) en pur Python, sans avoir à écrire de JavaScript.

## Architecture

```
watchlist-backend --> API FastAPI, DB, pipeline ML, intégration TMDB
watchlist-frontend (ce repo) --> interface Streamlit ("Netflix de ma watchlist")
watchlist (méta-repo) --> README d'architecture, docker-compose global, notebook Colab
```

```
watchlist-frontend/
    ├── app.py
    ├── api_client.py
    ├── ui/
    |	├── style.py
    |	├── sidebar.py
    |	└── grid.py
    ├── requirements.txt
    ├── requirements-dev.txt
    ├── .gitignore
    ├── Dockerfile
    ├──
    ├── pyproject.toml
    ├── .pre-commit-config.yaml
    └── tests/
        ├── __init__.py
        ├── test_api_client.py
        └── test_smoke.py
```

## Installation

### En local

```bash
python -m venv .venv
source .venv\Scripts\Activate.ps1 # ou .venv/bin/activate sous Linux
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
pre-commit install
streamlit run app.py
```

### Avec Docker

Depuis le meta-repo [`watchlist`](../watchlist), qui orchestre backend, base de données et frontend ensemble :

```bash
docker compose up --build
```

## Usage

1. Lancer le backend et la base de données (via Docker Compose, ou séparément en local)
2. Lancer `streamlit run app.py`
3. Dans la sidebar : importer `watched.csv` et `ratings.csv`, puis cliquer sur "Ré-entraîner"
4. La grille de recommandations s'affiche, organisée par catégorie
5. Cliquer sur "Synopsis" sous un film pour afficher sa description

## Tests

```bash
pytest
```

Les tests mockent tous les appels HTTP (via `responses`) — aucun backend réel n'est nécessaire pour les exécuter.

## Repos liés

- [watchlist-backend](https://github.com/Kevynflrs/watchlist-backend) : backend du projet
- [watchlist](https://github.com/Kevynflrs/watchlist) : méta-repo (architecture globale, docker-compose, notebook Colab)

## Convention de commits

Ce projet suit [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>: <description>
```

**Types utilisés dans ce projet :**

| Type         | Usage                                                                 |
| ------------ | --------------------------------------------------------------------- |
| `feat`     | Nouvelle fonctionnalité (ex: nouvel endpoint, nouvelle feature ML)   |
| `fix`      | Correction de bug                                                     |
| `test`     | Ajout ou modification de tests, sans changement de comportement       |
| `docs`     | Documentation uniquement (README, docstrings)                         |
| `refactor` | Changement de code sans nouvelle fonctionnalité ni correction de bug |

## Licence

Ce projet est distribué sous [licence MIT](LICENSE).
