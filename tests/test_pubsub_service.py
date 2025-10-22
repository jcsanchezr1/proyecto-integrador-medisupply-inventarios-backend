"""
Tests para PubSubService
"""
import pytest
from unittest.mock import MagicMock, patch
from google.cloud.exceptions import GoogleCloudError
from app.services.pubsub_service import PubSubService
from app.config.settings import Config


class TestPubSubService:
    """Tests para PubSubService"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock de Config"""
        config = MagicMock()
        config.GCP_PROJECT_ID = 'test-project'
        config.PUBSUB_TOPIC_PRODUCTS_IMPORT = 'test-topic'
        config.GOOGLE_APPLICATION_CREDENTIALS = ''
        return config
    
    @pytest.fixture
    def pubsub_service(self, mock_config):
        """Instancia de PubSubService con config mockeado"""
        with patch('app.services.pubsub_service.pubsub_v1.PublisherClient'):
            return PubSubService(config=mock_config)
    
    def test_publish_message_success(self, pubsub_service, mock_config):
        """Test: Publicar mensaje exitosamente"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'history_id': '123', 'event_type': 'test'}
        result = pubsub_service.publish_message('test-topic', message_data)
        
        assert result == 'message-id-123'
        mock_publisher.topic_path.assert_called_once_with('test-project', 'test-topic')
        mock_publisher.publish.assert_called_once()
    
    def test_publish_message_google_cloud_error(self, pubsub_service):
        """Test: Error de Google Cloud al publicar mensaje"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.side_effect = GoogleCloudError('Cloud error')
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'history_id': '123'}
        
        with pytest.raises(GoogleCloudError, match="Error al publicar mensaje en Pub/Sub"):
            pubsub_service.publish_message('test-topic', message_data)
    
    def test_publish_message_generic_error(self, pubsub_service):
        """Test: Error genérico al publicar mensaje"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.side_effect = Exception('Generic error')
        
        pubsub_service._publisher = mock_publisher
        
        message_data = {'history_id': '123'}
        
        with pytest.raises(Exception, match="Error al publicar mensaje en Pub/Sub"):
            pubsub_service.publish_message('test-topic', message_data)
    
    def test_publish_product_import_event_success(self, pubsub_service, mock_config):
        """Test: Publicar evento de importación de productos exitosamente"""
        mock_publisher = MagicMock()
        mock_future = MagicMock()
        mock_future.result.return_value = 'message-id-123'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'projects/test-project/topics/test-topic'
        
        pubsub_service._publisher = mock_publisher
        
        result = pubsub_service.publish_product_import_event('history-123')
        
        assert result == 'message-id-123'
        mock_publisher.publish.assert_called_once()
    
    def test_publish_product_import_event_error(self, pubsub_service):
        """Test: Error al publicar evento de importación de productos"""
        mock_publisher = MagicMock()
        mock_publisher.topic_path.side_effect = Exception('Error')
        
        pubsub_service._publisher = mock_publisher
        
        with pytest.raises(Exception):
            pubsub_service.publish_product_import_event('history-123')
    
    def test_publisher_property_lazy_initialization(self, mock_config):
        """Test: Inicialización lazy del publisher"""
        with patch('app.services.pubsub_service.pubsub_v1.PublisherClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            service = PubSubService(config=mock_config)
            assert service._publisher is None
            
            # Acceder a la propiedad para inicializar
            publisher = service.publisher
            
            assert publisher is not None
            mock_client_class.assert_called_once()
    
    def test_publisher_property_initialization_error(self, mock_config):
        """Test: Error al inicializar publisher"""
        with patch('app.services.pubsub_service.pubsub_v1.PublisherClient') as mock_client_class:
            mock_client_class.side_effect = Exception('Initialization error')
            
            service = PubSubService(config=mock_config)
            
            with pytest.raises(GoogleCloudError, match="Error al inicializar cliente de Pub/Sub"):
                _ = service.publisher

