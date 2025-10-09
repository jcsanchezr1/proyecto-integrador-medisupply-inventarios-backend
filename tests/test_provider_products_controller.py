import pytest
import json
from unittest.mock import Mock, patch
from app import create_app
from app.models.product import Product
from datetime import datetime, timedelta


class TestProviderProductsController:
    """Tests para el controlador de productos agrupados por proveedor"""
    
    @pytest.fixture
    def app(self):
        """Crear aplicación de prueba"""
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Crear cliente de prueba"""
        return app.test_client()
    
    @pytest.fixture
    def sample_products(self):
        """Productos de prueba"""
        future_date = datetime.utcnow() + timedelta(days=30)
        
        return [
            Product(
                sku="MED-0001",
                name="Paracetamol 500mg",
                expiration_date=future_date,
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Analgésico",
                product_type="Bajo valor",
                provider_id="32892e80-fbf9-4c7f-b211-228b3aa43985"
            ),
            Product(
                sku="MED-0002",
                name="Ibuprofeno 400mg",
                expiration_date=future_date,
                quantity=50,
                price=8000.0,
                location="A-01-02",
                description="Antiinflamatorio",
                product_type="Medio valor",
                provider_id="32892e80-fbf9-4c7f-b211-228b3aa43985"
            ),
            Product(
                sku="MED-0003",
                name="Vitamina C",
                expiration_date=future_date,
                quantity=200,
                price=12000.0,
                location="B-02-01",
                description="Suplemento vitamínico",
                product_type="Alto valor",
                provider_id="12345678-1234-1234-1234-123456789012"
            )
        ]
    
    @pytest.fixture
    def mock_provider_products_service(self):
        """Mock del servicio de productos agrupados por proveedor"""
        with patch('app.controllers.provider_products_controller.ProviderProductsService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            yield service_instance
    
    def test_get_provider_products_success(self, client, mock_provider_products_service):
        """Test exitoso del endpoint de productos agrupados por proveedor"""
        # Configurar mock del servicio
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {"name": "Paracetamol 500mg", "quantity": 100, "price": 5000.0},
                        {"name": "Ibuprofeno 400mg", "quantity": 50, "price": 8000.0}
                    ]
                },
                {
                    "provider": "Farmacia XYZ",
                    "products": [
                        {"name": "Vitamina C", "quantity": 200, "price": 12000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'groups' in data['data']
        assert len(data['data']['groups']) == 2  # Dos proveedores únicos
        
        # Verificar que se llamó al servicio
        mock_provider_products_service.get_products_grouped_by_provider.assert_called_once()
    
    def test_get_provider_products_empty(self, client, mock_provider_products_service):
        """Test cuando no hay productos"""
        # Configurar mock del servicio para caso vacío
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [],
            "message": "No hay productos registrados"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['groups'] == []
        assert data['message'] == "No hay productos registrados"
    
    def test_get_provider_products_service_error(self, client, mock_provider_products_service):
        """Test cuando falla el servicio"""
        from app.exceptions.business_logic_error import BusinessLogicError
        
        # Configurar mock para lanzar excepción
        mock_provider_products_service.get_products_grouped_by_provider.side_effect = BusinessLogicError("Error en el servicio")
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 422
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Error en el servicio' in data['details']
    
    def test_response_structure(self, client, mock_provider_products_service):
        """Test de la estructura de la respuesta"""
        # Configurar mock del servicio
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {"name": "Paracetamol 500mg", "quantity": 100, "price": 5000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verificar estructura general
        assert 'success' in data
        assert 'message' in data
        assert 'data' in data
        assert 'groups' in data['data']
        
        # Verificar estructura de cada grupo
        for group in data['data']['groups']:
            assert 'provider' in group
            assert 'products' in group
            assert isinstance(group['products'], list)
            
            # Verificar estructura de cada producto
            for product in group['products']:
                assert 'name' in product
                assert 'quantity' in product
                assert 'price' in product
                assert isinstance(product['quantity'], int)
                assert isinstance(product['price'], (int, float))
    
    def test_grouping_by_provider(self, client, mock_provider_products_service):
        """Test de agrupación por proveedor"""
        # Configurar mock del servicio
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {"name": "Paracetamol 500mg", "quantity": 100, "price": 5000.0},
                        {"name": "Ibuprofeno 400mg", "quantity": 50, "price": 8000.0}
                    ]
                },
                {
                    "provider": "Farmacia XYZ",
                    "products": [
                        {"name": "Vitamina C", "quantity": 200, "price": 12000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        groups = data['data']['groups']
        
        # Debe haber 2 grupos (2 proveedores únicos)
        assert len(groups) == 2
        
        # Verificar que cada grupo tiene productos
        for group in groups:
            assert len(group['products']) > 0
            assert group['provider'] in ["Farmacia ABC", "Farmacia XYZ"]
    
    def test_product_data_integrity(self, client, mock_provider_products_service):
        """Test de integridad de datos de productos"""
        # Configurar mock del servicio
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {"name": "Paracetamol 500mg", "quantity": 100, "price": 5000.0},
                        {"name": "Ibuprofeno 400mg", "quantity": 50, "price": 8000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        groups = data['data']['groups']
        
        # Encontrar el grupo con "Farmacia ABC"
        abc_group = None
        for group in groups:
            if group['provider'] == "Farmacia ABC":
                abc_group = group
                break
        
        assert abc_group is not None
        assert len(abc_group['products']) == 2  # 2 productos del mismo proveedor
        
        # Verificar datos específicos
        product_names = [p['name'] for p in abc_group['products']]
        assert "Paracetamol 500mg" in product_names
        assert "Ibuprofeno 400mg" in product_names
