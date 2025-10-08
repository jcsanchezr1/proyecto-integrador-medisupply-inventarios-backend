"""
Tests para BaseService
"""
import pytest
from abc import ABC
from app.services.base_service import BaseService


class ConcreteService(BaseService):
    """Implementación concreta de BaseService para testing"""
    
    def create(self, entity_data: dict):
        return {"id": 1, **entity_data}
    
    def get_by_id(self, entity_id: int):
        return {"id": entity_id}
    
    def get_all(self) -> list:
        return [{"id": 1}, {"id": 2}]


class TestBaseService:
    """Tests para BaseService"""
    
    def test_base_service_is_abstract(self):
        """Test: BaseService es una clase abstracta"""
        assert issubclass(BaseService, ABC)
    
    def test_base_service_cannot_be_instantiated(self):
        """Test: BaseService no puede ser instanciada directamente"""
        with pytest.raises(TypeError):
            BaseService()
    
    def test_concrete_service_can_be_instantiated(self):
        """Test: Una implementación concreta puede ser instanciada"""
        service = ConcreteService()
        assert isinstance(service, BaseService)
    
    def test_concrete_service_create_method(self):
        """Test: Método create de implementación concreta"""
        service = ConcreteService()
        result = service.create({"name": "test"})
        
        assert result == {"id": 1, "name": "test"}
    
    def test_concrete_service_get_by_id_method(self):
        """Test: Método get_by_id de implementación concreta"""
        service = ConcreteService()
        result = service.get_by_id(123)
        
        assert result == {"id": 123}
    
    def test_concrete_service_get_all_method(self):
        """Test: Método get_all de implementación concreta"""
        service = ConcreteService()
        result = service.get_all()
        
        assert result == [{"id": 1}, {"id": 2}]
    
    def test_base_service_has_abstract_methods(self):
        """Test: BaseService tiene métodos abstractos definidos"""
        abstract_methods = BaseService.__abstractmethods__
        
        assert 'create' in abstract_methods
        assert 'get_by_id' in abstract_methods
        assert 'get_all' in abstract_methods


