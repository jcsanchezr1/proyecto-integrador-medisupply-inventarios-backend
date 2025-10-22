"""
Tests para ProductProcessedHistoryRepository
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.repositories.product_processed_history_repository import ProductProcessedHistoryRepository
from app.models.product_processed_history import ProductProcessedHistory


class TestProductProcessedHistoryRepository:
    """Tests para ProductProcessedHistoryRepository"""
    
    @pytest.fixture
    def mock_session(self):
        """Mock de la sesión de SQLAlchemy"""
        return MagicMock()
    
    @pytest.fixture
    def repository(self):
        """Instancia de ProductProcessedHistoryRepository"""
        with patch('app.repositories.product_processed_history_repository.create_engine'):
            with patch('app.repositories.product_processed_history_repository.sessionmaker'):
                return ProductProcessedHistoryRepository()
    
    @pytest.fixture
    def valid_history(self):
        """Registro de historial válido"""
        return ProductProcessedHistory(
            file_name='products_abc123.csv',
            user_id='550e8400-e29b-41d4-a716-446655440000',
            status='En curso',
            result=None,
            id='123e4567-e89b-12d3-a456-426614174000'
        )
    
    def test_create_history_success(self, repository, mock_session, valid_history):
        """Test: Crear registro de historial exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        result = repository.create(valid_history)
        
        assert result.id is not None
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_create_history_with_validation_error(self, repository, mock_session):
        """Test: Error al crear registro con datos inválidos"""
        repository._get_session = MagicMock(return_value=mock_session)
        invalid_history = ProductProcessedHistory(
            file_name='',  # Inválido
            user_id='user123',
            status='En curso'
        )
        
        with pytest.raises(Exception):
            repository.create(invalid_history)
        
        mock_session.close.assert_called_once()
    
    def test_create_history_generates_uuid(self, repository, mock_session, valid_history):
        """Test: Crear registro genera UUID si no existe"""
        repository._get_session = MagicMock(return_value=mock_session)
        valid_history.id = None
        
        result = repository.create(valid_history)
        
        assert result.id is not None
        assert len(result.id) == 36  # UUID tiene 36 caracteres
    
    def test_get_by_id_success(self, repository, mock_session, valid_history):
        """Test: Obtener registro por ID exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        mock_db_history = MagicMock()
        mock_db_history.id = valid_history.id
        mock_db_history.file_name = valid_history.file_name
        mock_db_history.user_id = valid_history.user_id
        mock_db_history.status = valid_history.status
        mock_db_history.result = valid_history.result
        mock_db_history.created_at = datetime.utcnow()
        mock_db_history.updated_at = None
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_db_history
        mock_session.query.return_value = mock_query
        
        result = repository.get_by_id(valid_history.id)
        
        assert result is not None
        assert result.id == valid_history.id
        mock_session.close.assert_called_once()
    
    def test_get_by_id_not_found(self, repository, mock_session):
        """Test: Registro no encontrado por ID"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = repository.get_by_id('non-existent-id')
        
        assert result is None
        mock_session.close.assert_called_once()
    
    def test_get_all_success(self, repository, mock_session):
        """Test: Obtener todos los registros exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_db_history = MagicMock()
        mock_db_history.id = '123'
        mock_db_history.file_name = 'products.csv'
        mock_db_history.user_id = 'user123'
        mock_db_history.status = 'En curso'
        mock_db_history.result = None
        mock_db_history.created_at = datetime.utcnow()
        mock_db_history.updated_at = None
        
        # Configurar mock con encadenamiento correcto
        mock_all = MagicMock(return_value=[mock_db_history])
        mock_offset = MagicMock()
        mock_offset.all = mock_all
        mock_limit = MagicMock(return_value=mock_offset)
        mock_order_by = MagicMock()
        mock_order_by.limit = mock_limit
        mock_query = MagicMock()
        mock_query.order_by = MagicMock(return_value=mock_order_by)
        mock_session.query.return_value = mock_query
        
        result = repository.get_all(limit=10, offset=0)
        
        assert len(result) == 1
        assert result[0].id == '123'
        mock_session.close.assert_called_once()
    
    def test_update_history_success(self, repository, mock_session, valid_history):
        """Test: Actualizar registro exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_db_history = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_db_history
        mock_session.query.return_value = mock_query
        
        valid_history.status = 'Completado'
        result = repository.update(valid_history)
        
        assert result.status == 'Completado'
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_delete_history_success(self, repository, mock_session):
        """Test: Eliminar registro exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_db_history = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_db_history
        mock_session.query.return_value = mock_query
        
        result = repository.delete('123')
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_db_history)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_delete_history_not_found(self, repository, mock_session):
        """Test: Eliminar registro no encontrado"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        result = repository.delete('non-existent-id')
        
        assert result is False
        mock_session.close.assert_called_once()
    
    def test_get_by_user_id_success(self, repository, mock_session):
        """Test: Obtener registros por user_id exitosamente con offset"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_db_history = MagicMock()
        mock_db_history.id = '123'
        mock_db_history.file_name = 'products.csv'
        mock_db_history.user_id = 'user123'
        mock_db_history.status = 'En curso'
        mock_db_history.result = None
        mock_db_history.created_at = datetime.utcnow()
        mock_db_history.updated_at = None
        
        # Configurar el mock con el chain completo incluyendo offset
        mock_all = MagicMock()
        mock_all.all.return_value = [mock_db_history]
        
        mock_limit = MagicMock()
        mock_limit.offset.return_value = mock_all
        mock_limit.all.return_value = [mock_db_history]  # Para cuando no hay offset
        
        mock_order_by = MagicMock()
        mock_order_by.limit.return_value = mock_limit
        
        mock_filter = MagicMock()
        mock_filter.order_by.return_value = mock_order_by
        
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_filter
        
        mock_session.query.return_value = mock_query
        
        # Test con offset = 10
        result = repository.get_by_user_id('user123', limit=10, offset=10)
        
        assert len(result) == 1
        assert result[0].user_id == 'user123'
        mock_session.close.assert_called_once()
    
    def test_get_count_success(self, repository, mock_session):
        """Test: Obtener conteo de registros exitosamente"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_query = MagicMock()
        mock_query.count.return_value = 25
        mock_session.query.return_value = mock_query
        
        result = repository.get_count()
        
        assert result == 25
        mock_session.query.assert_called_once()
        mock_query.count.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_get_count_with_user_id(self, repository, mock_session):
        """Test: Obtener conteo de registros filtrado por user_id"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_query = MagicMock()
        mock_query.filter.return_value.count.return_value = 10
        mock_session.query.return_value = mock_query
        
        result = repository.get_count(user_id='user123')
        
        assert result == 10
        mock_query.filter.assert_called_once()
        mock_session.close.assert_called_once()
    
    def test_get_count_zero(self, repository, mock_session):
        """Test: Conteo retorna cero cuando no hay registros"""
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_session.query.return_value = mock_query
        
        result = repository.get_count()
        
        assert result == 0
        mock_session.close.assert_called_once()
    
    def test_get_count_with_error(self, repository, mock_session):
        """Test: Error al obtener conteo"""
        from sqlalchemy.exc import SQLAlchemyError
        
        repository._get_session = MagicMock(return_value=mock_session)
        
        mock_session.query.side_effect = SQLAlchemyError("Database error")
        
        with pytest.raises(Exception) as exc_info:
            repository.get_count()
        
        assert "Error al obtener conteo de historial" in str(exc_info.value)
        mock_session.close.assert_called_once()

