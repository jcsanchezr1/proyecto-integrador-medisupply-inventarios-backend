"""
Tests para ProductImportController
"""
import pytest
from unittest.mock import MagicMock, patch
from io import BytesIO
from werkzeug.datastructures import FileStorage
from flask import Flask
from app.controllers.product_import_controller import ProductImportController
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductImportController:
    """Tests para ProductImportController"""
    
    @pytest.fixture
    def mock_product_import_service(self):
        """Mock del ProductImportService"""
        return MagicMock()
    
    @pytest.fixture
    def controller(self, mock_product_import_service):
        """Instancia de ProductImportController con service mockeado"""
        return ProductImportController(product_import_service=mock_product_import_service)
    
    @pytest.fixture
    def app(self):
        """Instancia de la aplicación Flask"""
        from app import create_app
        return create_app()
    
    @pytest.fixture
    def valid_csv_file(self):
        """Archivo CSV válido"""
        csv_content = b"sku,name,quantity\nMED-0001,Product 1,10"
        return FileStorage(
            stream=BytesIO(csv_content),
            filename='products.csv',
            content_type='text/csv'
        )
    
    def test_post_success(self, controller, mock_product_import_service, app, valid_csv_file):
        """Test: Importar productos exitosamente"""
        mock_product_import_service.import_products_file.return_value = ('history-123', 'Archivo cargado exitosamente')
        
        with app.test_request_context(
            method='POST',
            content_type='multipart/form-data'
        ):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                # Configurar mock con MagicMock para evitar comportamiento async
                mock_files = MagicMock()
                mock_files.get = MagicMock(return_value=valid_csv_file)
                mock_form = MagicMock()
                mock_form.get = MagicMock(return_value='user123')
                
                mock_request.content_type = 'multipart/form-data'
                mock_request.files = mock_files
                mock_request.form = mock_form
                
                response, status_code = controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['data']['history_id'] == 'history-123'
        assert response['message'] == 'Archivo cargado exitosamente'
    
    def test_post_unsupported_content_type(self, controller, app):
        """Test: Error por Content-Type no soportado (sin archivo)"""
        with app.test_request_context(method='POST', content_type='application/json'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'application/json'
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert "El campo 'file' es obligatorio" in response['error']
        assert 'multipart/form-data' in response.get('details', '')
    
    def test_post_missing_file(self, controller, app):
        """Test: Error por archivo faltante"""
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_files = MagicMock()
                mock_files.get = MagicMock(return_value=None)
                mock_form = MagicMock()
                mock_form.get = MagicMock(return_value='user123')
                
                mock_request.content_type = 'multipart/form-data'
                mock_request.files = mock_files
                mock_request.form = mock_form
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert "El campo 'file' es obligatorio" in response['error']
    
    def test_post_missing_user_id(self, controller, app, valid_csv_file):
        """Test: Error por userId faltante"""
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_files = MagicMock()
                mock_files.get = MagicMock(return_value=valid_csv_file)
                mock_form = MagicMock()
                mock_form.get = MagicMock(return_value=None)
                
                mock_request.content_type = 'multipart/form-data'
                mock_request.files = mock_files
                mock_request.form = mock_form
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert "El campo 'userId' es obligatorio" in response['error']
    
    def test_post_validation_error(self, controller, mock_product_import_service, app, valid_csv_file):
        """Test: Error de validación durante la importación"""
        mock_product_import_service.import_products_file.side_effect = ValidationError("Solo se permiten archivos CSV/Excel")
        
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'multipart/form-data'
                mock_request.files.get.return_value = valid_csv_file
                mock_request.form.get.return_value = 'user123'
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert 'Error de validación' in response['error']
    
    def test_post_business_logic_error(self, controller, mock_product_import_service, app, valid_csv_file):
        """Test: Error de lógica de negocio durante la importación"""
        mock_product_import_service.import_products_file.side_effect = BusinessLogicError("Error al subir archivo")
        
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'multipart/form-data'
                mock_request.files.get.return_value = valid_csv_file
                mock_request.form.get.return_value = 'user123'
                
                response, status_code = controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert 'Error de lógica de negocio' in response['error']
    
    def test_post_generic_error(self, controller, mock_product_import_service, app, valid_csv_file):
        """Test: Error genérico durante la importación"""
        mock_product_import_service.import_products_file.side_effect = Exception("Unexpected error")
        
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'multipart/form-data'
                mock_request.files.get.return_value = valid_csv_file
                mock_request.form.get.return_value = 'user123'
                
                response, status_code = controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert 'Error temporal del sistema' in response['error']
    
    def test_post_validation_error_exceeds_limit(self, controller, mock_product_import_service, app, valid_csv_file):
        """Test: Error de validación por exceder límite de registros"""
        mock_product_import_service.import_products_file.side_effect = ValidationError(
            "Solo se permiten cargar 100 productos"
        )
        
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'multipart/form-data'
                mock_request.files.get.return_value = valid_csv_file
                mock_request.form.get.return_value = 'user123'
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
    
    def test_post_empty_user_id(self, controller, app, valid_csv_file):
        """Test: Error por userId vacío"""
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_files = MagicMock()
                mock_files.get = MagicMock(return_value=valid_csv_file)
                mock_form = MagicMock()
                mock_form.get = MagicMock(return_value='')
                
                mock_request.content_type = 'multipart/form-data'
                mock_request.files = mock_files
                mock_request.form = mock_form
                
                response, status_code = controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert "El campo 'userId' es obligatorio" in response['error']
    
    def test_post_with_excel_file(self, controller, mock_product_import_service, app):
        """Test: Importar productos con archivo Excel"""
        excel_content = b"PK\x03\x04..."
        excel_file = FileStorage(
            stream=BytesIO(excel_content),
            filename='products.xlsx',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        mock_product_import_service.import_products_file.return_value = ('history-456', 'Archivo cargado exitosamente')
        
        with app.test_request_context(method='POST', content_type='multipart/form-data'):
            with patch('app.controllers.product_import_controller.request') as mock_request:
                mock_request.content_type = 'multipart/form-data'
                mock_request.files.get.return_value = excel_file
                mock_request.form.get.return_value = 'user123'
                
                response, status_code = controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['data']['history_id'] == 'history-456'

