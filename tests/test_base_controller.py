import pytest
from app.controllers.base_controller import BaseController
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestBaseController:
    """Tests para BaseController"""
    
    @pytest.fixture
    def base_controller(self):
        """Instancia de BaseController"""
        return BaseController()
    
    def test_success_response_with_data(self, base_controller):
        """Test: Respuesta de éxito con datos"""
        data = {'id': 1, 'name': 'Test'}
        response, status_code = base_controller.success_response(data, "Operación exitosa")
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Operación exitosa"
        assert response['data'] == data
    
    def test_success_response_without_data(self, base_controller):
        """Test: Respuesta de éxito sin datos"""
        response, status_code = base_controller.success_response()
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Operación exitosa"
        assert 'data' not in response
    
    def test_success_response_with_none_data(self, base_controller):
        """Test: Respuesta de éxito con datos None"""
        response, status_code = base_controller.success_response(data=None)
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Operación exitosa"
        assert 'data' not in response
    
    def test_success_response_custom_message(self, base_controller):
        """Test: Respuesta de éxito con mensaje personalizado"""
        response, status_code = base_controller.success_response(message="Producto creado")
        
        assert status_code == 200
        assert response['success'] is True
        assert response['message'] == "Producto creado"
    
    def test_error_response_basic(self, base_controller):
        """Test: Respuesta de error básica"""
        response, status_code = base_controller.error_response("Error de validación")
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert 'details' not in response
    
    def test_error_response_with_details(self, base_controller):
        """Test: Respuesta de error con detalles"""
        response, status_code = base_controller.error_response(
            "Error de validación", 
            "Campo requerido faltante", 
            422
        )
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Campo requerido faltante"
    
    def test_error_response_custom_status_code(self, base_controller):
        """Test: Respuesta de error con código de estado personalizado"""
        response, status_code = base_controller.error_response(
            "Error interno", 
            status_code=500
        )
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error interno"
    
    def test_handle_exception_validation_error(self, base_controller):
        """Test: Manejo de excepción ValidationError"""
        error = ValidationError("Error de validación")
        response, status_code = base_controller.handle_exception(error)
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Error de validación"
    
    def test_handle_exception_business_logic_error(self, base_controller):
        """Test: Manejo de excepción BusinessLogicError"""
        error = BusinessLogicError("Error de lógica de negocio")
        response, status_code = base_controller.handle_exception(error)
        
        assert status_code == 422
        assert response['success'] is False
        assert response['error'] == "Error de lógica de negocio"
        assert response['details'] == "Error de lógica de negocio"
    
    def test_handle_exception_generic_exception(self, base_controller):
        """Test: Manejo de excepción genérica"""
        error = Exception("Error interno")
        response, status_code = base_controller.handle_exception(error)
        
        assert status_code == 500
        assert response['success'] is False
        assert response['error'] == "Error temporal del sistema. Contacte soporte técnico si persiste"
        assert 'details' not in response
    
    def test_handle_exception_with_details(self, base_controller):
        """Test: Manejo de excepción con detalles"""
        error = ValidationError("Error específico")
        response, status_code = base_controller.handle_exception(error)
        
        assert status_code == 400
        assert response['success'] is False
        assert response['error'] == "Error de validación"
        assert response['details'] == "Error específico"
