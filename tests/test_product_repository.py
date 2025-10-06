import pytest
from unittest.mock import patch, MagicMock, call
from app.repositories.product_repository import ProductRepository, ProductDB
from app.models.product import Product
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid


class TestProductRepository:
    """Pruebas unitarias para ProductRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Fixture para mock de sesión SQLAlchemy"""
        return MagicMock()
    
    @pytest.fixture
    def product_repository(self, mock_session):
        """Fixture para ProductRepository con sesión mockeada"""
        with patch('app.repositories.product_repository.create_engine'):
            with patch('app.repositories.product_repository.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value = mock_session
                with patch('app.repositories.product_repository.Base.metadata.create_all'):
                    repo = ProductRepository()
                    # Reemplazar el método _get_session para usar nuestro mock
                    repo._get_session = lambda: mock_session
                    return repo
    
    @pytest.fixture
    def product_data(self):
        """Datos de producto para testing"""
        return {
            'sku': 'MED-1234',
            'name': 'Producto Test',
            'expiration_date': '2025-12-31T00:00:00.000Z',
            'quantity': 100,
            'price': 15000.0,
            'location': 'A-01-01',
            'description': 'Producto de prueba',
            'product_type': 'Alto valor',
            'photo_filename': 'test.jpg'
        }
    
    @pytest.fixture
    def valid_product(self, product_data):
        """Producto válido para testing"""
        return Product(**product_data)
    
    def test_create_product_success(self, product_repository, valid_product, mock_session):
        """Test: Crear producto exitosamente"""
        # Mock del objeto de base de datos
        mock_db_product = MagicMock()
        mock_db_product.id = 1
        
        # Mock de la sesión
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        
        # Mock del método _model_to_db
        with patch.object(product_repository, '_model_to_db', return_value=mock_db_product) as mock_model_to_db:
            result = product_repository.create(valid_product)
        
        # Verificar que se llamaron los métodos correctos
        mock_model_to_db.assert_called_once_with(valid_product)
        mock_session.add.assert_called_once_with(mock_db_product)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        
        # Verificar que se asignó el ID
        assert result.id == 1
        assert result == valid_product
    
    def test_create_product_validation_error(self, product_repository, valid_product, mock_session):
        """Test: Error de validación al crear producto"""
        # Mock de validación que falla
        valid_product.validate = MagicMock(side_effect=ValueError("Error de validación"))
        
        with pytest.raises(ValueError, match="Error de validación"):
            product_repository.create(valid_product)
        
        mock_session.close.assert_called_once()
    
    def test_create_product_database_error(self, product_repository, valid_product, mock_session):
        """Test: Error de base de datos al crear producto"""
        # Mock de error de base de datos
        mock_session.add.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al crear producto: Database connection error"):
            product_repository.create(valid_product)
        
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_get_by_id_success(self, product_repository, mock_session):
        """Test: Obtener producto por ID exitosamente"""
        # Mock del query
        mock_query = MagicMock()
        mock_db_product = MagicMock()
        mock_db_product.id = 1
        mock_db_product.sku = 'MED-1234'
        mock_db_product.name = 'Producto Test'
        mock_db_product.expiration_date = datetime.now()
        mock_db_product.quantity = 100
        mock_db_product.price = 15000.0
        mock_db_product.location = 'A-01-01'
        mock_db_product.description = 'Producto de prueba'
        mock_db_product.product_type = 'Alto valor'
        mock_db_product.photo_filename = 'test.jpg'
        
        mock_query.filter.return_value.first.return_value = mock_db_product
        mock_session.query.return_value = mock_query
        
        # Mock del método _db_to_model
        expected_product = MagicMock()
        with patch.object(product_repository, '_db_to_model', return_value=expected_product) as mock_db_to_model:
            result = product_repository.get_by_id(1)
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.filter.assert_called_once()
        mock_db_to_model.assert_called_once_with(mock_db_product)
        mock_session.close.assert_called_once()
        
        assert result == expected_product
    
    def test_get_by_id_not_found(self, product_repository, mock_session):
        """Test: Producto no encontrado por ID"""
        # Mock del query que retorna None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = product_repository.get_by_id(999)
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.filter.assert_called_once()
        mock_session.close.assert_called_once()
        
        assert result is None
    
    def test_get_by_id_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al obtener por ID"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al obtener producto por ID: Database connection error"):
            product_repository.get_by_id(1)
        
        mock_session.close.assert_called_once()
    
    def test_get_by_sku_success(self, product_repository, mock_session):
        """Test: Obtener producto por SKU exitosamente"""
        # Mock del query
        mock_query = MagicMock()
        mock_db_product = MagicMock()
        mock_db_product.sku = 'MED-1234'
        
        mock_query.filter.return_value.first.return_value = mock_db_product
        mock_session.query.return_value = mock_query
        
        # Mock del método _db_to_model
        expected_product = MagicMock()
        with patch.object(product_repository, '_db_to_model', return_value=expected_product) as mock_db_to_model:
            result = product_repository.get_by_sku('MED-1234')
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.filter.assert_called_once()
        mock_db_to_model.assert_called_once_with(mock_db_product)
        mock_session.close.assert_called_once()
        
        assert result == expected_product
    
    def test_get_by_sku_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al obtener por SKU"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al obtener producto por SKU: Database connection error"):
            product_repository.get_by_sku('MED-1234')
        
        mock_session.close.assert_called_once()
    
    def test_get_all_success(self, product_repository, mock_session):
        """Test: Obtener todos los productos exitosamente"""
        # Mock de productos de base de datos
        mock_db_products = [
            MagicMock(id=1, sku='MED-1234'),
            MagicMock(id=2, sku='MED-5678')
        ]
        
        mock_session.query.return_value.all.return_value = mock_db_products
        
        # Mock del método _db_to_model
        expected_products = [MagicMock(), MagicMock()]
        with patch.object(product_repository, '_db_to_model', side_effect=expected_products) as mock_db_to_model:
            result = product_repository.get_all()
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_session.query.return_value.all.assert_called_once()
        assert mock_db_to_model.call_count == 2
        mock_session.close.assert_called_once()
        
        assert result == expected_products
    
    def test_get_all_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al obtener todos los productos"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al obtener todos los productos: Database connection error"):
            product_repository.get_all()
        
        mock_session.close.assert_called_once()
    
    def test_delete_product_success(self, product_repository, mock_session):
        """Test: Eliminar producto exitosamente"""
        # Mock del query
        mock_query = MagicMock()
        mock_db_product = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_db_product
        mock_session.query.return_value = mock_query
        
        result = product_repository.delete(1)
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.filter.assert_called_once()
        mock_session.delete.assert_called_once_with(mock_db_product)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        
        assert result is True
    
    def test_delete_product_not_found(self, product_repository, mock_session):
        """Test: Producto no encontrado para eliminar"""
        # Mock del query que retorna None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = product_repository.delete(999)
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.filter.assert_called_once()
        mock_session.close.assert_called_once()
        
        assert result is False
    
    def test_delete_product_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al eliminar producto"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al eliminar producto: Database connection error"):
            product_repository.delete(1)
        
        mock_session.close.assert_called_once()
    
    def test_delete_all_success(self, product_repository, mock_session):
        """Test: Eliminar todos los productos exitosamente"""
        # Mock del query
        mock_query = MagicMock()
        mock_query.count.return_value = 5
        mock_query.delete.return_value = 5
        mock_session.query.return_value = mock_query
        
        result = product_repository.delete_all()
        
        # Verificar que se llamaron los métodos correctos
        assert mock_session.query.call_count == 2  # Se llama dos veces: count() y delete()
        mock_query.count.assert_called_once()
        mock_query.delete.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        
        assert result == 5
    
    def test_delete_all_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al eliminar todos los productos"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al eliminar todos los productos: Database connection error"):
            product_repository.delete_all()
        
        mock_session.close.assert_called_once()
    
    def test_count_success(self, product_repository, mock_session):
        """Test: Contar productos exitosamente"""
        # Mock del query
        mock_query = MagicMock()
        mock_query.count.return_value = 10
        mock_session.query.return_value = mock_query
        
        result = product_repository.count()
        
        # Verificar que se llamaron los métodos correctos
        mock_session.query.assert_called_once_with(ProductDB)
        mock_query.count.assert_called_once()
        mock_session.close.assert_called_once()
        
        assert result == 10
    
    def test_count_database_error(self, product_repository, mock_session):
        """Test: Error de base de datos al contar productos"""
        # Mock de error de base de datos
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        
        with pytest.raises(Exception, match="Error al contar productos: Database connection error"):
            product_repository.count()
        
        mock_session.close.assert_called_once()