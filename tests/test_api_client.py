import responses
from api_client import BACKEND_URL, get_recommendations, import_csv


@responses.activate
def test_get_recommendations_builds_correct_url():
    """Verifie que get_recommendations appelle bien la bonne URL avec les bons params."""
    responses.add(
        responses.GET,
        f"{BACKEND_URL}/recommend/",
        json=[{"titre": "Inception", "score": 0.92}],
        status=200,
    )

    result = get_recommendations(categorie="Blockbuster", limit=10)

    assert result == [{"titre": "Inception", "score": 0.92}]
    # On verifie que l'appel reel a bien utilise les bons parametres.
    request_url = responses.calls[0].request.url
    assert "categorie=Blockbuster" in request_url
    assert "limit=10" in request_url


@responses.activate
def test_import_csv_sends_multipart_with_correct_filename():
    """Verifie que import_csv envoie bien un multipart avec le nom de fichier attendu."""
    responses.add(
        responses.POST,
        f"{BACKEND_URL}/watched/import/watched",
        json={"inserted": 5, "updated": 2},
        status=200,
    )

    result = import_csv(
        endpoint="watched/import/watched",
        file_bytes=b"movie_id,watched_at\n1,2026-01-01",
        filename="watched.csv",
    )

    assert result == {"inserted": 5, "updated": 2}
    sent_body = responses.calls[0].request.body.decode()
    assert 'filename="watched.csv"' in sent_body


@responses.activate
def test_get_recommendations_raises_on_http_error():
    """Verifie qu'une erreur HTTP 500 leve bien une exception (pas de swallow silencieux)."""
    responses.add(
        responses.GET,
        f"{BACKEND_URL}/recommend/",
        json={"detail": "Internal Server Error"},
        status=500,
    )

    try:
        get_recommendations(categorie="Blockbuster", limit=10)
        raise AssertionError("Une exception HTTPError aurait du etre levee")
    except Exception as exc:
        assert "500" in str(exc)
