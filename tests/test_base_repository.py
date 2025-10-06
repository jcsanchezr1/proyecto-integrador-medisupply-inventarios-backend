"""
Tests para BaseRepository
"""
import pytest
from abc import ABC
from app.repositories.base_repository import BaseRepository


class ConcreteRepository(BaseRepository):
    """Implementación concreta de BaseRepository para testing"""
    
    def __init__(self):
        self.entities = {}
        self.next_id = 1
    
    def create(self, entity):
        entity.id = self.next_id
        self.entities[self.next_id] = entity
        self.next_id += 1
        return entity
    
    def get_by_id(self, entity_id: int):
        return self.entities.get(entity_id)
    
    def get_all(self) -> list:
        return list(self.entities.values())
    
    def update(self, entity):
        if entity.id in self.entities:
            self.entities[entity.id] = entity
        return entity
    
    def delete(self, entity_id: int) -> bool:
        if entity_id in self.entities:
            del self.entities[entity_id]
            return True
        return False


class TestBaseRepository:
    """Tests para BaseRepository"""
    
    def test_base_repository_is_abstract(self):
        """Test: BaseRepository es una clase abstracta"""
        assert issubclass(BaseRepository, ABC)
    
    def test_base_repository_cannot_be_instantiated(self):
        """Test: BaseRepository no puede ser instanciada directamente"""
        with pytest.raises(TypeError):
            BaseRepository()
    
    def test_concrete_repository_can_be_instantiated(self):
        """Test: Una implementación concreta puede ser instanciada"""
        repository = ConcreteRepository()
        assert isinstance(repository, BaseRepository)
    
    def test_concrete_repository_create_method(self):
        """Test: Método create de implementación concreta"""
        repository = ConcreteRepository()
        
        class MockEntity:
            def __init__(self, name):
                self.name = name
                self.id = None
        
        entity = MockEntity("test")
        result = repository.create(entity)
        
        assert result.id == 1
        assert result.name == "test"
    
    def test_concrete_repository_get_by_id_method(self):
        """Test: Método get_by_id de implementación concreta"""
        repository = ConcreteRepository()
        
        class MockEntity:
            def __init__(self, name):
                self.name = name
                self.id = None
        
        entity = MockEntity("test")
        repository.create(entity)
        
        result = repository.get_by_id(1)
        assert result.name == "test"
        
        result = repository.get_by_id(999)
        assert result is None
    
    def test_concrete_repository_get_all_method(self):
        """Test: Método get_all de implementación concreta"""
        repository = ConcreteRepository()
        
        class MockEntity:
            def __init__(self, name):
                self.name = name
                self.id = None
        
        entity1 = MockEntity("test1")
        entity2 = MockEntity("test2")
        
        repository.create(entity1)
        repository.create(entity2)
        
        result = repository.get_all()
        assert len(result) == 2
        assert result[0].name == "test1"
        assert result[1].name == "test2"
    
    def test_concrete_repository_update_method(self):
        """Test: Método update de implementación concreta"""
        repository = ConcreteRepository()
        
        class MockEntity:
            def __init__(self, name):
                self.name = name
                self.id = None
        
        entity = MockEntity("test")
        repository.create(entity)
        
        entity.name = "updated"
        result = repository.update(entity)
        
        assert result.name == "updated"
        assert repository.get_by_id(1).name == "updated"
    
    def test_concrete_repository_delete_method(self):
        """Test: Método delete de implementación concreta"""
        repository = ConcreteRepository()
        
        class MockEntity:
            def __init__(self, name):
                self.name = name
                self.id = None
        
        entity = MockEntity("test")
        repository.create(entity)
        
        result = repository.delete(1)
        assert result is True
        assert repository.get_by_id(1) is None
        
        result = repository.delete(999)
        assert result is False
    
    def test_base_repository_has_abstract_methods(self):
        """Test: BaseRepository tiene métodos abstractos definidos"""
        abstract_methods = BaseRepository.__abstractmethods__
        
        assert 'create' in abstract_methods
        assert 'get_by_id' in abstract_methods
        assert 'get_all' in abstract_methods
        assert 'update' in abstract_methods
        assert 'delete' in abstract_methods


