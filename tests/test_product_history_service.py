import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.product_history_service import ProductHistoryService
from app.models.product_processed_history import ProductProcessedHistory


class TestProductHistoryService:
    """Tests para el servicio de historial de productos procesados"""
    
    @pytest.fixture
    def sample_histories(self):
        """Historiales de prueba"""
        return [
            ProductProcessedHistory(
                id="history-1",
                file_name="productos_2025_01.xlsx",
                user_id="user-1",
                status="Completado",
                result="Se procesaron 100 productos correctamente",
                created_at=datetime(2025, 1, 15, 10, 30, 0)
            ),
            ProductProcessedHistory(
                id="history-2",
                file_name="productos_2025_02.xlsx",
                user_id="user-2",
                status="En curso",
                result=None,
                created_at=datetime(2025, 1, 16, 14, 20, 0)
            ),
            ProductProcessedHistory(
                id="history-3",
                file_name="productos_2025_03.xlsx",
                user_id="user-1",
                status="Error",
                result="Error al procesar: formato inválido",
                created_at=datetime(2025, 1, 17, 9, 15, 0)
            )
        ]
    
    @pytest.fixture
    def mock_history_repository(self, sample_histories):
        """Mock del repositorio de historial"""
        with patch('app.services.product_history_service.ProductProcessedHistoryRepository') as mock:
            repository_instance = Mock()
            mock.return_value = repository_instance
            repository_instance.get_all.return_value = sample_histories
            repository_instance.get_by_user_id.return_value = [
                h for h in sample_histories if h.user_id == "user-1"
            ]
            repository_instance.get_count.return_value = len(sample_histories)
            yield repository_instance
    
    @pytest.fixture
    def mock_authenticator_service(self):
        """Mock del servicio de autenticación"""
        with patch('app.services.product_history_service.AuthenticatorService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            
            # Configurar respuestas del mock
            def get_user_name_side_effect(user_id):
                if user_id == "user-1":
                    return "Usuario Uno"
                elif user_id == "user-2":
                    return "Usuario Dos"
                else:
                    return "Usuario no disponible"
            
            service_instance.get_user_name.side_effect = get_user_name_side_effect
            
            yield service_instance
    
    def test_get_history_paginated_success_default(self, mock_history_repository, mock_authenticator_service):
        """Test exitoso de obtención de historial con paginación por defecto"""
        service = ProductHistoryService()
        result = service.get_history_paginated()
        
        # Verificaciones
        assert len(result) == 3
        assert all(isinstance(item, dict) for item in result)
        
        # Verificar primer registro
        assert result[0]["id"] == "history-1"
        assert result[0]["file_name"] == "productos_2025_01.xlsx"
        assert result[0]["status"] == "Completado"
        assert result[0]["user"] == "Usuario Uno"
        
        # Verificar que se llamó con parámetros por defecto
        mock_history_repository.get_all.assert_called_once_with(limit=10, offset=0)
    
    def test_get_history_paginated_with_page(self, mock_history_repository, mock_authenticator_service):
        """Test de obtención de historial con página específica"""
        service = ProductHistoryService()
        result = service.get_history_paginated(page=2, per_page=10)
        
        # Verificar que se calculó el offset correctamente
        mock_history_repository.get_all.assert_called_once_with(limit=10, offset=10)
    
    def test_get_history_paginated_with_per_page(self, mock_history_repository, mock_authenticator_service):
        """Test de obtención de historial con per_page personalizado"""
        service = ProductHistoryService()
        result = service.get_history_paginated(page=1, per_page=5)
        
        mock_history_repository.get_all.assert_called_once_with(limit=5, offset=0)
    
    def test_get_history_paginated_page_3_per_page_20(self, mock_history_repository, mock_authenticator_service):
        """Test de cálculo de offset para página 3 con 20 por página"""
        service = ProductHistoryService()
        result = service.get_history_paginated(page=3, per_page=20)
        
        # offset debe ser (3-1) * 20 = 40
        mock_history_repository.get_all.assert_called_once_with(limit=20, offset=40)
    
    def test_get_history_paginated_with_user_id(self, mock_history_repository, mock_authenticator_service):
        """Test de obtención de historial filtrado por usuario"""
        service = ProductHistoryService()
        result = service.get_history_paginated(page=1, per_page=10, user_id="user-1")
        
        # Verificaciones
        assert len(result) == 2
        assert all(item["user"] == "Usuario Uno" for item in result)
        
        # Debe llamar get_by_user_id en lugar de get_all
        mock_history_repository.get_by_user_id.assert_called_once_with("user-1", limit=10, offset=0)
        mock_history_repository.get_all.assert_not_called()
    
    def test_get_history_paginated_user_page_2(self, mock_history_repository, mock_authenticator_service):
        """Test de paginación con filtro de usuario"""
        service = ProductHistoryService()
        result = service.get_history_paginated(page=2, per_page=5, user_id="user-1")
        
        # offset debe ser (2-1) * 5 = 5
        mock_history_repository.get_by_user_id.assert_called_once_with("user-1", limit=5, offset=5)
    
    def test_get_history_paginated_empty(self, mock_history_repository, mock_authenticator_service):
        """Test cuando no hay registros en el historial"""
        mock_history_repository.get_all.return_value = []
        
        service = ProductHistoryService()
        result = service.get_history_paginated()
        
        # Verificaciones
        assert len(result) == 0
        assert result == []
        mock_authenticator_service.get_user_name.assert_not_called()
    
    def test_get_history_paginated_repository_error(self, mock_history_repository, mock_authenticator_service):
        """Test cuando el repositorio lanza una excepción"""
        mock_history_repository.get_all.side_effect = Exception("Error de base de datos")
        
        service = ProductHistoryService()
        
        # Verificar que se lanza la excepción
        with pytest.raises(Exception) as exc_info:
            service.get_history_paginated()
        
        assert "Error al obtener historial" in str(exc_info.value)
    
    def test_get_history_count_success(self, mock_history_repository, mock_authenticator_service):
        """Test exitoso de obtención del conteo"""
        mock_history_repository.get_count.return_value = 50
        
        service = ProductHistoryService()
        result = service.get_history_count()
        
        assert result == 50
        mock_history_repository.get_count.assert_called_once_with(user_id=None)
    
    def test_get_history_count_with_user_id(self, mock_history_repository, mock_authenticator_service):
        """Test de conteo filtrado por usuario"""
        mock_history_repository.get_count.return_value = 10
        
        service = ProductHistoryService()
        result = service.get_history_count(user_id="user-1")
        
        assert result == 10
        mock_history_repository.get_count.assert_called_once_with(user_id="user-1")
    
    def test_get_history_count_zero(self, mock_history_repository, mock_authenticator_service):
        """Test cuando el conteo es cero"""
        mock_history_repository.get_count.return_value = 0
        
        service = ProductHistoryService()
        result = service.get_history_count()
        
        assert result == 0
    
    def test_get_history_count_error(self, mock_history_repository, mock_authenticator_service):
        """Test cuando el repositorio lanza excepción al contar"""
        mock_history_repository.get_count.side_effect = Exception("Error de base de datos")
        
        service = ProductHistoryService()
        
        with pytest.raises(Exception) as exc_info:
            service.get_history_count()
        
        assert "Error al obtener conteo" in str(exc_info.value)
    
    def test_history_data_structure(self, mock_history_repository, mock_authenticator_service):
        """Test de la estructura de datos retornada"""
        service = ProductHistoryService()
        result = service.get_history_paginated()
        
        # Verificar que cada registro tiene los campos requeridos
        for history_item in result:
            assert "id" in history_item
            assert "file_name" in history_item
            assert "created_at" in history_item
            assert "status" in history_item
            assert "result" in history_item
            assert "user" in history_item
            
            # Verificar tipos de datos
            assert isinstance(history_item["id"], str)
            assert isinstance(history_item["file_name"], str)
            assert isinstance(history_item["status"], str)
            assert isinstance(history_item["user"], str)
            assert isinstance(history_item["created_at"], str)
    
    def test_authenticator_service_called_per_history(self, mock_history_repository, mock_authenticator_service):
        """Test que el servicio de autenticación se llama para cada registro"""
        service = ProductHistoryService()
        result = service.get_history_paginated()
        
        # Debe llamarse 3 veces (una por cada registro)
        assert mock_authenticator_service.get_user_name.call_count == 3
    
    def test_service_initialization(self):
        """Test de inicialización del servicio"""
        with patch('app.services.product_history_service.ProductProcessedHistoryRepository'):
            with patch('app.services.product_history_service.AuthenticatorService'):
                service = ProductHistoryService()
                
                # Verificar que las dependencias se inicializaron
                assert hasattr(service, 'history_repository')
                assert hasattr(service, 'authenticator_service')
