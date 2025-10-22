import pytest
import json
from unittest.mock import Mock, patch
from app import create_app


class TestProductHistoryController:
    """Tests para el controlador de historial de productos procesados"""
    
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
    def sample_history_data(self):
        """Datos de historial de prueba"""
        return [
            {
                "id": "history-1",
                "file_name": "productos_2025_01.xlsx",
                "created_at": "2025-01-15T10:30:00",
                "status": "Completado",
                "result": "Se procesaron 100 productos correctamente",
                "user": "medisupply01"
            },
            {
                "id": "history-2",
                "file_name": "productos_2025_02.xlsx",
                "created_at": "2025-01-16T14:20:00",
                "status": "En curso",
                "result": None,
                "user": "medisupply02"
            }
        ]
    
    @pytest.fixture
    def mock_history_service(self):
        """Mock del servicio de historial"""
        with patch('app.controllers.product_history_controller.ProductHistoryService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            yield service_instance
    
    def test_get_history_success_default_pagination(self, client, mock_history_service, sample_history_data):
        """Test exitoso del endpoint con paginación por defecto"""
        # Configurar mock del servicio
        mock_history_service.get_history_paginated.return_value = sample_history_data
        mock_history_service.get_history_count.return_value = 25
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['message'] == "Historial obtenido exitosamente"
        assert 'data' in data
        assert 'history' in data['data']
        assert 'pagination' in data['data']
        
        # Verificar paginación
        pagination = data['data']['pagination']
        assert pagination['page'] == 1
        assert pagination['per_page'] == 10
        assert pagination['total'] == 25
        assert pagination['total_pages'] == 3
        assert pagination['has_next'] is True
        assert pagination['has_prev'] is False
        assert pagination['next_page'] == 2
        assert pagination['prev_page'] is None
        
        # Verificar que se llamó al servicio con parámetros por defecto
        mock_history_service.get_history_paginated.assert_called_once_with(page=1, per_page=10, user_id=None)
        mock_history_service.get_history_count.assert_called_once_with(user_id=None)
    
    def test_get_history_with_page_parameter(self, client, mock_history_service, sample_history_data):
        """Test del endpoint con parámetro page"""
        mock_history_service.get_history_paginated.return_value = sample_history_data
        mock_history_service.get_history_count.return_value = 50
        
        response = client.get('/inventory/products/history?page=2')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        pagination = data['data']['pagination']
        assert pagination['page'] == 2
        assert pagination['has_prev'] is True
        assert pagination['prev_page'] == 1
        
        mock_history_service.get_history_paginated.assert_called_once_with(page=2, per_page=10, user_id=None)
    
    def test_get_history_with_per_page_parameter(self, client, mock_history_service, sample_history_data):
        """Test del endpoint con parámetro per_page"""
        mock_history_service.get_history_paginated.return_value = sample_history_data[:5]
        mock_history_service.get_history_count.return_value = 50
        
        response = client.get('/inventory/products/history?per_page=5')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        pagination = data['data']['pagination']
        assert pagination['per_page'] == 5
        assert pagination['total_pages'] == 10
        
        mock_history_service.get_history_paginated.assert_called_once_with(page=1, per_page=5, user_id=None)
    
    def test_get_history_with_page_and_per_page(self, client, mock_history_service, sample_history_data):
        """Test del endpoint con parámetros page y per_page"""
        mock_history_service.get_history_paginated.return_value = sample_history_data
        mock_history_service.get_history_count.return_value = 100
        
        response = client.get('/inventory/products/history?page=3&per_page=20')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        pagination = data['data']['pagination']
        assert pagination['page'] == 3
        assert pagination['per_page'] == 20
        assert pagination['total_pages'] == 5
        
        mock_history_service.get_history_paginated.assert_called_once_with(page=3, per_page=20, user_id=None)
    
    def test_get_history_by_user_id(self, client, mock_history_service, sample_history_data):
        """Test del endpoint con filtro por user_id"""
        user_history = [sample_history_data[0]]
        mock_history_service.get_history_paginated.return_value = user_history
        mock_history_service.get_history_count.return_value = 5
        
        response = client.get('/inventory/products/history?user_id=user-123')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        pagination = data['data']['pagination']
        assert pagination['total'] == 5
        
        mock_history_service.get_history_paginated.assert_called_once_with(page=1, per_page=10, user_id='user-123')
        mock_history_service.get_history_count.assert_called_once_with(user_id='user-123')
    
    def test_get_history_empty(self, client, mock_history_service):
        """Test cuando no hay historial"""
        mock_history_service.get_history_paginated.return_value = []
        mock_history_service.get_history_count.return_value = 0
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['history'] == []
        assert data['data']['pagination']['total'] == 0
        assert data['data']['pagination']['total_pages'] == 0
    
    def test_get_history_invalid_page_zero(self, client, mock_history_service):
        """Test con page inválido (0)"""
        response = client.get('/inventory/products/history?page=0')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'page' in data['details'].lower()
    
    def test_get_history_invalid_page_negative(self, client, mock_history_service):
        """Test con page negativo"""
        response = client.get('/inventory/products/history?page=-1')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'page' in data['details'].lower()
    
    def test_get_history_invalid_per_page_zero(self, client, mock_history_service):
        """Test con per_page inválido (0)"""
        response = client.get('/inventory/products/history?per_page=0')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'per_page' in data['details'].lower()
    
    def test_get_history_invalid_per_page_negative(self, client, mock_history_service):
        """Test con per_page negativo"""
        response = client.get('/inventory/products/history?per_page=-5')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'per_page' in data['details'].lower()
    
    def test_get_history_invalid_per_page_too_large(self, client, mock_history_service):
        """Test con per_page mayor a 100"""
        response = client.get('/inventory/products/history?per_page=101')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'per_page' in data['details'].lower()
    
    def test_get_history_service_error(self, client, mock_history_service):
        """Test cuando el servicio lanza una excepción"""
        from app.exceptions.business_logic_error import BusinessLogicError
        
        mock_history_service.get_history_paginated.side_effect = BusinessLogicError("Error en el servicio")
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 422
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Error en el servicio' in data['details']
    
    def test_get_history_validation_error(self, client, mock_history_service):
        """Test cuando hay error de validación"""
        from app.exceptions.validation_error import ValidationError
        
        mock_history_service.get_history_paginated.side_effect = ValidationError("Datos inválidos")
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Datos inválidos' in data['details']
    
    def test_get_history_generic_exception(self, client, mock_history_service):
        """Test cuando ocurre una excepción genérica"""
        mock_history_service.get_history_paginated.side_effect = Exception("Error inesperado")
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_response_structure(self, client, mock_history_service, sample_history_data):
        """Test de la estructura de la respuesta"""
        mock_history_service.get_history_paginated.return_value = sample_history_data
        mock_history_service.get_history_count.return_value = 10
        
        response = client.get('/inventory/products/history')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        
        # Verificar estructura general
        assert 'success' in data
        assert 'message' in data
        assert 'data' in data
        assert 'history' in data['data']
        assert 'pagination' in data['data']
        assert isinstance(data['data']['history'], list)
        
        # Verificar estructura de paginación
        pagination = data['data']['pagination']
        assert 'page' in pagination
        assert 'per_page' in pagination
        assert 'total' in pagination
        assert 'total_pages' in pagination
        assert 'has_next' in pagination
        assert 'has_prev' in pagination
        assert 'next_page' in pagination
        assert 'prev_page' in pagination
        
        # Verificar estructura de cada registro de historial
        for history_item in data['data']['history']:
            assert 'id' in history_item
            assert 'file_name' in history_item
            assert 'created_at' in history_item
            assert 'status' in history_item
            assert 'result' in history_item
            assert 'user' in history_item
    
    def test_pagination_last_page(self, client, mock_history_service, sample_history_data):
        """Test de paginación en la última página"""
        mock_history_service.get_history_paginated.return_value = sample_history_data
        mock_history_service.get_history_count.return_value = 25
        
        response = client.get('/inventory/products/history?page=3&per_page=10')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        pagination = data['data']['pagination']
        assert pagination['page'] == 3
        assert pagination['total_pages'] == 3
        assert pagination['has_next'] is False
        assert pagination['has_prev'] is True
        assert pagination['next_page'] is None
        assert pagination['prev_page'] == 2
    
    def test_endpoint_method_allowed(self, client):
        """Test que el endpoint solo acepta GET"""
        response = client.post('/inventory/products/history')
        assert response.status_code == 405  # Method Not Allowed
        
        response = client.put('/inventory/products/history')
        assert response.status_code == 405
        
        response = client.delete('/inventory/products/history')
        assert response.status_code == 405
