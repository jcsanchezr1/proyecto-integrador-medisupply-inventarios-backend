"""
Tests para BaseModel
"""
import pytest
from abc import ABC
from app.models.base_model import BaseModel


class ConcreteModel(BaseModel):
    """Implementación concreta de BaseModel para testing"""
    
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    
    def validate(self) -> None:
        if not self.name:
            raise ValueError("Name is required")
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}


class TestBaseModel:
    """Tests para BaseModel"""
    
    def test_base_model_is_abstract(self):
        """Test: BaseModel es una clase abstracta"""
        assert issubclass(BaseModel, ABC)
    
    def test_base_model_cannot_be_instantiated(self):
        """Test: BaseModel no puede ser instanciada directamente"""
        with pytest.raises(TypeError):
            BaseModel()
    
    def test_concrete_model_can_be_instantiated(self):
        """Test: Una implementación concreta puede ser instanciada"""
        model = ConcreteModel("test")
        assert isinstance(model, BaseModel)
    
    def test_base_model_has_id_attribute(self):
        """Test: BaseModel tiene atributo id"""
        model = ConcreteModel("test")
        assert hasattr(model, 'id')
        assert model.id is None
    
    def test_concrete_model_validate_method(self):
        """Test: Método validate de implementación concreta"""
        model = ConcreteModel("test")
        model.validate()  # No debe lanzar excepción
        
        invalid_model = ConcreteModel("")
        with pytest.raises(ValueError, match="Name is required"):
            invalid_model.validate()
    
    def test_concrete_model_to_dict_method(self):
        """Test: Método to_dict de implementación concreta"""
        model = ConcreteModel("test")
        result = model.to_dict()
        
        assert result == {"id": None, "name": "test"}
    
    def test_base_model_has_abstract_methods(self):
        """Test: BaseModel tiene métodos abstractos definidos"""
        abstract_methods = BaseModel.__abstractmethods__
        
        assert 'validate' in abstract_methods
        assert 'to_dict' in abstract_methods
    
    def test_base_model_repr_method(self):
        """Test: Método __repr__ de BaseModel"""
        model = ConcreteModel("test")
        repr_str = repr(model)
        
        assert "ConcreteModel" in repr_str
        assert "id=None" in repr_str


