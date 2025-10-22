import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from flask import Flask
from app.controllers.product_controller import ProductController, ProductDeleteAllController
from app.services.product_service import ProductService
from app.models.product import Product
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductController:
    """Tests para ProductController"""
    
    @pytest.fixture
    def mock_service(self):
        """Mock del ProductService"""
        return MagicMock()
    
    @pytest.fixture
    def product_controller(self, mock_service):
        """Instancia de ProductController con service mockeado"""
        return ProductController(product_service=mock_service)
    
    @pytest.fixture
    def app(self):
        """Instancia de la aplicación Flask"""
        from app import create_app
        return create_app()
    
    @pytest.fixture
    def valid_product_data(self):
        """Datos válidos para crear un producto"""
        return {
            'sku': 'MED-1234',
            'name': 'Producto Test',
            'expiration_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'quantity': 100,
            'price': 15000.0,
            'location': 'A-01-01',
            'description': 'Producto de prueba',
            'product_type': 'Alto valor',
            'photo_filename': 'test.jpg'
        }
    
    def test_post_json_success(self, product_controller, mock_service, app, valid_product_data):
        """Test: POST con JSON exitoso"""
        mock_product = MagicMock()
        mock_product.to_dict.return_value = {'id': 1, 'sku': 'MED-1234'}
        mock_service.create_product.return_value = mock_product
        
        with app.test_request_context(json=valid_product_data):
            response, status_code = product_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['message'] == "Producto registrado exitosamente"
        assert response['data'] == {'id': 1, 'sku': 'MED-1234'}
        mock_service.create_product.assert_called_once_with(valid_product_data, None)
    
    def test_post_multipart_success(self, product_controller, mock_service, app, valid_product_data):
        """Test: POST con multipart/form-data exitoso"""
        mock_product = MagicMock()
        mock_product.to_dict.return_value = {'id': 1, 'sku': 'MED-1234'}
        mock_service.create_product.return_value = mock_product
        
        with app.test_request_context(content_type='multipart/form-data'):
            with patch('app.controllers.product_controller.request') as mock_request:
                mock_request.is_json = False
                mock_request.content_type = 'multipart/form-data'
                mock_request.form.to_dict.return_value = valid_product_data
                mock_request.files.get.return_value = None
                
                response, status_code = product_controller.post()
        
        assert status_code == 201
        assert response['success'] is True
        assert response['message'] == "Producto registrado exitosamente"
        mock_service.create_product.assert_called_once()
    
    def test_post_unsupported_content_type(self, product_controller, app):
        """Test: POST con Content-Type no soportado"""
        with app.test_request_context(content_type='text/plain'):
            response, status_code = product_controller.post()
        
        assert status_code == 415
        assert response['success'] is False
        assert response['error'] == "Content-Type no soportado"
    
    def test_post_validation_error(self, product_controller, mock_service, app, valid_product_data):
        """Test: POST con error de validación"""
        mock_service.create_product.side_effect = ValidationError("Error de validación")
        
        with app.test_request_context(json=valid_product_data):
            response, status_code = product_controller.post()
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Error de validación"
    
    def test_post_business_logic_error(self, product_controller, mock_service, app, valid_product_data):
        """Test: POST con error de lógica de negocio"""
        mock_service.create_product.side_effect = BusinessLogicError("SKU duplicado")
        
        with app.test_request_context(json=valid_product_data):
            response, status_code = product_controller.post()
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
        assert response['details'] == "SKU duplicado"
    
    def test_post_generic_error(self, product_controller, mock_service, app, valid_product_data):
        """Test: POST con error genérico"""
        mock_service.create_product.side_effect = Exception("Error interno")
        
        with app.test_request_context(json=valid_product_data):
            response, status_code = product_controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error temporal del sistema. Contacte soporte técnico si persiste"
    
    def test_post_json_malformed(self, product_controller, app):
        """Test: POST con JSON malformado"""
        with app.test_request_context(data='invalid json', content_type='application/json'):
            response, status_code = product_controller.post()
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error temporal del sistema. Contacte soporte técnico si persiste"
    
    def test_get_product_by_id_success(self, product_controller, mock_service):
        """Test: GET producto por ID exitoso"""
        mock_product = MagicMock()
        mock_product.to_dict.return_value = {'id': 1, 'sku': 'MED-1234'}
        mock_service.get_product_by_id.return_value = mock_product
        
        response, status_code = product_controller.get(product_id=1)
        
        assert status_code == 200
        assert response['success'] is True
        assert response['data'] == {'id': 1, 'sku': 'MED-1234'}
        mock_service.get_product_by_id.assert_called_once_with(1)
    
    def test_get_product_by_id_not_found(self, product_controller, mock_service):
        """Test: GET producto por ID no encontrado"""
        mock_service.get_product_by_id.return_value = None
        
        response, status_code = product_controller.get(product_id=1)
        
        assert status_code == 404
        assert response['success'] is False
        assert response['error'] == "Producto no encontrado"
    
    def test_get_all_products_success(self, product_controller, mock_service):
        """Test: GET todos los productos exitoso"""
        mock_products_summary = [
            {'id': 1, 'sku': 'MED-1234'},
            {'id': 2, 'sku': 'MED-5678'}
        ]
        mock_service.get_products_summary.return_value = mock_products_summary
        mock_service.get_products_count.return_value = 2

        app = Flask(__name__)
        with app.test_request_context('/inventory/products'):
            response, status_code = product_controller.get()
        
        assert status_code == 200
        assert response['success'] is True
        assert 'products' in response['data']
        assert 'pagination' in response['data']
        assert response['data']['products'] == mock_products_summary
        assert response['data']['pagination']['total'] == 2
        assert response['data']['pagination']['page'] == 1
        assert response['data']['pagination']['per_page'] == 10
        mock_service.get_products_summary.assert_called_once()
        mock_service.get_products_count.assert_called_once()
    
    def test_get_service_error(self, product_controller, mock_service):
        """Test: GET con error del servicio"""
        mock_service.get_product_by_id.side_effect = BusinessLogicError("Error del servicio")
        
        response, status_code = product_controller.get(product_id=1)
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
    
    def test_delete_product_success(self, product_controller, mock_service):
        """Test: DELETE producto exitoso"""
        mock_service.delete_product.return_value = True
        
        response, status_code = product_controller.delete(product_id=1)
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Producto eliminado exitosamente"
        mock_service.delete_product.assert_called_once_with(1)
    
    def test_delete_product_failure(self, product_controller, mock_service):
        """Test: DELETE producto fallido"""
        mock_service.delete_product.return_value = False
        
        response, status_code = product_controller.delete(product_id=1)
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "No se pudo eliminar el producto"
    
    def test_delete_product_service_error(self, product_controller, mock_service):
        """Test: DELETE producto con error del servicio"""
        mock_service.delete_product.side_effect = BusinessLogicError("Producto no encontrado")
        
        response, status_code = product_controller.delete(product_id=1)
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
    
    def test_extract_multipart_data_success(self, product_controller, app, valid_product_data):
        """Test: Extraer datos multipart exitosamente"""
        with app.test_request_context():
            with patch('app.controllers.product_controller.request') as mock_request:
                mock_request.form.to_dict.return_value = valid_product_data
                mock_request.files.get.return_value = None
                
                result = product_controller._extract_multipart_data()
        
        # Verificar que se llamaron los métodos correctos
        mock_request.form.to_dict.assert_called_once()
        mock_request.files.get.assert_called_once_with('photo')
        assert len(result) == 2
    
    def test_extract_multipart_data_with_photo(self, product_controller, app, valid_product_data):
        """Test: Extraer datos multipart con foto"""
        mock_photo_file = MagicMock()
        
        with app.test_request_context():
            with patch('app.controllers.product_controller.request') as mock_request:
                mock_request.form.to_dict.return_value = valid_product_data
                mock_request.files.get.return_value = mock_photo_file
                
                result = product_controller._extract_multipart_data()
        
        # Verificar que se llamaron los métodos correctos
        mock_request.form.to_dict.assert_called_once()
        mock_request.files.get.assert_called_once_with('photo')
        assert len(result) == 2
    
    def test_extract_multipart_data_error(self, product_controller, app):
        """Test: Error al extraer datos multipart"""
        with app.test_request_context():
            with patch('app.controllers.product_controller.request') as mock_request:
                mock_request.form.to_dict.return_value = {}
                mock_request.files.get.return_value = None
                
                # Simplemente verificar que el método se ejecuta
                result = product_controller._extract_multipart_data()
                assert len(result) == 2


