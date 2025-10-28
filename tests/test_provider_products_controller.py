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
                product_type="Cadena de frío",
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
                product_type="Seguridad",
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
    
    def test_product_includes_new_fields(self, client, mock_provider_products_service):
        """Test que verifica que los productos incluyen los nuevos campos: id, expiration_date y description"""
        # Configurar mock del servicio con los nuevos campos (fecha en formato ISO)
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Paracetamol 500mg",
                            "quantity": 100,
                            "price": 5000.0,
                            "photo_url": "https://example.com/photo.jpg",
                            "expiration_date": "2025-12-25T00:00:00",
                            "description": "Analgésico y antipirético"
                        }
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        groups = data['data']['groups']
        
        assert len(groups) > 0
        
        # Verificar que cada producto tiene los nuevos campos
        for group in groups:
            for product in group['products']:
                # Verificar que los nuevos campos están presentes
                assert 'id' in product, "El campo 'id' debe estar presente"
                assert 'expiration_date' in product, "El campo 'expiration_date' debe estar presente"
                assert 'description' in product, "El campo 'description' debe estar presente"
                
                # Verificar que los campos originales también están presentes
                assert 'name' in product
                assert 'quantity' in product
                assert 'price' in product
                assert 'photo_url' in product
                
                # Verificar tipos de datos
                if product['id'] is not None:
                    assert isinstance(product['id'], str), "El campo 'id' debe ser string"
                
                if product['expiration_date'] is not None:
                    assert isinstance(product['expiration_date'], str), "El campo 'expiration_date' debe ser string"
                
                if product['description'] is not None:
                    assert isinstance(product['description'], str), "El campo 'description' debe ser string"
    
    def test_get_provider_products_with_user_id_recommendations(self, client, mock_provider_products_service):
        """Test del endpoint con userId que genera recomendaciones"""
        # Configurar mock del servicio con grupo de recomendados
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Recomendados",
                    "products": [
                        {
                            "id": 1,
                            "name": "Producto Recomendado 1",
                            "quantity": 100,
                            "price": 5000.0,
                            "photo_url": None,
                            "expiration_date": "2025-12-31T00:00:00",
                            "description": "Producto recomendado basado en specialty"
                        },
                        {
                            "id": 2,
                            "name": "Producto Recomendado 2",
                            "quantity": 50,
                            "price": 8000.0,
                            "photo_url": None,
                            "expiration_date": "2025-12-31T00:00:00",
                            "description": "Otro producto recomendado"
                        }
                    ]
                },
                {
                    "provider": "Farmacia ABC",
                    "products": [
                        {"id": 3, "name": "Paracetamol 500mg", "quantity": 100, "price": 5000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        # Hacer petición con userId
        response = client.get('/inventory/providers/products?userId=329cb4cc-841c-4de0-86a3-fbdd8872bc0f')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'groups' in data['data']
        
        # Verificar que el primer grupo es "Recomendados"
        assert len(data['data']['groups']) >= 1
        assert data['data']['groups'][0]['provider'] == "Recomendados"
        assert len(data['data']['groups'][0]['products']) > 0
        
        # Verificar que se llamó al servicio con el user_id
        mock_provider_products_service.get_products_grouped_by_provider.assert_called_once_with(
            user_id='329cb4cc-841c-4de0-86a3-fbdd8872bc0f'
        )
    
    def test_get_provider_products_without_user_id(self, client, mock_provider_products_service):
        """Test del endpoint sin userId (flujo normal sin recomendaciones)"""
        # Configurar mock del servicio sin grupo de recomendados
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
        
        # Hacer petición sin userId
        response = client.get('/inventory/providers/products')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'groups' in data['data']
        
        # Verificar que no hay grupo de recomendados
        for group in data['data']['groups']:
            assert group['provider'] != "Recomendados"
        
        # Verificar que se llamó al servicio sin user_id (None)
        mock_provider_products_service.get_products_grouped_by_provider.assert_called_once_with(user_id=None)
    
    def test_get_provider_products_with_invalid_user_id(self, client, mock_provider_products_service):
        """Test del endpoint con userId inválido (retorna grupos normales sin recomendados)"""
        # Configurar mock del servicio sin grupo de recomendados (cuando el usuario no existe)
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
        
        # Hacer petición con userId inválido
        response = client.get('/inventory/providers/products?userId=invalid-user-id')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'groups' in data['data']
        
        # Verificar que no hay grupo de recomendados
        for group in data['data']['groups']:
            assert group['provider'] != "Recomendados"
        
        # Verificar que se llamó al servicio con el user_id inválido
        mock_provider_products_service.get_products_grouped_by_provider.assert_called_once_with(
            user_id='invalid-user-id'
        )
    
    def test_get_provider_products_recommendations_first_position(self, client, mock_provider_products_service):
        """Test que verifica que el grupo Recomendados siempre está en primera posición"""
        # Configurar mock con recomendados en primera posición y otros grupos después
        mock_provider_products_service.get_products_grouped_by_provider.return_value = {
            "groups": [
                {
                    "provider": "Recomendados",
                    "products": [
                        {
                            "id": 1,
                            "name": "Producto Recomendado",
                            "quantity": 100,
                            "price": 5000.0,
                            "photo_url": None,
                            "expiration_date": "2025-12-31T00:00:00",
                            "description": "Producto recomendado"
                        }
                    ]
                },
                {
                    "provider": "Proveedor no asociado",
                    "products": [
                        {"id": 2, "name": "Producto 2", "quantity": 50, "price": 3000.0}
                    ]
                },
                {
                    "provider": "Farmacia XYZ",
                    "products": [
                        {"id": 3, "name": "Producto 3", "quantity": 75, "price": 4000.0}
                    ]
                }
            ],
            "message": "Productos agrupados por proveedor obtenidos exitosamente"
        }
        
        response = client.get('/inventory/providers/products?userId=test-user-id')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        groups = data['data']['groups']
        
        # Verificar que hay al menos 1 grupo
        assert len(groups) >= 1
        
        # Verificar que el primer grupo es "Recomendados"
        assert groups[0]['provider'] == "Recomendados"
        
        # Verificar que los otros grupos están después
        if len(groups) > 1:
            assert groups[1]['provider'] != "Recomendados"
            assert groups[2]['provider'] != "Recomendados"