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
        
        # Health check route
        assert '/inventory/ping' in rules
        
        # Product routes
        assert '/inventory/products' in rules
        assert '/inventory/products/<int:product_id>' in rules
        assert '/inventory/products/delete-all' in rules
    
    def test_create_app_endpoints_respond(self):
        """Prueba que los endpoints responden correctamente"""
        app = create_app()
        
        with app.test_client() as client:
            # Health check
            response = client.get('/inventory/ping')
            assert response.status_code == 200
            
            # Product endpoints
            response = client.get('/inventory/products')
            assert response.status_code == 200
            
            # GET producto específico puede retornar 200 o 404 dependiendo de si existe
            response = client.get('/inventory/products/1')
            assert response.status_code in [200, 404]
            
            response = client.delete('/inventory/products/delete-all')
            assert response.status_code == 200

