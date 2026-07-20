import app


def test_app_importable():
    """Verifie que le module app.py ne leve aucune exception a l'import."""
    assert app is not None
