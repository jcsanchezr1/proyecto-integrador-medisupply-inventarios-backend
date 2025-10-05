"""
Tests para la aplicación principal
"""
import pytest
from app import create_app


class TestAppCreation:
    """Pruebas para la creación de la aplicación"""
    
    def test_create_app(self):
        """Prueba que la aplicación se crea correctamente"""
        app = create_app()
        assert app is not None
        assert app.config['SECRET_KEY'] is not None
    
    def test_create_app_has_routes(self):
        """Prueba que la aplicación tiene las rutas registradas"""
        app = create_app()
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/inventory/ping' in rules

