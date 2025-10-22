"""
Tests para métodos de actualización de stock en ProductService
"""
import pytest
from unittest.mock import MagicMock, patch
from app.services.product_service import ProductService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductServiceStock:
    """Tests para métodos de actualización de stock en ProductService"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.mock_repository = MagicMock()
        self.service = ProductService(product_repository=self.mock_repository)
    
    def test_update_stock_success_add(self):
        """Test: Actualizar stock con operación add exitosamente"""
        # Configurar mock del repositorio
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 60,
            "operation": "add",
            "quantity_changed": 10
        }
        self.mock_repository.update_stock.return_value = expected_result
        
        # Ejecutar método
        result = self.service.update_stock(1, "add", 10)
        
        # Verificar resultado
        assert result == expected_result
        self.mock_repository.update_stock.assert_called_once_with(1, "add", 10)
    
    def test_update_stock_success_subtract(self):
        """Test: Actualizar stock con operación subtract exitosamente"""
        # Configurar mock del repositorio
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 40,
            "operation": "subtract",
            "quantity_changed": 10
        }
        self.mock_repository.update_stock.return_value = expected_result
        
        # Ejecutar método
        result = self.service.update_stock(1, "subtract", 10)
        
        # Verificar resultado
        assert result == expected_result
        self.mock_repository.update_stock.assert_called_once_with(1, "subtract", 10)
    
    def test_update_stock_invalid_product_id_none(self):
        """Test: Error cuando product_id es None"""
        with pytest.raises(ValidationError, match="El ID del producto debe ser válido"):
            self.service.update_stock(None, "add", 10)
    
    def test_update_stock_invalid_product_id_zero(self):
        """Test: Error cuando product_id es 0"""
        with pytest.raises(ValidationError, match="El ID del producto debe ser válido"):
            self.service.update_stock(0, "add", 10)
    
    def test_update_stock_invalid_product_id_negative(self):
        """Test: Error cuando product_id es negativo"""
        with pytest.raises(ValidationError, match="El ID del producto debe ser válido"):
            self.service.update_stock(-1, "add", 10)
    
    def test_update_stock_missing_operation(self):
        """Test: Error cuando operation es None"""
        with pytest.raises(ValidationError, match="La operación debe ser 'add' o 'subtract'"):
            self.service.update_stock(1, None, 10)
    
    def test_update_stock_empty_operation(self):
        """Test: Error cuando operation está vacío"""
        with pytest.raises(ValidationError, match="La operación debe ser 'add' o 'subtract'"):
            self.service.update_stock(1, "", 10)
    
    def test_update_stock_invalid_operation(self):
        """Test: Error cuando operation no es válida"""
        with pytest.raises(ValidationError, match="La operación debe ser 'add' o 'subtract'"):
            self.service.update_stock(1, "multiply", 10)
    
    def test_update_stock_missing_quantity(self):
        """Test: Error cuando quantity es None"""
        with pytest.raises(ValidationError, match="La cantidad debe ser mayor a 0"):
            self.service.update_stock(1, "add", None)
    
    def test_update_stock_zero_quantity(self):
        """Test: Error cuando quantity es 0"""
        with pytest.raises(ValidationError, match="La cantidad debe ser mayor a 0"):
            self.service.update_stock(1, "add", 0)
    
    def test_update_stock_negative_quantity(self):
        """Test: Error cuando quantity es negativo"""
        with pytest.raises(ValidationError, match="La cantidad debe ser mayor a 0"):
            self.service.update_stock(1, "add", -5)
    
    def test_update_stock_repository_value_error(self):
        """Test: Error de ValueError del repositorio se convierte a BusinessLogicError"""
        self.mock_repository.update_stock.side_effect = ValueError("Producto no encontrado")
        
        with pytest.raises(BusinessLogicError, match="Producto no encontrado"):
            self.service.update_stock(1, "add", 10)
    
    def test_update_stock_repository_generic_exception(self):
        """Test: Error genérico del repositorio se convierte a BusinessLogicError"""
        self.mock_repository.update_stock.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al actualizar stock del producto: Database error"):
            self.service.update_stock(1, "add", 10)
    
    def test_update_stock_repository_sqlalchemy_error(self):
        """Test: Error de SQLAlchemy del repositorio se convierte a BusinessLogicError"""
        from sqlalchemy.exc import SQLAlchemyError
        self.mock_repository.update_stock.side_effect = SQLAlchemyError("Connection error")
        
        with pytest.raises(BusinessLogicError, match="Error al actualizar stock del producto: Connection error"):
            self.service.update_stock(1, "add", 10)
    
    def test_update_stock_validation_error_preserved(self):
        """Test: ValidationError del servicio se preserva"""
        # Simular que el servicio ya lanzó una ValidationError
        with pytest.raises(ValidationError, match="El ID del producto debe ser válido"):
            self.service.update_stock(None, "add", 10)
    
    def test_update_stock_business_logic_error_preserved(self):
        """Test: BusinessLogicError del servicio se preserva"""
        # Simular que el servicio ya lanzó una BusinessLogicError
        self.mock_repository.update_stock.side_effect = ValueError("Stock insuficiente")
        
        with pytest.raises(BusinessLogicError, match="Stock insuficiente"):
            self.service.update_stock(1, "subtract", 100)
    
    def test_update_stock_large_quantity(self):
        """Test: Actualizar stock con cantidad grande"""
        expected_result = {
            "product_id": 1,
            "previous_quantity": 1000,
            "new_quantity": 2000,
            "operation": "add",
            "quantity_changed": 1000
        }
        self.mock_repository.update_stock.return_value = expected_result
        
        result = self.service.update_stock(1, "add", 1000)
        
        assert result == expected_result
        self.mock_repository.update_stock.assert_called_once_with(1, "add", 1000)
    
    def test_update_stock_float_quantity(self):
        """Test: Actualizar stock con cantidad flotante (se convierte a int en el controlador)"""
        expected_result = {
            "product_id": 1,
            "previous_quantity": 50,
            "new_quantity": 60,
            "operation": "add",
            "quantity_changed": 10
        }
        self.mock_repository.update_stock.return_value = expected_result
        
        # El servicio debería manejar tanto int como float
        result = self.service.update_stock(1, "add", 10.0)
        
        assert result == expected_result
        self.mock_repository.update_stock.assert_called_once_with(1, "add", 10.0)