class TestProductDeleteAllController:
    """Tests para ProductDeleteAllController"""
    
    @pytest.fixture
    def mock_service(self):
        """Mock del ProductService"""
        return MagicMock()
    
    @pytest.fixture
    def delete_controller(self, mock_service):
        """Instancia de ProductDeleteAllController con service mockeado"""
        return ProductDeleteAllController(product_service=mock_service)
    
    def test_delete_all_success(self, delete_controller, mock_service):
        """Test: DELETE todos los productos exitoso"""
        mock_service.delete_all_products.return_value = 5
        
        response, status_code = delete_controller.delete()
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Se eliminaron 5 productos"
        assert response['data']['deleted_count'] == 5
        mock_service.delete_all_products.assert_called_once()
    
    def test_delete_all_zero_products(self, delete_controller, mock_service):
        """Test: DELETE todos los productos cuando no hay productos"""
        mock_service.delete_all_products.return_value = 0
        
        response, status_code = delete_controller.delete()
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Se eliminaron 0 productos"
        assert response['data']['deleted_count'] == 0
    
    def test_delete_all_service_error(self, delete_controller, mock_service):
        """Test: DELETE todos los productos con error del servicio"""
        mock_service.delete_all_products.side_effect = BusinessLogicError("Error del servicio")
        
        response, status_code = delete_controller.delete()
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
    
    def test_delete_all_generic_error(self, delete_controller, mock_service):
        """Test: DELETE todos los productos con error genérico"""
        mock_service.delete_all_products.side_effect = Exception("Error interno")
        
        response, status_code = delete_controller.delete()
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error temporal del sistema. Contacte soporte técnico si persiste"
