"""
Tests para ProductStockController
"""
import pytest
from unittest.mock import MagicMock, patch
from app import create_app
from app.controllers.product_stock_controller import ProductStockController
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductStockController:
    """Tests para ProductStockController"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.controller = ProductStockController()
        self.mock_service = MagicMock()
        self.controller.product_service = self.mock_service
    
    def test_put_success_add_operation(self):
        """Test: Actualizar stock con operación add exitosamente"""
        # Configurar mock
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 60,
            "operation": "add",
            "quantity_changed": 10
        }
        self.mock_service.update_stock.return_value = expected_result
        
        # Simular request
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": 10,
                                             "reason": "restock"
                                         }):
            response, status_code = self.controller.put(1)
            
            # Verificar respuesta
            assert status_code == 200
            assert response['success'] is True
            assert response['data'] == expected_result
            assert "Stock actualizado exitosamente" in response['message']
            
            # Verificar llamada al servicio
            self.mock_service.update_stock.assert_called_once_with(1, "add", 10)
    
    def test_put_success_subtract_operation(self):
        """Test: Actualizar stock con operación subtract exitosamente"""
        # Configurar mock
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 40,
            "operation": "subtract",
            "quantity_changed": 10
        }
        self.mock_service.update_stock.return_value = expected_result
        
        # Simular request
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "subtract",
                                             "quantity": 10
                                         }):
            response, status_code = self.controller.put(1)
            
            # Verificar respuesta
            assert status_code == 200
            assert response['success'] is True
            assert response['data'] == expected_result
            
            # Verificar llamada al servicio
            self.mock_service.update_stock.assert_called_once_with(1, "subtract", 10)
    
    def test_put_no_json_data(self):
        """Test: Error cuando no se proporciona JSON"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT'):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "Se requiere un cuerpo JSON" in response['details']
    
    def test_put_missing_operation(self):
        """Test: Error cuando falta el campo operation"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "quantity": 10
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "El campo 'operation' es obligatorio" in response['details']
    
    def test_put_missing_quantity(self):
        """Test: Error cuando falta el campo quantity"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add"
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "El campo 'quantity' es obligatorio" in response['details']
    
    def test_put_invalid_quantity_type(self):
        """Test: Error cuando quantity no es un número"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": "invalid"
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "La cantidad debe ser un número mayor a 0" in response['details']
    
    def test_put_negative_quantity(self):
        """Test: Error cuando quantity es negativo"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": -5
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "La cantidad debe ser un número mayor a 0" in response['details']
    
    def test_put_zero_quantity(self):
        """Test: Error cuando quantity es cero"""
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": 0
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "La cantidad debe ser un número mayor a 0" in response['details']
    
    def test_put_validation_error(self):
        """Test: Error de validación del servicio"""
        self.mock_service.update_stock.side_effect = ValidationError("Producto no encontrado")
        
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": 10
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 400
            assert response['success'] is False
            assert "Error de validación" in response['error']
            assert "Producto no encontrado" in response['details']
    
    def test_put_business_logic_error(self):
        """Test: Error de lógica de negocio del servicio"""
        self.mock_service.update_stock.side_effect = BusinessLogicError("Stock insuficiente")
        
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "subtract",
                                             "quantity": 100
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 422
            assert response['success'] is False
            assert "Error de lógica de negocio" in response['error']
            assert "Stock insuficiente" in response['details']
    
    def test_put_generic_exception(self):
        """Test: Error genérico del servicio"""
        self.mock_service.update_stock.side_effect = Exception("Error de base de datos")
        
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": 10
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 500
            assert response['success'] is False
            assert "Error interno del servidor" in response['error']
            assert "Error de base de datos" in response['details']
    
    def test_put_float_quantity_converted_to_int(self):
        """Test: Cantidad flotante se convierte a entero"""
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 60,
            "operation": "add",
            "quantity_changed": 10
        }
        self.mock_service.update_stock.return_value = expected_result
        
        with self.app.test_request_context('/inventory/products/1/stock', 
                                         method='PUT',
                                         json={
                                             "operation": "add",
                                             "quantity": 10.5  # Flotante
                                         }):
            response, status_code = self.controller.put(1)
            
            assert status_code == 200
            assert response['success'] is True
            
            # Verificar que se convirtió a entero
            self.mock_service.update_stock.assert_called_once_with(1, "add", 10)
