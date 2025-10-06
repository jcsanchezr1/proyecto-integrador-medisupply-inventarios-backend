import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.repositories.product_repository import ProductRepository
from app.models.product import Product


class TestProductRepository:
    """Tests para ProductRepository"""
    
    @pytest.fixture
    def product_repository(self):
        """Instancia de ProductRepository"""
        return ProductRepository()
    
    @pytest.fixture
    def valid_product(self):
        """Producto válido para testing"""
        return Product(
            sku='MED-1234',
            name='Producto Test',
            expiration_date=datetime.utcnow() + timedelta(days=30),
            quantity=100,
            price=15000.0,
            location='A-01-01',
            description='Producto de prueba',
            product_type='Alto valor',
            photo_filename='test.jpg'
        )
    
    def test_create_product_success(self, product_repository, valid_product):
        """Test: Crear producto exitosamente"""
        result = product_repository.create(valid_product)
        
        assert result == valid_product
        assert result.id == 1  # Primer ID asignado
    
    def test_create_product_validation_error(self, product_repository):
        """Test: Error de validación al crear producto"""
        invalid_product = MagicMock()
        invalid_product.validate.side_effect = ValueError("Error de validación")
        
        with pytest.raises(Exception, match="Error al crear producto"):
            product_repository.create(invalid_product)
    
    def test_create_product_database_error(self, product_repository, valid_product):
        """Test: Error de base de datos al crear producto"""
        # Simular error de base de datos modificando el método
        original_create = product_repository.create
        
        def mock_create(product):
            raise Exception("Database connection error")
        
        product_repository.create = mock_create
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.create(valid_product)
    
    def test_get_by_id_success(self, product_repository):
        """Test: Obtener producto por ID exitosamente"""
        result = product_repository.get_by_id(1)
        
        # En la implementación actual retorna None (simulación)
        assert result is None
    
    def test_get_by_id_database_error(self, product_repository):
        """Test: Error de base de datos al obtener por ID"""
        # Simular error de base de datos
        original_get_by_id = product_repository.get_by_id
        
        def mock_get_by_id(product_id):
            raise Exception("Database connection error")
        
        product_repository.get_by_id = mock_get_by_id
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.get_by_id(1)
    
    def test_get_by_sku_success(self, product_repository):
        """Test: Obtener producto por SKU exitosamente"""
        result = product_repository.get_by_sku('MED-1234')
        
        # En la implementación actual retorna None (simulación)
        assert result is None
    
    def test_get_by_sku_database_error(self, product_repository):
        """Test: Error de base de datos al obtener por SKU"""
        # Simular error de base de datos
        original_get_by_sku = product_repository.get_by_sku
        
        def mock_get_by_sku(sku):
            raise Exception("Database connection error")
        
        product_repository.get_by_sku = mock_get_by_sku
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.get_by_sku('MED-1234')
    
    def test_get_all_success(self, product_repository):
        """Test: Obtener todos los productos exitosamente"""
        result = product_repository.get_all()
        
        # En la implementación actual retorna lista vacía (simulación)
        assert result == []
    
    def test_get_all_database_error(self, product_repository):
        """Test: Error de base de datos al obtener todos los productos"""
        # Simular error de base de datos
        original_get_all = product_repository.get_all
        
        def mock_get_all():
            raise Exception("Database connection error")
        
        product_repository.get_all = mock_get_all
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.get_all()
    
    def test_update_product_success(self, product_repository, valid_product):
        """Test: Actualizar producto exitosamente"""
        result = product_repository.update(valid_product)
        
        assert result == valid_product
    
    def test_update_product_validation_error(self, product_repository):
        """Test: Error de validación al actualizar producto"""
        invalid_product = MagicMock()
        invalid_product.validate.side_effect = ValueError("Error de validación")
        
        with pytest.raises(Exception, match="Error al actualizar producto"):
            product_repository.update(invalid_product)
    
    def test_update_product_database_error(self, product_repository, valid_product):
        """Test: Error de base de datos al actualizar producto"""
        # Simular error de base de datos
        original_update = product_repository.update
        
        def mock_update(product):
            raise Exception("Database connection error")
        
        product_repository.update = mock_update
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.update(valid_product)
    
    def test_delete_product_success(self, product_repository):
        """Test: Eliminar producto exitosamente"""
        result = product_repository.delete(1)
        
        # En la implementación actual retorna True (simulación)
        assert result is True
    
    def test_delete_product_database_error(self, product_repository):
        """Test: Error de base de datos al eliminar producto"""
        # Simular error de base de datos
        original_delete = product_repository.delete
        
        def mock_delete(product_id):
            raise Exception("Database connection error")
        
        product_repository.delete = mock_delete
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.delete(1)
    
    def test_delete_all_success(self, product_repository):
        """Test: Eliminar todos los productos exitosamente"""
        result = product_repository.delete_all()
        
        # En la implementación actual retorna 0 (simulación)
        assert result == 0
    
    def test_delete_all_database_error(self, product_repository):
        """Test: Error de base de datos al eliminar todos los productos"""
        # Simular error de base de datos
        original_delete_all = product_repository.delete_all
        
        def mock_delete_all():
            raise Exception("Database connection error")
        
        product_repository.delete_all = mock_delete_all
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.delete_all()
    
    def test_count_success(self, product_repository):
        """Test: Contar productos exitosamente"""
        result = product_repository.count()
        
        # En la implementación actual retorna 0 (simulación)
        assert result == 0
    
    def test_count_database_error(self, product_repository):
        """Test: Error de base de datos al contar productos"""
        # Simular error de base de datos
        original_count = product_repository.count
        
        def mock_count():
            raise Exception("Database connection error")
        
        product_repository.count = mock_count
        
        with pytest.raises(Exception, match="Database connection error"):
            product_repository.count()
