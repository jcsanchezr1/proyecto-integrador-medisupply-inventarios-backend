"""
Tests para métodos de actualización de stock en ProductRepository
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.repositories.product_repository import ProductRepository, ProductDB
from sqlalchemy.exc import SQLAlchemyError


class TestProductRepositoryStock:
    """Tests para métodos de actualización de stock en ProductRepository"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.repository = ProductRepository()
        self.mock_session = MagicMock()
        self.repository._get_session = MagicMock(return_value=self.mock_session)
    
    def test_update_stock_success_add(self):
        """Test: Actualizar stock con operación add exitosamente"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        mock_product.updated_at = datetime.utcnow()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        result = self.repository.update_stock(1, "add", 10)
        
        # Verificar resultado
        assert result["product_id"] == 1
        assert result["previous_quantity"] == 50
        assert result["new_quantity"] == 60
        assert result["operation"] == "add"
        assert result["quantity_changed"] == 10
        
        # Verificar que se actualizó la cantidad
        assert mock_product.quantity == 60
        self.mock_session.commit.assert_called_once()
    
    def test_update_stock_success_subtract(self):
        """Test: Actualizar stock con operación subtract exitosamente"""
        # Configurar mock de producto
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        mock_product.updated_at = datetime.utcnow()
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        # Ejecutar método
        result = self.repository.update_stock(1, "subtract", 10)
        
        # Verificar resultado
        assert result["product_id"] == 1
        assert result["previous_quantity"] == 50
        assert result["new_quantity"] == 40
        assert result["operation"] == "subtract"
        assert result["quantity_changed"] == 10
        
        # Verificar que se actualizó la cantidad
        assert mock_product.quantity == 40
        self.mock_session.commit.assert_called_once()
    
    def test_update_stock_product_not_found(self):
        """Test: Error cuando el producto no existe"""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Producto con ID 999 no encontrado"):
            self.repository.update_stock(999, "add", 10)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_invalid_operation(self):
        """Test: Error cuando la operación no es válida"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        with pytest.raises(ValueError, match="La operación debe ser 'add' o 'subtract'"):
            self.repository.update_stock(1, "invalid", 10)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_invalid_quantity_zero(self):
        """Test: Error cuando la cantidad es cero"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            self.repository.update_stock(1, "add", 0)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_invalid_quantity_negative(self):
        """Test: Error cuando la cantidad es negativa"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        with pytest.raises(ValueError, match="La cantidad debe ser mayor a 0"):
            self.repository.update_stock(1, "add", -5)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_insufficient_stock(self):
        """Test: Error cuando no hay stock suficiente para restar"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 5  # Solo 5 disponibles
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        with pytest.raises(ValueError, match="Stock insuficiente. Disponible: 5, Solicitado: 10"):
            self.repository.update_stock(1, "subtract", 10)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_database_error(self):
        """Test: Error de base de datos durante la actualización"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 50
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        self.mock_session.commit.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al actualizar stock del producto: Database connection error"):
            self.repository.update_stock(1, "add", 10)
        
        self.mock_session.rollback.assert_called_once()
    
    def test_update_stock_exact_stock_subtract(self):
        """Test: Restar exactamente todo el stock disponible"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 10  # Exactamente 10 disponibles
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        # Ejecutar método
        result = self.repository.update_stock(1, "subtract", 10)
        
        # Verificar resultado
        assert result["product_id"] == 1
        assert result["previous_quantity"] == 10
        assert result["new_quantity"] == 0
        assert result["operation"] == "subtract"
        assert result["quantity_changed"] == 10
        
        # Verificar que se actualizó la cantidad
        assert mock_product.quantity == 0
        self.mock_session.commit.assert_called_once()
    
    def test_update_stock_large_quantity_add(self):
        """Test: Agregar una cantidad grande de stock"""
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.quantity = 1000
        
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_product
        
        # Ejecutar método
        result = self.repository.update_stock(1, "add", 5000)
        
        # Verificar resultado
        assert result["product_id"] == 1
        assert result["previous_quantity"] == 1000
        assert result["new_quantity"] == 6000
        assert result["operation"] == "add"
        assert result["quantity_changed"] == 5000
        
        # Verificar que se actualizó la cantidad
        assert mock_product.quantity == 6000
        self.mock_session.commit.assert_called_once()
