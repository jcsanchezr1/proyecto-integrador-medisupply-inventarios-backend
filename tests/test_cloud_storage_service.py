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

    def test_generate_unique_filename_no_extension(self, cloud_service):
        """Prueba generate_unique_filename sin extensión"""
        service, _ = cloud_service
        
        # Caso: filename sin extensión
        result = service.generate_unique_filename("filename_without_extension")
        
        assert result.startswith("product_")
        assert result.endswith(".jpg")
        assert len(result) > 10  # Debe tener UUID

    def test_generate_unique_filename_empty_filename(self, cloud_service):
        """Prueba generate_unique_filename con filename vacío"""
        service, _ = cloud_service
        
        # Caso: filename vacío
        result = service.generate_unique_filename("")
        
        assert result.startswith("product_")
        assert result.endswith(".jpg")
        assert len(result) > 10  # Debe tener UUID

    def test_generate_unique_filename_none_filename(self, cloud_service):
        """Prueba generate_unique_filename con filename None"""
        service, _ = cloud_service
        
        # Caso: filename None
        result = service.generate_unique_filename(None)
        
        assert result.startswith("product_")
        assert result.endswith(".jpg")
        assert len(result) > 10  # Debe tener UUID

    def test_delete_image_blob_not_exists(self, cloud_service):
        """Prueba delete_image cuando el blob no existe"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob no existe
        mock_blob.exists.return_value = False
        
        success, message = service.delete_image("test-image.jpg")
        
        assert not success
        assert "El archivo no existe en el bucket" in message
        mock_blob.exists.assert_called_once()

    def test_get_image_url_blob_not_exists(self, cloud_service):
        """Prueba get_image_url cuando el blob no existeF"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob no existe
        mock_blob.exists.return_value = False
        
        result = service.get_image_url("test-image.jpg")
        
        assert result == ""
        mock_blob.exists.assert_called_once()

    def test_image_exists_exception(self, cloud_service):
        """Prueba image_exists cuando hay excepción"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que lance excepción
        mock_blob.exists.side_effect = Exception("Test exception")
        
        result = service.image_exists("test-image.jpg")
        
        assert result is False
        mock_blob.exists.assert_called_once()

    def test_image_exists_success(self, cloud_service):
        """Prueba image_exists cuando existe"""
        service, mock_blob = cloud_service
        
        # Configurar mock para que blob existe
        mock_blob.exists.return_value = True
        
        result = service.image_exists("test-image.jpg")
        
        assert result is True
        mock_blob.exists.assert_called_once()

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

    def test_generate_unique_filename_no_dot(self, cloud_service):
        """Prueba generate_unique_filename con filename sin punto"""
        service, _ = cloud_service
        
        # Caso: filename sin punto (no hay extensión)
        result = service.generate_unique_filename("filename_without_dot")
        
        assert result.startswith("product_")
        assert result.endswith(".jpg")
        assert len(result) > 10
