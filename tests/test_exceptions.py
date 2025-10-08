"""
Tests para las excepciones personalizadas
"""
import pytest
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestValidationError:
    """Tests para ValidationError"""
    
    def test_validation_error_inheritance(self):
        """Test: ValidationError hereda de Exception"""
        error = ValidationError("Test error")
        assert isinstance(error, Exception)
    
    def test_validation_error_message(self):
        """Test: ValidationError mantiene el mensaje"""
        message = "Campo requerido faltante"
        error = ValidationError(message)
        assert str(error) == message
    
    def test_validation_error_empty_message(self):
        """Test: ValidationError con mensaje vacío"""
        error = ValidationError("")
        assert str(error) == ""
    
    def test_validation_error_can_be_raised(self):
        """Test: ValidationError puede ser lanzada"""
        with pytest.raises(ValidationError, match="Error de validación"):
            raise ValidationError("Error de validación")


class TestBusinessLogicError:
    """Tests para BusinessLogicError"""
    
    def test_business_logic_error_inheritance(self):
        """Test: BusinessLogicError hereda de Exception"""
        error = BusinessLogicError("Test error")
        assert isinstance(error, Exception)
    
    def test_business_logic_error_message(self):
        """Test: BusinessLogicError mantiene el mensaje"""
        message = "SKU ya existe en el sistema"
        error = BusinessLogicError(message)
        assert str(error) == message
    
    def test_business_logic_error_empty_message(self):
        """Test: BusinessLogicError con mensaje vacío"""
        error = BusinessLogicError("")
        assert str(error) == ""
    
    def test_business_logic_error_can_be_raised(self):
        """Test: BusinessLogicError puede ser lanzada"""
        with pytest.raises(BusinessLogicError, match="Error de lógica"):
            raise BusinessLogicError("Error de lógica")
    
    def test_business_logic_error_different_from_validation_error(self):
        """Test: BusinessLogicError es diferente de ValidationError"""
        validation_error = ValidationError("Validation error")
        business_error = BusinessLogicError("Business error")
        
        assert not isinstance(business_error, ValidationError)
        assert not isinstance(validation_error, BusinessLogicError)


