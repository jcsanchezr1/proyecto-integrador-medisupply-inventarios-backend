"""
Servicio para gestión del historial de productos procesados
"""
import logging
from typing import List, Dict, Optional
from app.repositories.product_processed_history_repository import ProductProcessedHistoryRepository
from app.external.authenticator_service import AuthenticatorService

logger = logging.getLogger(__name__)


class ProductHistoryService:
    """
    Servicio para gestión del historial de productos procesados
    """
    
    def __init__(self):
        """
        Inicializa el servicio con sus dependencias
        """
        self.history_repository = ProductProcessedHistoryRepository()
        self.authenticator_service = AuthenticatorService()
    
    def get_history_paginated(self, page: int = 1, per_page: int = 10, user_id: Optional[str] = None) -> List[Dict]:
        """
        Obtiene el historial de productos procesados paginado
        
        Args:
            page: Número de página (empieza en 1)
            per_page: Cantidad de registros por página
            user_id: ID del usuario para filtrar (opcional)
            
        Returns:
            List[Dict]: Lista de registros de historial con información del usuario
            
        Raises:
            Exception: Si hay error al obtener los datos
        """
        try:
            # Calcular offset
            offset = (page - 1) * per_page
            
            # Obtener registros del historial
            if user_id:
                histories = self.history_repository.get_by_user_id(user_id, limit=per_page, offset=offset)
            else:
                histories = self.history_repository.get_all(limit=per_page, offset=offset)
            
            # Preparar respuesta
            result = []
            for history in histories:
                # Obtener nombre del usuario
                user_name = self.authenticator_service.get_user_name(history.user_id)
                
                # Construir respuesta
                history_data = {
                    'id': history.id,
                    'file_name': history.file_name,
                    'created_at': history.created_at.isoformat() if history.created_at else None,
                    'status': history.status,
                    'result': history.result,
                    'user': user_name
                }
                
                result.append(history_data)
            
            logger.info(f"Se obtuvieron {len(result)} registros del historial (página {page})")
            return result
            
        except Exception as e:
            logger.error(f"Error al obtener historial de productos procesados: {str(e)}")
            raise Exception(f"Error al obtener historial: {str(e)}")
    
    def get_history_count(self, user_id: Optional[str] = None) -> int:
        """
        Obtiene el conteo total de registros de historial
        
        Args:
            user_id: ID del usuario para filtrar (opcional)
            
        Returns:
            int: Total de registros
            
        Raises:
            Exception: Si hay error al obtener el conteo
        """
        try:
            return self.history_repository.get_count(user_id=user_id)
        except Exception as e:
            logger.error(f"Error al obtener conteo de historial: {str(e)}")
            raise Exception(f"Error al obtener conteo: {str(e)}")

