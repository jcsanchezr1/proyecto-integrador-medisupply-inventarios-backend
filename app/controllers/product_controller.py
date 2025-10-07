from flask import request
from flask_restful import Resource
from typing import Dict, Any, Tuple, Optional
from app.controllers.base_controller import BaseController
from app.services.product_service import ProductService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class ProductController(BaseController, Resource):
    """
    Controlador para operaciones de productos
    """
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def post(self) -> Tuple[Dict[str, Any], int]:
        """
        Crea un nuevo producto
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            # Determinar el tipo de contenido
            if request.is_json:
                product_data = request.get_json()
                photo_file = None
            elif request.content_type and 'multipart/form-data' in request.content_type:
                product_data, photo_file = self._extract_multipart_data()
            else:
                return self.error_response("Content-Type no soportado", "Se requiere application/json o multipart/form-data", 415)
            
            # Crear producto
            product = self.product_service.create_product(product_data, photo_file)
            
            return self.created_response(
                data=product.to_dict(),
                message="Producto registrado exitosamente"
            )
            
        except ValidationError as e:
            return self.handle_exception(e)
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def get(self, product_id: int = None) -> Tuple[Dict[str, Any], int]:
        """
        Obtiene productos
        
        Args:
            product_id: ID del producto (opcional)
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            if product_id:
                # Obtener producto específico
                product = self.product_service.get_product_by_id(product_id)
                if not product:
                    return self.error_response("Producto no encontrado", None, 404)
                
                return self.success_response(data=product.to_dict())
            else:
                # Obtener todos los productos
                products_summary = self.product_service.get_products_summary()
                return self.success_response(data=products_summary)
                
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def delete(self, product_id: int) -> Tuple[Dict[str, Any], int]:
        """
        Elimina un producto
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            success = self.product_service.delete_product(product_id)
            if success:
                return self.success_response(message="Producto eliminado exitosamente")
            else:
                return self.error_response("No se pudo eliminar el producto", None, 500)
                
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
    
    def _extract_multipart_data(self) -> Tuple[Dict[str, Any], Optional[Any]]:
        """
        Extrae datos de una petición multipart/form-data
        
        Returns:
            Tuple[Dict[str, Any], Optional[Any]]: Datos extraídos y archivo de foto
            
        Raises:
            ValidationError: Si hay error en el formato de datos
        """
        try:
            # Obtener datos del formulario
            form_data = request.form.to_dict()
            
            # Obtener archivo de foto si existe
            photo_file = request.files.get('photo')
            
            return form_data, photo_file
            
        except Exception as e:
            raise ValidationError(f"Error al procesar datos multipart: {str(e)}")


class ProductDeleteAllController(BaseController, Resource):
    """
    Controlador para eliminar todos los productos
    """
    
    def __init__(self, product_service=None):
        self.product_service = product_service or ProductService()
    
    def delete(self) -> Tuple[Dict[str, Any], int]:
        """
        Elimina todos los productos
        
        Returns:
            Tuple[Dict[str, Any], int]: Respuesta y código de estado
        """
        try:
            deleted_count = self.product_service.delete_all_products()
            return self.success_response(
                data={"deleted_count": deleted_count},
                message=f"Se eliminaron {deleted_count} productos"
            )
            
        except BusinessLogicError as e:
            return self.handle_exception(e)
        except Exception as e:
            return self.handle_exception(e)
