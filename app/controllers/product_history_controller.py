"""
Controlador para el historial de productos procesados
"""
from flask import request
from flask_restful import Resource
from app.controllers.base_controller import BaseController
from app.services.product_history_service import ProductHistoryService
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError
import logging

logger = logging.getLogger(__name__)


class ProductHistoryController(Resource, BaseController):
    """
    Controlador para gestión del historial de productos procesados
    Endpoint: GET /inventory/products/history
    """
    
    def __init__(self):
        """
        Inicializa el controlador
        """
        self.service = ProductHistoryService()
    
    def get(self):
        """
        Obtiene el historial de productos procesados con paginación
        
        Query Parameters:
            page (int, opcional): Número de página (default: 1, mínimo: 1)
            per_page (int, opcional): Registros por página (default: 10, rango: 1-100)
            user_id (str, opcional): ID del usuario para filtrar resultados
        
        Returns:
            JSON con la lista paginada de registros de historial y metadatos de paginación
        """
        try:
            # Obtener parámetros de query
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            user_id = request.args.get('user_id', type=str)
            
            # Validar page
            if page < 1:
                raise ValidationError("El parámetro 'page' debe ser mayor a 0")
            
            # Validar per_page
            if per_page < 1 or per_page > 100:
                raise ValidationError("El parámetro 'per_page' debe estar entre 1 y 100")
            
            # Obtener historial paginado
            logger.info(f"Consultando historial (page={page}, per_page={per_page}, user_id={user_id})")
            history_list = self.service.get_history_paginated(
                page=page,
                per_page=per_page,
                user_id=user_id
            )
            
            # Obtener total de registros
            total = self.service.get_history_count(user_id=user_id)
            
            # Calcular metadatos de paginación
            total_pages = (total + per_page - 1) // per_page
            has_next = page < total_pages
            has_prev = page > 1
            
            return self.success_response(
                data={
                    'history': history_list,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': total,
                        'total_pages': total_pages,
                        'has_next': has_next,
                        'has_prev': has_prev,
                        'next_page': page + 1 if has_next else None,
                        'prev_page': page - 1 if has_prev else None
                    }
                },
                message="Historial obtenido exitosamente"
            )
            
        except ValidationError as e:
            logger.warning(f"Error de validación en consulta de historial: {str(e)}")
            return self.handle_exception(e)
        except BusinessLogicError as e:
            logger.error(f"Error de lógica de negocio en consulta de historial: {str(e)}")
            return self.handle_exception(e)
        except Exception as e:
            logger.error(f"Error inesperado al consultar historial: {str(e)}")
            return self.handle_exception(e)
