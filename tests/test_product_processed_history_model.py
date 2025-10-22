"""
Tests para el modelo ProductProcessedHistory
"""
import pytest
from datetime import datetime
from app.models.product_processed_history import ProductProcessedHistory


class TestProductProcessedHistory:
    """Tests para ProductProcessedHistory"""
    
    @pytest.fixture
    def valid_history_data(self):
        """Datos válidos para crear un registro de historial"""
        return {
            'file_name': 'products_abc123.csv',
            'user_id': '550e8400-e29b-41d4-a716-446655440000',
            'status': 'En curso',
            'result': None,
            'id': '123e4567-e89b-12d3-a456-426614174000'
        }
    
    def test_create_product_processed_history_success(self, valid_history_data):
        """Test: Crear un registro de historial exitosamente"""
        history = ProductProcessedHistory(**valid_history_data)
        
        assert history.file_name == valid_history_data['file_name']
        assert history.user_id == valid_history_data['user_id']
        assert history.status == valid_history_data['status']
        assert history.result == valid_history_data['result']
        assert history.id == valid_history_data['id']
        assert isinstance(history.created_at, datetime)
    
    def test_create_product_processed_history_with_defaults(self):
        """Test: Crear un registro de historial con valores por defecto"""
        history = ProductProcessedHistory(
            file_name='products.csv',
            user_id='user123'
        )
        
        assert history.file_name == 'products.csv'
        assert history.user_id == 'user123'
        assert history.status == 'En curso'
        assert history.result is None
        assert history.id is None
        assert isinstance(history.created_at, datetime)
    
    def test_validate_success(self, valid_history_data):
        """Test: Validación exitosa"""
        history = ProductProcessedHistory(**valid_history_data)
        history.validate()  # No debe lanzar excepción
    
    def test_validate_missing_file_name(self, valid_history_data):
        """Test: Error de validación por file_name faltante"""
        valid_history_data['file_name'] = ''
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El nombre del archivo es obligatorio"):
            history.validate()
    
    def test_validate_missing_user_id(self, valid_history_data):
        """Test: Error de validación por user_id faltante"""
        valid_history_data['user_id'] = ''
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El ID del usuario es obligatorio"):
            history.validate()
    
    def test_validate_missing_status(self, valid_history_data):
        """Test: Error de validación por status faltante"""
        valid_history_data['status'] = ''
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El estado es obligatorio"):
            history.validate()
    
    def test_validate_file_name_too_long(self, valid_history_data):
        """Test: Error de validación por file_name demasiado largo"""
        valid_history_data['file_name'] = 'a' * 101
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El nombre del archivo no puede exceder 100 caracteres"):
            history.validate()
    
    def test_validate_user_id_too_long(self, valid_history_data):
        """Test: Error de validación por user_id demasiado largo"""
        valid_history_data['user_id'] = 'a' * 37
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El ID del usuario no puede exceder 36 caracteres"):
            history.validate()
    
    def test_validate_status_too_long(self, valid_history_data):
        """Test: Error de validación por status demasiado largo"""
        valid_history_data['status'] = 'a' * 21
        history = ProductProcessedHistory(**valid_history_data)
        
        with pytest.raises(ValueError, match="El estado no puede exceder 20 caracteres"):
            history.validate()
    
    def test_to_dict(self, valid_history_data):
        """Test: Conversión a diccionario"""
        history = ProductProcessedHistory(**valid_history_data)
        history_dict = history.to_dict()
        
        assert history_dict['file_name'] == valid_history_data['file_name']
        assert history_dict['user_id'] == valid_history_data['user_id']
        assert history_dict['status'] == valid_history_data['status']
        assert history_dict['result'] == valid_history_data['result']
        assert history_dict['id'] == valid_history_data['id']
        assert 'created_at' in history_dict
    
    def test_repr(self, valid_history_data):
        """Test: Representación en string"""
        history = ProductProcessedHistory(**valid_history_data)
        repr_str = repr(history)
        
        assert 'ProductProcessedHistory' in repr_str
        assert valid_history_data['id'] in repr_str
        assert valid_history_data['file_name'] in repr_str
        assert valid_history_data['status'] in repr_str

