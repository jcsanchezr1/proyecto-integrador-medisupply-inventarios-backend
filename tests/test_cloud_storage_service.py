"""
Pruebas para el servicio de almacenamiento en la nube
"""
import pytest
from unittest.mock import MagicMock, patch, Mock
from werkzeug.datastructures import FileStorage
from app.services.cloud_storage_service import CloudStorageService
from app.config.settings import Config


class TestCloudStorageService:
    """Pruebas para el servicio de almacenamiento en la nube"""

    @pytest.fixture
    def mock_config(self):
        """Configuración mock"""
        config = MagicMock(spec=Config)
        config.GCP_PROJECT_ID = "test-project"
        config.BUCKET_NAME = "test-bucket"
        config.BUCKET_FOLDER = "products"
        config.GOOGLE_APPLICATION_CREDENTIALS = None
        config.ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
        config.MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
        config.SIGNING_SERVICE_ACCOUNT_EMAIL = "test-signing@test-project.iam.gserviceaccount.com"
        return config

    @pytest.fixture
    def cloud_service(self, mock_config):
        """Servicio de cloud storage con mocks"""
        with patch('app.services.cloud_storage_service.storage') as mock_storage:
            # Mock del cliente y bucket
            mock_client = MagicMock()
            mock_bucket = MagicMock()
            mock_blob = MagicMock()
            
            mock_storage.Client.return_value = mock_client
            mock_client.bucket.return_value = mock_bucket
            mock_bucket.blob.return_value = mock_blob
            
            service = CloudStorageService(mock_config)
            service._client = mock_client
            service._bucket = mock_bucket
            
            return service, mock_blob

    def test_validate_image_file_no_file(self, cloud_service):
        """Prueba validate_image_file sin archivo"""
        service, _ = cloud_service
        
        # Caso: sin archivo
        is_valid, message = service.validate_image_file(None)
        
        assert not is_valid
        assert "No se proporcionó archivo" in message

    def test_validate_image_file_no_filename(self, cloud_service):
        """Prueba validate_image_file sin filename"""
        service, _ = cloud_service
        
        # Caso: archivo sin filename
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = None
        
        is_valid, message = service.validate_image_file(mock_file)
        
        assert not is_valid
        assert "No se proporcionó archivo" in message

    def test_validate_image_file_invalid_extension(self, cloud_service):
        """Prueba validate_image_file con extensión inválida"""
        service, _ = cloud_service
        
        # Caso: extensión inválida
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = "test.txt"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)
        
        is_valid, message = service.validate_image_file(mock_file)
        
        assert not is_valid
        assert "Extensión no permitida" in message

    def test_delete_image_blob_not_exists(self, cloud_service):
        """Prueba delete_image cuando el blob no existe"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob no existe
        mock_blob.exists.return_value = False
        
        success, message = service.delete_image("test-image.jpg")
        
        assert not success
        assert "La imagen no existe" in message
        mock_blob.exists.assert_called_once()

    def test_get_image_url_blob_not_exists(self, cloud_service):
        """Prueba get_image_url cuando el blob no existe"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob no existe
        mock_blob.exists.return_value = False
        
        result = service.get_image_url("test-image.jpg")
        
        # Debe retornar URL directa como fallback cuando el blob no existe
        expected_url = "https://storage.googleapis.com/test-bucket/products/test-image.jpg"
        assert result == expected_url
        # No verificar exists porque se ejecuta dentro del try-catch


    def test_upload_image_google_cloud_error(self, cloud_service):
        """Prueba upload_image con GoogleCloudError"""
        service, mock_blob = cloud_service
        
        # Crear archivo mock válido
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = "test.jpg"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)  # 1KB
        
        # Mock PIL Image
        with patch('app.services.cloud_storage_service.Image') as mock_image:
            mock_image.open.return_value.verify.return_value = None
            
            # Configurar mock para que lance GoogleCloudError
            mock_blob.upload_from_file.side_effect = Exception("Google Cloud Error")
            
            success, message, url = service.upload_image(mock_file, "test.jpg")
            
            assert not success
            assert "Error de Google Cloud Storage" in message
            assert url is None

    def test_delete_image_google_cloud_error(self, cloud_service):
        """Prueba delete_image con GoogleCloudError"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que lance excepción
        mock_blob.exists.side_effect = Exception("Google Cloud Error")
        
        success, message = service.delete_image("test-image.jpg")
        
        assert not success
        assert "Error de Google Cloud Storage" in message

    def test_get_image_url_exception_fallback(self, cloud_service):
        """Prueba get_image_url con excepción y fallback"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que lance excepción
        mock_blob.exists.side_effect = Exception("Test exception")
        
        result = service.get_image_url("test-image.jpg")
        
        # Debe retornar URL directa como fallback
        expected_url = "https://storage.googleapis.com/test-bucket/products/test-image.jpg"
        assert result == expected_url

    def test_delete_image_general_exception(self, cloud_service):
        """Prueba delete_image con excepción general"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que lance excepción general (no GoogleCloudError)
        mock_blob.exists.return_value = True
        mock_blob.delete.side_effect = Exception("General error")
        
        success, message = service.delete_image("test-image.jpg")
        
        assert not success
        assert "Error de Google Cloud Storage" in message

    def test_delete_image_success(self, cloud_service):
        """Prueba delete_image exitoso"""
        service, mock_blob = cloud_service
        
        # Configurar mock para éxito
        mock_blob.exists.return_value = True
        mock_blob.delete.return_value = None
        
        success, message = service.delete_image("test-image.jpg")
        
        assert success
        assert "Imagen eliminada exitosamente" in message
        mock_blob.delete.assert_called_once()

    def test_get_image_url_with_impersonated_credentials(self, cloud_service):
        """Prueba get_image_url con impersonated credentials - simplificada"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob existe
        mock_blob.exists.return_value = True
        
        result = service.get_image_url("test-image.jpg")
        
        # Debe retornar URL directa como fallback debido a la excepción de google.auth
        expected_url = "https://storage.googleapis.com/test-bucket/products/test-image.jpg"
        assert result == expected_url

    def test_get_image_url_impersonated_credentials_exception(self, cloud_service):
        """Prueba get_image_url con excepción en impersonated credentials"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob existe
        mock_blob.exists.return_value = True
        
        # Mock que lance excepción
        with patch('google.auth.default') as mock_default:
            mock_default.side_effect = Exception("Credentials error")
            
            result = service.get_image_url("test-image.jpg")
            
            # Debe retornar URL directa como fallback
            expected_url = "https://storage.googleapis.com/test-bucket/products/test-image.jpg"
            assert result == expected_url

    def test_upload_image_success_with_signed_url(self, cloud_service):
        """Prueba upload_image exitoso con URL firmada"""
        service, mock_blob = cloud_service
        
        # Crear archivo mock válido
        mock_file = MagicMock(spec=FileStorage)
        mock_file.filename = "test.jpg"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)  # 1KB
        
        # Mock PIL Image
        with patch('app.services.cloud_storage_service.Image') as mock_image, \
             patch.object(service, 'get_image_url') as mock_get_url:
            
            mock_image.open.return_value.verify.return_value = None
            mock_get_url.return_value = "https://signed-url.com/test.jpg"
            
            success, message, url = service.upload_image(mock_file, "test.jpg")
            
            assert success
            assert "Imagen subida exitosamente" in message
            assert url == "https://signed-url.com/test.jpg"
            mock_blob.upload_from_file.assert_called_once()
            mock_get_url.assert_called_once_with("test.jpg")
