import pytest
import requests
from unittest.mock import Mock, patch
from app.external.provider_service import ProviderService
from app.models.provider import Provider
from app.exceptions.business_logic_error import BusinessLogicError


class TestProviderService:
    """Tests para el servicio de comunicación con proveedores externos"""
    
    @pytest.fixture
    def provider_service(self):
        """Crear instancia del servicio de proveedores"""
        return ProviderService()
    
    @pytest.fixture
    def sample_provider_data(self):
        """Datos de ejemplo de un proveedor"""
        return {
            "id": "32892e80-fbf9-4c7f-b211-228b3aa43985",
            "name": "Farmacia ABC",
            "email": "ventas500@hotmail.com",
            "phone": "3458829365",
            "logo_filename": "",
            "logo_url": "",
            "created_at": "2025-10-09T18:20:46.504233",
            "updated_at": "2025-10-09T18:20:46.504233"
        }
    
    @pytest.fixture
    def sample_provider_response(self, sample_provider_data):
        """Respuesta de ejemplo del servicio de proveedores"""
        return {
            "message": "Proveedor obtenido exitosamente",
            "data": sample_provider_data
        }
    
    def test_get_provider_by_id_success(self, provider_service, sample_provider_response):
        """Test exitoso de obtención de proveedor por ID"""
        with patch('requests.get') as mock_get:
            # Configurar mock de respuesta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_provider_response
            mock_get.return_value = mock_response
            
            # Ejecutar método
            result = provider_service.get_provider_by_id("32892e80-fbf9-4c7f-b211-228b3aa43985")
            
            # Verificaciones
            assert result is not None
            assert isinstance(result, Provider)
            assert result.id == "32892e80-fbf9-4c7f-b211-228b3aa43985"
            assert result.name == "Farmacia ABC"
            assert result.email == "ventas500@hotmail.com"
            assert result.phone == "3458829365"
            
            # Verificar que se hizo la petición correcta
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "32892e80-fbf9-4c7f-b211-228b3aa43985" in call_args[0][0]
            assert call_args[1]['timeout'] == 10
    
    def test_get_provider_by_id_not_found(self, provider_service):
        """Test cuando el proveedor no existe"""
        with patch('requests.get') as mock_get:
            # Configurar mock para 404
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # Ejecutar método
            result = provider_service.get_provider_by_id("non-existent-id")
            
            # Verificaciones
            assert result is None
    
    def test_get_provider_by_id_unexpected_response(self, provider_service):
        """Test con respuesta inesperada del servicio"""
        with patch('requests.get') as mock_get:
            # Configurar mock con respuesta inesperada
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "Error inesperado",
                "data": None
            }
            mock_get.return_value = mock_response
            
            # Ejecutar método
            result = provider_service.get_provider_by_id("test-id")
            
            # Verificaciones
            assert result is None
    
    def test_get_provider_by_id_service_error(self, provider_service):
        """Test cuando el servicio retorna error"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error del servidor
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.return_value = mock_response
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                provider_service.get_provider_by_id("test-id")
            
            assert "Error en servicio de proveedores: 500" in str(exc_info.value)
    
    def test_get_provider_by_id_timeout(self, provider_service):
        """Test cuando ocurre timeout"""
        with patch('requests.get') as mock_get:
            # Configurar mock para timeout
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                provider_service.get_provider_by_id("test-id")
            
            assert "Timeout al consultar el servicio de proveedores" in str(exc_info.value)
    
    def test_get_provider_by_id_connection_error(self, provider_service):
        """Test cuando ocurre error de conexión"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error de conexión
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                provider_service.get_provider_by_id("test-id")
            
            assert "Error de conexión con el servicio de proveedores" in str(exc_info.value)
    
    def test_get_provider_by_id_request_exception(self, provider_service):
        """Test cuando ocurre error de petición"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error de petición
            mock_get.side_effect = requests.exceptions.RequestException("Request failed")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                provider_service.get_provider_by_id("test-id")
            
            assert "Error al consultar proveedor: Request failed" in str(exc_info.value)
    
    def test_get_provider_by_id_generic_exception(self, provider_service):
        """Test cuando ocurre excepción genérica"""
        with patch('requests.get') as mock_get:
            # Configurar mock para excepción genérica
            mock_get.side_effect = Exception("Unexpected error")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                provider_service.get_provider_by_id("test-id")
            
            assert "Error inesperado al consultar proveedor: Unexpected error" in str(exc_info.value)
    
    def test_get_providers_batch_success(self, provider_service, sample_provider_response):
        """Test exitoso de obtención de múltiples proveedores"""
        provider_ids = ["provider-1", "provider-2"]
        
        with patch.object(provider_service, 'get_provider_by_id') as mock_get_provider:
            # Configurar mocks para diferentes proveedores
            mock_provider_1 = Provider(
                id="provider-1",
                name="Proveedor 1",
                email="test1@test.com",
                phone="1234567890"
            )
            mock_provider_2 = Provider(
                id="provider-2",
                name="Proveedor 2",
                email="test2@test.com",
                phone="0987654321"
            )
            
            mock_get_provider.side_effect = [mock_provider_1, mock_provider_2]
            
            # Ejecutar método
            result = provider_service.get_providers_batch(provider_ids)
            
            # Verificaciones
            assert len(result) == 2
            assert "provider-1" in result
            assert "provider-2" in result
            assert result["provider-1"] == mock_provider_1
            assert result["provider-2"] == mock_provider_2
            
            # Verificar que se llamó para cada proveedor
            assert mock_get_provider.call_count == 2
    
    def test_get_providers_batch_with_errors(self, provider_service):
        """Test de obtención de múltiples proveedores con errores"""
        provider_ids = ["provider-1", "provider-2"]
        
        with patch.object(provider_service, 'get_provider_by_id') as mock_get_provider:
            # Configurar mock para que el primer proveedor falle y el segundo funcione
            mock_provider_2 = Provider(
                id="provider-2",
                name="Proveedor 2",
                email="test2@test.com",
                phone="0987654321"
            )
            
            mock_get_provider.side_effect = [
                BusinessLogicError("Error en proveedor 1"),
                mock_provider_2
            ]
            
            # Ejecutar método
            result = provider_service.get_providers_batch(provider_ids)
            
            # Verificaciones
            assert len(result) == 2
            assert result["provider-1"] is None  # Error
            assert result["provider-2"] == mock_provider_2  # Éxito
    
    def test_get_provider_name_success(self, provider_service):
        """Test exitoso de obtención de nombre de proveedor"""
        with patch.object(provider_service, 'get_provider_by_id') as mock_get_provider:
            # Configurar mock
            mock_provider = Provider(
                id="test-id",
                name="Proveedor Test",
                email="test@test.com",
                phone="1234567890"
            )
            mock_get_provider.return_value = mock_provider
            
            # Ejecutar método
            result = provider_service.get_provider_name("test-id")
            
            # Verificaciones
            assert result == "Proveedor Test"
            mock_get_provider.assert_called_once_with("test-id")
    
    def test_get_provider_name_not_found(self, provider_service):
        """Test cuando el proveedor no se encuentra"""
        with patch.object(provider_service, 'get_provider_by_id') as mock_get_provider:
            # Configurar mock para retornar None
            mock_get_provider.return_value = None
            
            # Ejecutar método
            result = provider_service.get_provider_name("non-existent-id")
            
            # Verificaciones
            assert result == "Proveedor no asociado"
    
    def test_get_provider_name_error(self, provider_service):
        """Test cuando ocurre error al obtener proveedor"""
        with patch.object(provider_service, 'get_provider_by_id') as mock_get_provider:
            # Configurar mock para lanzar excepción
            mock_get_provider.side_effect = BusinessLogicError("Error de conexión")
            
            # Ejecutar método
            result = provider_service.get_provider_name("test-id")
            
            # Verificaciones
            assert result == "Proveedor no asociado"
    
    def test_service_configuration(self, provider_service):
        """Test de configuración del servicio"""
        # Verificar configuración por defecto
        assert provider_service.timeout == 10
        assert provider_service.base_url is not None
        assert "localhost:8083" in provider_service.base_url or "localhost" in provider_service.base_url or "medisupply-proveedores" in provider_service.base_url
    
    def test_url_construction(self, provider_service):
        """Test de construcción de URL"""
        provider_id = "test-provider-id"
        expected_url = f"{provider_service.base_url}/providers/{provider_id}"
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "Proveedor obtenido exitosamente",
                "data": {"id": provider_id, "name": "Test Provider"}
            }
            mock_get.return_value = mock_response
            
            provider_service.get_provider_by_id(provider_id)
            
            # Verificar que se construyó la URL correctamente
            call_args = mock_get.call_args
            assert call_args[0][0] == expected_url
    
    def test_timeout_configuration(self, provider_service):
        """Test de configuración de timeout"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "Proveedor obtenido exitosamente",
                "data": {"id": "test", "name": "Test Provider"}
            }
            mock_get.return_value = mock_response
            
            provider_service.get_provider_by_id("test-id")
            
            # Verificar que se pasó el timeout correcto
            call_args = mock_get.call_args
            assert call_args[1]['timeout'] == 10
