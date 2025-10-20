"""
Pruebas extendidas para el repositorio de productos
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.product_repository import ProductRepository
from app.models.product import Product


class TestProductRepositoryExtended:
    """Pruebas extendidas para el repositorio de productos"""

    @pytest.fixture
    def product_repository(self):
        """Repositorio de productos para pruebas"""
        with patch('app.repositories.product_repository.create_engine'):
            return ProductRepository()

    @pytest.fixture
    def mock_session(self):
        """Sesión mock"""
        return MagicMock()

    def test_get_session(self, product_repository):
        """Prueba _get_session()"""
        with patch.object(product_repository, 'Session') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            result = product_repository._get_session()
            
            assert result == mock_session
            mock_session_class.assert_called_once()

    def test_db_to_model_with_none_expiration_date(self, product_repository):
        """Prueba _db_to_model() con expiration_date None"""
        # Crear ProductDB mock con expiration_date None
        db_product = MagicMock()
        db_product.id = 1
        db_product.sku = "MED-1234"
        db_product.name = "Test Product"
        db_product.expiration_date = None
        db_product.quantity = 100
        db_product.price = 50000.0
        db_product.location = "A-01-01"
        db_product.description = "Test description"
        db_product.product_type = "Alto valor"
        db_product.provider_id = '550e8400-e29b-41d4-a716-446655440000'
        db_product.photo_filename = "test.jpg"
        db_product.created_at = datetime.utcnow()
        db_product.updated_at = datetime.utcnow()
        
        result = product_repository._db_to_model(db_product)
        
        assert result.id == 1
        assert result.sku == "MED-1234"
        assert result.name == "Test Product"
        assert result.expiration_date is None  # Verificar que maneja None correctamente

    def test_get_by_sku_not_found(self, product_repository, mock_session):
        """Prueba get_by_sku() cuando no encuentra el producto"""
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            # Configurar mock para que no encuentre el producto
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            result = product_repository.get_by_sku("NON-EXISTENT")
            
            assert result is None
            mock_session.close.assert_called_once()

    def test_update_success(self, product_repository, mock_session):
        """Prueba update() exitoso"""
        # Crear producto para actualizar
        product = Product(
            id=1,
            sku="MED-1234",
            name="Updated Product",
            expiration_date=datetime(2025, 12, 31),
            quantity=200,
            price=20000.0,
            location="B-02-02",
            description="Updated description",
            product_type="Seguridad",
            provider_id="550e8400-e29b-41d4-a716-446655440000",
            photo_filename="updated.jpg"
        )
        
        # Crear ProductDB mock existente
        db_product = MagicMock()
        db_product.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = db_product
        
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            result = product_repository.update(product)
            
            assert result == product
            # Verificar que se actualizaron los campos
            assert db_product.sku == "MED-1234"
            assert db_product.name == "Updated Product"
            assert db_product.quantity == 200
            assert db_product.price == 20000.0
            assert db_product.location == "B-02-02"
            assert db_product.description == "Updated description"
            assert db_product.product_type == "Seguridad"
            assert db_product.photo_filename == "updated.jpg"
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_update_with_string_date(self, product_repository, mock_session):
        """Prueba update() con fecha como string"""
        # Crear producto con fecha como string
        product = Product(
            id=1,
            sku="MED-1234",
            name="Updated Product",
            expiration_date="2025-12-31T00:00:00Z",  # String date
            quantity=200,
            price=20000.0,
            location="B-02-02",
            description="Updated description",
            product_type="Seguridad",
            provider_id="550e8400-e29b-41d4-a716-446655440000",
            photo_filename="updated.jpg"
        )
        
        # Crear ProductDB mock existente
        db_product = MagicMock()
        db_product.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = db_product
        
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            result = product_repository.update(product)
            
            assert result == product
            # Verificar que se convirtió la fecha string a datetime
            assert isinstance(db_product.expiration_date, datetime)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_update_with_none_date(self, product_repository, mock_session):
        """Prueba update() con fecha válida"""
        # Crear producto con fecha válida (no puede ser None por validación)
        product = Product(
            id=1,
            sku="MED-1234",
            name="Updated Product",
            expiration_date=datetime(2025, 12, 31),  # Fecha válida
            quantity=200,
            price=20000.0,
            location="B-02-02",
            description="Updated description",
            product_type="Seguridad",
            provider_id="550e8400-e29b-41d4-a716-446655440000",
            photo_filename="updated.jpg"
        )
        
        # Crear ProductDB mock existente
        db_product = MagicMock()
        db_product.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = db_product
        
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            result = product_repository.update(product)
            
            assert result == product
            # Verificar que se actualizó correctamente
            assert db_product.sku == "MED-1234"
            assert db_product.name == "Updated Product"
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_update_database_error(self, product_repository, mock_session):
        """Prueba update() con error de base de datos"""
        # Crear producto para actualizar
        product = Product(
            id=1,
            sku="MED-1234",
            name="Updated Product",
            expiration_date=datetime(2025, 12, 31),
            quantity=200,
            price=20000.0,
            location="B-02-02",
            description="Updated description",
            product_type="Seguridad",
            provider_id="550e8400-e29b-41d4-a716-446655440000",
            photo_filename="updated.jpg"
        )
        
        # Crear ProductDB mock existente
        db_product = MagicMock()
        db_product.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = db_product
        
        # Configurar mock para que lance SQLAlchemyError
        mock_session.commit.side_effect = SQLAlchemyError("Database error")
        
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            with pytest.raises(Exception, match="Error al actualizar producto: Database error"):
                product_repository.update(product)
            
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_update_product_not_found(self, product_repository, mock_session):
        """Prueba update() cuando no encuentra el producto"""
        # Crear producto para actualizar
        product = Product(
            id=999,
            sku="MED-9999",
            name="Producto Inexistente",  # Nombre válido
            expiration_date=datetime(2025, 12, 31),
            quantity=200,
            price=20000.0,
            location="B-02-02",
            description="Updated description",
            product_type="Seguridad",
            provider_id="550e8400-e29b-41d4-a716-446655440000",
            photo_filename="updated.jpg"
        )
        
        # Configurar mock para que no encuentre el producto
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch.object(product_repository, '_get_session', return_value=mock_session):
            result = product_repository.update(product)
            
            # Cuando no encuentra el producto, debería retornar el producto original
            assert result == product
            mock_session.close.assert_called_once()
