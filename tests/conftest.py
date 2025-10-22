"""
Configuración global de pytest para el proyecto de inventarios
"""
import pytest
from unittest.mock import patch, MagicMock
import sys

def pytest_configure(config):
    """Configuración que se ejecuta antes de que se importen los módulos de prueba"""
    # Mock de Google Cloud Storage antes de que se importe cualquier módulo
    mock_storage = MagicMock()
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    
    mock_storage.Client.return_value = mock_client
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_blob.exists.return_value = True
    mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/test-bucket/test-image.jpg?signature=test"
    mock_blob.upload_from_file.return_value = None
    
    # Mock para GoogleCloudError
    mock_google_cloud_error = MagicMock()
    mock_google_cloud_error.GoogleCloudError = Exception
    
    # Mock para PIL (Pillow)
    mock_pil = MagicMock()
    mock_image = MagicMock()
    mock_image.open.return_value = mock_image
    mock_image.verify.return_value = None
    mock_pil.Image = mock_image
    
    # Mock para pandas
    mock_pandas = MagicMock()
    mock_df = MagicMock()
    mock_df.__len__ = MagicMock(return_value=50)
    mock_pandas.read_csv = MagicMock(return_value=mock_df)
    mock_pandas.read_excel = MagicMock(return_value=mock_df)
    
    # Mock para openpyxl
    mock_openpyxl = MagicMock()
    
    # Mock para Google Cloud Pub/Sub
    mock_pubsub = MagicMock()
    mock_publisher = MagicMock()
    mock_pubsub.PublisherClient = MagicMock(return_value=mock_publisher)
    
    # Aplicar mocks a sys.modules
    sys.modules['google'] = MagicMock()
    sys.modules['google.cloud'] = MagicMock()
    sys.modules['google.cloud.storage'] = mock_storage
    sys.modules['google.cloud.exceptions'] = mock_google_cloud_error
    sys.modules['google.cloud.pubsub_v1'] = mock_pubsub
    sys.modules['google.auth'] = MagicMock()
    sys.modules['google.auth.impersonated_credentials'] = MagicMock()
    sys.modules['PIL'] = mock_pil
    sys.modules['PIL.Image'] = mock_image
    sys.modules['pandas'] = mock_pandas
    sys.modules['openpyxl'] = mock_openpyxl
