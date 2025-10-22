import pytest
import requests
from unittest.mock import Mock, patch
from app.external.authenticator_service import AuthenticatorService
from app.exceptions.business_logic_error import BusinessLogicError


class TestAuthenticatorService:
    """Tests para el servicio de comunicación con el servicio de autenticación"""
    
    @pytest.fixture
    def authenticator_service(self):
        """Crear instancia del servicio de autenticación"""
        return AuthenticatorService()
    
    @pytest.fixture
    def sample_user_data(self):
        """Datos de ejemplo de un usuario"""
        return {
            "id": "8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05",
            "name": "medisupply05",
            "tax_id": None,
            "email": "medisupply05@gmail.com",
            "address": None,
            "phone": None,
            "institution_type": None,
            "logo_filename": None,
            "logo_url": None,
            "specialty": None,
            "applicant_name": None,
            "applicant_email": None,
            "latitude": None,
            "longitude": None,
            "enabled": True,
            "created_at": "2025-10-21T16:45:04.561982+00:00",
            "updated_at": "2025-10-21T16:45:04.561982+00:00"
        }
    
    @pytest.fixture
    def sample_user_response(self, sample_user_data):
        """Respuesta de ejemplo del servicio de autenticación"""
        return {
            "message": "Usuario obtenido exitosamente",
            "data": sample_user_data
        }
    
    def test_get_user_by_id_success(self, authenticator_service, sample_user_response, sample_user_data):
        """Test exitoso de obtención de usuario por ID"""
        with patch('requests.get') as mock_get:
            # Configurar mock de respuesta
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_user_response
            mock_get.return_value = mock_response
            
            # Ejecutar método
            result = authenticator_service.get_user_by_id("8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05")
            
            # Verificaciones
            assert result is not None
            assert isinstance(result, dict)
            assert result["id"] == "8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05"
            assert result["name"] == "medisupply05"
            assert result["email"] == "medisupply05@gmail.com"
            assert result["enabled"] is True
            
            # Verificar que se hizo la petición correcta
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "8f1b7d3f-4e3b-4f5e-9b2a-7d2a6b9f1c05" in call_args[0][0]
            assert call_args[1]['timeout'] == 10
    
    def test_get_user_by_id_not_found(self, authenticator_service):
        """Test cuando el usuario no existe"""
        with patch('requests.get') as mock_get:
            # Configurar mock para 404
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response
            
            # Ejecutar método
            result = authenticator_service.get_user_by_id("non-existent-id")
            
            # Verificaciones
            assert result is None
    
    def test_get_user_by_id_unexpected_response(self, authenticator_service):
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
            result = authenticator_service.get_user_by_id("test-id")
            
            # Verificaciones
            assert result is None
    
    def test_get_user_by_id_service_error(self, authenticator_service):
        """Test cuando el servicio retorna error"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error del servidor
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.return_value = mock_response
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                authenticator_service.get_user_by_id("test-id")
            
            assert "Error en servicio de autenticación: 500" in str(exc_info.value)
    
    def test_get_user_by_id_timeout(self, authenticator_service):
        """Test cuando ocurre timeout"""
        with patch('requests.get') as mock_get:
            # Configurar mock para timeout
            mock_get.side_effect = requests.exceptions.Timeout("Timeout")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                authenticator_service.get_user_by_id("test-id")
            
            assert "Timeout al consultar el servicio de autenticación" in str(exc_info.value)
    
    def test_get_user_by_id_connection_error(self, authenticator_service):
        """Test cuando ocurre error de conexión"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error de conexión
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                authenticator_service.get_user_by_id("test-id")
            
            assert "Error de conexión con el servicio de autenticación" in str(exc_info.value)
    
    def test_get_user_by_id_request_exception(self, authenticator_service):
        """Test cuando ocurre error de petición"""
        with patch('requests.get') as mock_get:
            # Configurar mock para error de petición
            mock_get.side_effect = requests.exceptions.RequestException("Request failed")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                authenticator_service.get_user_by_id("test-id")
            
            assert "Error al consultar usuario: Request failed" in str(exc_info.value)
    
    def test_get_user_by_id_generic_exception(self, authenticator_service):
        """Test cuando ocurre excepción genérica"""
        with patch('requests.get') as mock_get:
            # Configurar mock para excepción genérica
            mock_get.side_effect = Exception("Unexpected error")
            
            # Ejecutar método y verificar excepción
            with pytest.raises(BusinessLogicError) as exc_info:
                authenticator_service.get_user_by_id("test-id")
            
            assert "Error inesperado al consultar usuario: Unexpected error" in str(exc_info.value)
    
    def test_get_user_name_success(self, authenticator_service):
        """Test exitoso de obtención de nombre de usuario"""
        with patch.object(authenticator_service, 'get_user_by_id') as mock_get_user:
            # Configurar mock
            mock_user = {
                "id": "test-id",
                "name": "Usuario Test",
                "email": "test@test.com"
            }
            mock_get_user.return_value = mock_user
            
            # Ejecutar método
            result = authenticator_service.get_user_name("test-id")
            
            # Verificaciones
            assert result == "Usuario Test"
            mock_get_user.assert_called_once_with("test-id")
    
    def test_get_user_name_not_found(self, authenticator_service):
        """Test cuando el usuario no se encuentra"""
        with patch.object(authenticator_service, 'get_user_by_id') as mock_get_user:
            # Configurar mock para retornar None
            mock_get_user.return_value = None
            
            # Ejecutar método
            result = authenticator_service.get_user_name("non-existent-id")
            
            # Verificaciones
            assert result == "Usuario no disponible"
    
    def test_get_user_name_no_name_field(self, authenticator_service):
        """Test cuando el usuario no tiene el campo name"""
        with patch.object(authenticator_service, 'get_user_by_id') as mock_get_user:
            # Configurar mock sin campo name
            mock_user = {
                "id": "test-id",
                "email": "test@test.com"
            }
            mock_get_user.return_value = mock_user
            
            # Ejecutar método
            result = authenticator_service.get_user_name("test-id")
            
            # Verificaciones
            assert result == "Usuario no disponible"
    
    def test_get_user_name_error(self, authenticator_service):
        """Test cuando ocurre error al obtener usuario"""
        with patch.object(authenticator_service, 'get_user_by_id') as mock_get_user:
            # Configurar mock para lanzar excepción
            mock_get_user.side_effect = BusinessLogicError("Error de conexión")
            
            # Ejecutar método
            result = authenticator_service.get_user_name("test-id")
            
            # Verificaciones
            assert result == "Usuario no disponible"
    
    def test_service_configuration(self, authenticator_service):
        """Test de configuración del servicio"""
        # Verificar configuración por defecto
        assert authenticator_service.timeout == 10
        assert authenticator_service.base_url is not None
        # Verificar que la URL sea válida (contenga http/https y un dominio)
        assert authenticator_service.base_url.startswith(("http://", "https://"))
        assert "." in authenticator_service.base_url or "localhost" in authenticator_service.base_url
    
    def test_url_construction(self, authenticator_service):
        """Test de construcción de URL"""
        user_id = "test-user-id"
        expected_url = f"{authenticator_service.base_url}/auth/user/{user_id}"
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "Usuario obtenido exitosamente",
                "data": {"id": user_id, "name": "Test User"}
            }
            mock_get.return_value = mock_response
            
            authenticator_service.get_user_by_id(user_id)
            
            # Verificar que se construyó la URL correctamente
            call_args = mock_get.call_args
            assert call_args[0][0] == expected_url
    
    def test_timeout_configuration(self, authenticator_service):
        """Test de configuración de timeout"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "Usuario obtenido exitosamente",
                "data": {"id": "test", "name": "Test User"}
            }
            mock_get.return_value = mock_response
            
            authenticator_service.get_user_by_id("test-id")
            
            # Verificar que se pasó el timeout correcto
            call_args = mock_get.call_args
            assert call_args[1]['timeout'] == 10

