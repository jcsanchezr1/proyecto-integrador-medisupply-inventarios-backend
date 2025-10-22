"""
Tests para ProductImportService
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app.services.product_import_service import ProductImportService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductImportService:
    """Tests para ProductImportService"""
    
    @pytest.fixture
    def mock_config(self):
        """Mock de Config"""
        config = MagicMock()
        config.MAX_IMPORT_PRODUCTS = 100
        config.BUCKET_FOLDER_PROCESSED_PRODUCTS = 'processed-products'
        config.PUBSUB_TOPIC_PRODUCTS_IMPORT = 'test-topic'
        return config
    
    @pytest.fixture
    def mock_history_repository(self):
        """Mock del ProductProcessedHistoryRepository"""
        return MagicMock()
    
    @pytest.fixture
    def mock_cloud_storage_service(self):
        """Mock del CloudStorageService"""
        return MagicMock()
    
    @pytest.fixture
    def mock_pubsub_service(self):
        """Mock del PubSubService"""
        return MagicMock()
    
    @pytest.fixture
    def product_import_service(self, mock_config, mock_history_repository, 
                               mock_cloud_storage_service, mock_pubsub_service):
        """Instancia de ProductImportService con dependencias mockeadas"""
        return ProductImportService(
            config=mock_config,
            history_repository=mock_history_repository,
            cloud_storage_service=mock_cloud_storage_service,
            pubsub_service=mock_pubsub_service
        )
    
    @pytest.fixture
    def valid_csv_file(self):
        """Archivo CSV válido"""
        csv_content = b"sku,name,quantity\nMED-0001,Product 1,10\nMED-0002,Product 2,20"
        return FileStorage(
            stream=BytesIO(csv_content),
            filename='products.csv',
            content_type='text/csv'
        )
    
    @pytest.fixture
    def valid_excel_file(self):
        """Archivo Excel válido simulado"""
        # Simular contenido de Excel
        excel_content = b"PK\x03\x04..." # Contenido mínimo de Excel
        return FileStorage(
            stream=BytesIO(excel_content),
            filename='products.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    def test_validate_required_fields_success(self, product_import_service, valid_csv_file):
        """Test: Validar campos requeridos exitosamente"""
        product_import_service._validate_required_fields(valid_csv_file, 'user123')
        # No debe lanzar excepción
    
    def test_validate_required_fields_missing_file(self, product_import_service):
        """Test: Error al validar sin archivo"""
        with pytest.raises(ValidationError, match="El archivo es obligatorio"):
            product_import_service._validate_required_fields(None, 'user123')
    
    def test_validate_required_fields_missing_user_id(self, product_import_service, valid_csv_file):
        """Test: Error al validar sin userId"""
        with pytest.raises(ValidationError, match="El userId es obligatorio"):
            product_import_service._validate_required_fields(valid_csv_file, '')
    
    def test_validate_file_type_csv_success(self, product_import_service, valid_csv_file):
        """Test: Validar tipo de archivo CSV exitosamente"""
        product_import_service._validate_file_type(valid_csv_file)
        # No debe lanzar excepción
    
    def test_validate_file_type_excel_success(self, product_import_service, valid_excel_file):
        """Test: Validar tipo de archivo Excel exitosamente"""
        product_import_service._validate_file_type(valid_excel_file)
        # No debe lanzar excepción
    
    def test_validate_file_type_invalid(self, product_import_service):
        """Test: Error al validar tipo de archivo inválido"""
        invalid_file = FileStorage(
            stream=BytesIO(b"content"),
            filename='products.txt',
            content_type='text/plain'
        )
        
        with pytest.raises(ValidationError, match="Solo se permiten archivos CSV/Excel"):
            product_import_service._validate_file_type(invalid_file)
    
    def test_validate_file_type_no_extension(self, product_import_service):
        """Test: Error al validar archivo sin extensión"""
        invalid_file = FileStorage(
            stream=BytesIO(b"content"),
            filename='products',
            content_type='text/plain'
        )
        
        with pytest.raises(ValidationError, match="El archivo no tiene extensión"):
            product_import_service._validate_file_type(invalid_file)
    
    @patch('app.services.product_import_service.pd.read_csv')
    def test_validate_records_count_success(self, mock_read_csv, product_import_service, valid_csv_file):
        """Test: Validar número de registros exitosamente"""
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=50)
        mock_read_csv.return_value = mock_df
        
        product_import_service._validate_records_count(valid_csv_file)
        # No debe lanzar excepción
    
    @patch('app.services.product_import_service.pd.read_csv')
    def test_validate_records_count_exceeds_limit(self, mock_read_csv, product_import_service, valid_csv_file):
        """Test: Error al validar número de registros excede límite"""
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=101)
        mock_read_csv.return_value = mock_df
        
        with pytest.raises(ValidationError, match="Solo se permiten cargar 100 productos"):
            product_import_service._validate_records_count(valid_csv_file)
    
    @patch('app.services.product_import_service.pd.read_excel')
    def test_validate_records_count_excel(self, mock_read_excel, product_import_service, valid_excel_file):
        """Test: Validar número de registros en archivo Excel"""
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=50)
        mock_read_excel.return_value = mock_df
        
        product_import_service._validate_records_count(valid_excel_file)
        # No debe lanzar excepción
    
    def test_generate_new_filename(self, product_import_service):
        """Test: Generar nuevo nombre de archivo con UUID"""
        original_filename = 'products.csv'
        new_filename = product_import_service._generate_new_filename(original_filename)
        
        assert 'products_' in new_filename
        assert '.csv' in new_filename
        assert len(new_filename) > len(original_filename)
    
    def test_generate_new_filename_without_extension(self, product_import_service):
        """Test: Generar nuevo nombre de archivo sin extensión"""
        original_filename = 'products'
        new_filename = product_import_service._generate_new_filename(original_filename)
        
        assert 'products_' in new_filename
    
    def test_upload_file_to_storage_success(self, product_import_service, 
                                           mock_cloud_storage_service, valid_csv_file):
        """Test: Subir archivo a Cloud Storage exitosamente"""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_cloud_storage_service.bucket = mock_bucket
        
        product_import_service._upload_file_to_storage(valid_csv_file, 'test.csv')
        
        mock_bucket.blob.assert_called_once()
        mock_blob.upload_from_file.assert_called_once()
    
    def test_upload_file_to_storage_error(self, product_import_service, 
                                         mock_cloud_storage_service, valid_csv_file):
        """Test: Error al subir archivo a Cloud Storage"""
        mock_bucket = MagicMock()
        mock_bucket.blob.side_effect = Exception('Storage error')
        mock_cloud_storage_service.bucket = mock_bucket
        
        with pytest.raises(BusinessLogicError, match="Error al subir archivo a Cloud Storage"):
            product_import_service._upload_file_to_storage(valid_csv_file, 'test.csv')
    
    def test_create_history_record_success(self, product_import_service, mock_history_repository):
        """Test: Crear registro de historial exitosamente"""
        mock_history = MagicMock()
        mock_history.id = 'history-123'
        mock_history_repository.create.return_value = mock_history
        
        result = product_import_service._create_history_record('test.csv', 'user123')
        
        assert result.id == 'history-123'
        mock_history_repository.create.assert_called_once()
    
    def test_create_history_record_error(self, product_import_service, mock_history_repository):
        """Test: Error al crear registro de historial"""
        mock_history_repository.create.side_effect = Exception('Database error')
        
        with pytest.raises(BusinessLogicError, match="Error al crear registro de historial"):
            product_import_service._create_history_record('test.csv', 'user123')
    
    def test_publish_import_event_success(self, product_import_service, mock_pubsub_service):
        """Test: Publicar evento de importación exitosamente"""
        mock_pubsub_service.publish_product_import_event.return_value = 'message-123'
        
        product_import_service._publish_import_event('history-123')
        
        mock_pubsub_service.publish_product_import_event.assert_called_once_with('history-123')
    
    def test_publish_import_event_error(self, product_import_service, mock_pubsub_service):
        """Test: Error al publicar evento de importación"""
        mock_pubsub_service.publish_product_import_event.side_effect = Exception('PubSub error')
        
        with pytest.raises(BusinessLogicError, match="Error al publicar evento de importación"):
            product_import_service._publish_import_event('history-123')
    
    @patch('app.services.product_import_service.pd.read_csv')
    def test_import_products_file_success(self, mock_read_csv, product_import_service, 
                                         mock_history_repository, mock_cloud_storage_service,
                                         mock_pubsub_service, valid_csv_file):
        """Test: Importar archivo de productos exitosamente"""
        # Mock validaciones
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=50)
        mock_read_csv.return_value = mock_df
        
        # Mock Cloud Storage
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_bucket.blob.return_value = mock_blob
        mock_cloud_storage_service.bucket = mock_bucket
        
        # Mock repository
        mock_history = MagicMock()
        mock_history.id = 'history-123'
        mock_history_repository.create.return_value = mock_history
        
        # Mock Pub/Sub
        mock_pubsub_service.publish_product_import_event.return_value = 'message-123'
        
        history_id, message = product_import_service.import_products_file(valid_csv_file, 'user123')
        
        assert history_id == 'history-123'
        assert message == 'Archivo cargado exitosamente'
        mock_history_repository.create.assert_called_once()
        mock_pubsub_service.publish_product_import_event.assert_called_once()
    
    def test_import_products_file_validation_error(self, product_import_service):
        """Test: Error de validación al importar archivo"""
        with pytest.raises(ValidationError, match="El archivo es obligatorio"):
            product_import_service.import_products_file(None, 'user123')
    
    @patch('app.services.product_import_service.pd.read_csv')
    def test_import_products_file_business_logic_error(self, mock_read_csv, product_import_service,
                                                       mock_history_repository, valid_csv_file):
        """Test: Error de lógica de negocio al importar archivo"""
        # Mock validaciones
        mock_df = MagicMock()
        mock_df.__len__ = MagicMock(return_value=50)
        mock_read_csv.return_value = mock_df
        
        # Mock error en repository
        mock_history_repository.create.side_effect = Exception('Database error')
        
        with pytest.raises(BusinessLogicError):
            product_import_service.import_products_file(valid_csv_file, 'user123')

