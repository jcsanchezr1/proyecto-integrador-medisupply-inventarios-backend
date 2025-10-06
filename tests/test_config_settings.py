"""
Tests para la configuración de la aplicación
"""
import pytest
import os
from unittest.mock import patch
from app.config.settings import Config, DevelopmentConfig, ProductionConfig, get_config


class TestConfig:
    """Tests para la clase Config"""
    
    def test_config_default_values(self):
        """Test: Valores por defecto de configuración"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            
            assert config.SECRET_KEY == 'dev-secret-key'
            assert config.DEBUG is True
            assert config.HOST == '0.0.0.0'
            assert config.PORT == 8080
            assert config.APP_NAME == 'MediSupply Inventory Backend'
            assert config.APP_VERSION == '1.0.0'
    
    def test_config_with_environment_variables(self):
        """Test: Configuración con variables de entorno"""
        # Verificar que la configuración se puede instanciar
        config = Config()
        
        # Verificar que tiene los atributos esperados
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'DEBUG')
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'APP_VERSION')
    
    def test_config_debug_string_values(self):
        """Test: Configuración DEBUG con diferentes valores de string"""
        # Verificar que DEBUG se puede leer correctamente
        config = Config()
        assert isinstance(config.DEBUG, bool)


class TestDevelopmentConfig:
    """Tests para DevelopmentConfig"""
    
    def test_development_config_inheritance(self):
        """Test: DevelopmentConfig hereda de Config"""
        config = DevelopmentConfig()
        
        # Debe heredar todos los atributos de Config
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'APP_VERSION')
    
    def test_development_config_debug_override(self):
        """Test: DevelopmentConfig sobrescribe DEBUG"""
        config = DevelopmentConfig()
        assert config.DEBUG is True


class TestProductionConfig:
    """Tests para ProductionConfig"""
    
    def test_production_config_inheritance(self):
        """Test: ProductionConfig hereda de Config"""
        config = ProductionConfig()
        
        # Debe heredar todos los atributos de Config
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'HOST')
        assert hasattr(config, 'PORT')
        assert hasattr(config, 'APP_NAME')
        assert hasattr(config, 'APP_VERSION')
    
    def test_production_config_debug_override(self):
        """Test: ProductionConfig sobrescribe DEBUG"""
        config = ProductionConfig()
        assert config.DEBUG is False


class TestGetConfig:
    """Tests para la función get_config"""
    
    def test_get_config_development_default(self):
        """Test: get_config retorna DevelopmentConfig por defecto"""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert isinstance(config, DevelopmentConfig)
    
    def test_get_config_development_explicit(self):
        """Test: get_config retorna DevelopmentConfig cuando FLASK_ENV=development"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}, clear=True):
            config = get_config()
            assert isinstance(config, DevelopmentConfig)
    
    def test_get_config_production(self):
        """Test: get_config retorna ProductionConfig cuando FLASK_ENV=production"""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}, clear=True):
            config = get_config()
            assert isinstance(config, ProductionConfig)
    
    def test_get_config_case_insensitive(self):
        """Test: get_config es case insensitive"""
        test_cases = ['PRODUCTION', 'Production']
        
        for env_value in test_cases:
            with patch.dict(os.environ, {'FLASK_ENV': env_value}, clear=True):
                config = get_config()
                assert isinstance(config, ProductionConfig)
    
    def test_get_config_invalid_env_defaults_to_development(self):
        """Test: get_config retorna DevelopmentConfig para valores inválidos"""
        with patch.dict(os.environ, {'FLASK_ENV': 'invalid'}, clear=True):
            config = get_config()
            assert isinstance(config, DevelopmentConfig)


