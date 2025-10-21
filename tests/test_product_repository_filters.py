"""
Tests para ProductRepository con filtros
"""
import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.product_repository import ProductRepository
from app.models.product import Product


class TestProductRepositoryFilters(unittest.TestCase):
    """Tests para ProductRepository con funcionalidad de filtros"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.repository = ProductRepository()
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_sku_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por SKU exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(sku='MED-1234')

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_name_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por nombre exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(name='Paracetamol')

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_expiration_date_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por fecha de vencimiento exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(expiration_date='2024-12-31')

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_quantity_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por cantidad exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(quantity=100)

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_price_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por precio exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(price=25.50)

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_location_filter_success(self, mock_get_session):
        """Test: Obtener productos con filtro por ubicación exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(location='Estante A')

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_multiple_filters_success(self, mock_get_session):
        """Test: Obtener productos con múltiples filtros exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(
            sku='MED-1234',
            name='Paracetamol',
            quantity=100,
            price=25.50,
            location='Estante A'
        )

        mock_session.query.assert_called_once()
        self.assertEqual(mock_query.filter.call_count, 5)
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_with_pagination_and_filters_success(self, mock_get_session):
        """Test: Obtener productos con paginación y filtros exitosamente"""
        # Configurar mock de sesión
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_session.return_value = mock_session

        result = self.repository.get_all(
            limit=5,
            offset=10,
            sku='MED-1234'
        )

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.limit.assert_called_once_with(5)
        mock_query.offset.assert_called_once_with(10)
        mock_session.close.assert_called_once()
        self.assertEqual(result, [])
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_get_all_database_error(self, mock_get_session):
        """Test: Error de base de datos al obtener productos con filtros"""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        mock_get_session.return_value = mock_session
        
        # Ejecutar método y verificar excepción
        with self.assertRaises(Exception) as context:
            self.repository.get_all(sku='MED-1234')
        
        self.assertIn("Error al obtener productos: Database connection error", str(context.exception))
        mock_session.close.assert_called_once()
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_count_with_sku_filter_success(self, mock_get_session):
        """Test: Contar productos con filtro por SKU exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 5
        mock_get_session.return_value = mock_session

        result = self.repository.count(sku='MED-1234')

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_query.count.assert_called_once()
        mock_session.close.assert_called_once()
        self.assertEqual(result, 5)
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_count_with_multiple_filters_success(self, mock_get_session):
        """Test: Contar productos con múltiples filtros exitosamente"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 3
        mock_get_session.return_value = mock_session

        result = self.repository.count(
            sku='MED-1234',
            name='Paracetamol',
            quantity=100
        )

        mock_session.query.assert_called_once()
        self.assertEqual(mock_query.filter.call_count, 3)
        mock_query.count.assert_called_once()
        mock_session.close.assert_called_once()
        self.assertEqual(result, 3)
    
    @patch('app.repositories.product_repository.ProductRepository._get_session')
    def test_count_database_error(self, mock_get_session):
        """Test: Error de base de datos al contar productos con filtros"""
        mock_session = MagicMock()
        mock_session.query.side_effect = SQLAlchemyError("Database connection error")
        mock_get_session.return_value = mock_session

        with self.assertRaises(Exception) as context:
            self.repository.count(sku='MED-1234')
        
        self.assertIn("Error al contar productos: Database connection error", str(context.exception))
        mock_session.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()