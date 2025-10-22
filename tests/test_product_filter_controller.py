"""
Tests para ProductFilterController
"""
import unittest
from unittest.mock import MagicMock, patch
from flask import Flask

from app.controllers.product_filter_controller import ProductFilterController
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductFilterController(unittest.TestCase):
    """Tests para ProductFilterController"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Mock del servicio
        self.mock_service = MagicMock()
        self.controller = ProductFilterController(product_service=self.mock_service)
    
    def test_get_with_sku_filter_success(self):
        """Test: Filtrar productos por SKU exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED-1234'):
            # Configurar mocks
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'name': 'Paracetamol'}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(len(response['data']['products']), 1)
            self.assertEqual(response['data']['filters_applied']['sku'], 'MED-1234')
            self.mock_service.get_products_summary.assert_called_once_with(
                limit=10, offset=0, sku='MED-1234', name=None,
                expiration_date=None, quantity=None, price=None, location=None
            )
            self.mock_service.get_products_count.assert_called_once_with(
                sku='MED-1234', name=None, expiration_date=None,
                quantity=None, price=None, location=None
            )
    
    def test_get_with_name_filter_success(self):
        """Test: Filtrar productos por nombre exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?name=Paracetamol'):
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'name': 'Paracetamol'}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['name'], 'Paracetamol')
    
    def test_get_with_expiration_date_filter_success(self):
        """Test: Filtrar productos por fecha de vencimiento exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?expiration_date=2024-12-31'):
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'expiration_date': '2024-12-31'}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['expiration_date'], '2024-12-31')
    
    def test_get_with_quantity_filter_success(self):
        """Test: Filtrar productos por cantidad exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?quantity=100'):
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'quantity': 100}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['quantity'], 100)
    
    def test_get_with_price_filter_success(self):
        """Test: Filtrar productos por precio exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?price=25.50'):
            # Configurar mocks
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'price': 25.50}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['price'], 25.50)
    
    def test_get_with_location_filter_success(self):
        """Test: Filtrar productos por ubicación exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?location=Estante A'):
            # Configurar mocks
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'location': 'Estante A'}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['location'], 'Estante A')
    
    def test_get_with_multiple_filters_success(self):
        """Test: Filtrar productos con múltiples filtros exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED&name=Paracetamol&quantity=100'):
            # Configurar mocks
            mock_products = [{'id': 1, 'sku': 'MED-1234', 'name': 'Paracetamol', 'quantity': 100}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 1
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['filters_applied']['sku'], 'MED')
            self.assertEqual(response['data']['filters_applied']['name'], 'Paracetamol')
            self.assertEqual(response['data']['filters_applied']['quantity'], 100)
    
    def test_get_with_pagination_success(self):
        """Test: Filtrar productos con paginación exitosamente"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED&page=2&per_page=5'):
            # Configurar mocks
            mock_products = [{'id': 1, 'sku': 'MED-1234'}]
            self.mock_service.get_products_summary.return_value = mock_products
            self.mock_service.get_products_count.return_value = 10
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 200)
            self.assertTrue(response['success'])
            self.assertEqual(response['data']['pagination']['page'], 2)
            self.assertEqual(response['data']['pagination']['per_page'], 5)
            self.assertEqual(response['data']['pagination']['total'], 10)
            self.assertEqual(response['data']['pagination']['total_pages'], 2)
            self.assertTrue(response['data']['pagination']['has_prev'])
            self.assertFalse(response['data']['pagination']['has_next'])
    
    def test_get_no_filters_error(self):
        """Test: Error cuando no se proporcionan filtros"""
        with self.app.test_request_context('/inventory/products/filter'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertFalse(response['success'])
            self.assertIn('Debe proporcionar al menos un filtro', response['error'])
    
    def test_get_invalid_page_error(self):
        """Test: Error con página inválida"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED&page=0'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertFalse(response['success'])
            self.assertIn('El parámetro \'page\' debe ser mayor a 0', response['error'])
    
    def test_get_invalid_per_page_error(self):
        """Test: Error con per_page inválido"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED&per_page=150'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertFalse(response['success'])
            self.assertIn('El parámetro \'per_page\' debe estar entre 1 y 100', response['error'])
    
    def test_get_invalid_expiration_date_format_error(self):
        """Test: Error con formato de fecha inválido"""
        with self.app.test_request_context('/inventory/products/filter?expiration_date=31-12-2024'):
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 400)
            self.assertFalse(response['success'])
            self.assertIn('El formato de \'expiration_date\' debe ser YYYY-MM-DD', response['error'])
    
    def test_get_business_logic_error(self):
        """Test: Manejo de BusinessLogicError"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED'):
            self.mock_service.get_products_summary.side_effect = BusinessLogicError("Error de negocio")
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 422)
            self.assertFalse(response['success'])
            self.assertIn('Error de negocio', response['details'])
    
    def test_get_general_exception(self):
        """Test: Manejo de excepción general"""
        with self.app.test_request_context('/inventory/products/filter?sku=MED'):
            self.mock_service.get_products_summary.side_effect = Exception("Error general")
            
            response, status_code = self.controller.get()
            
            self.assertEqual(status_code, 500)
            self.assertFalse(response['success'])
            self.assertIn('Error temporal del sistema', response['error'])


if __name__ == '__main__':
    unittest.main()
