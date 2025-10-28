from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging
from app.services.product_service import ProductService
from app.external.provider_service import ProviderService
from app.external.authenticator_service import AuthenticatorService
from app.exceptions.business_logic_error import BusinessLogicError

logger = logging.getLogger(__name__)


class ProviderProductsService:
    """
    Servicio para la lógica de negocio de productos agrupados por proveedor
    """
    
    def __init__(self, product_service=None, provider_service=None, authenticator_service=None):
        self.product_service = product_service or ProductService()
        self.provider_service = provider_service or ProviderService()
        self.authenticator_service = authenticator_service or AuthenticatorService()
    
    def get_products_grouped_by_provider(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene todos los productos agrupados por proveedor
        
        Args:
            user_id: ID del usuario para obtener recomendaciones (opcional)
        
        Returns:
            Dict[str, Any]: Diccionario con la estructura de respuesta
            
        Raises:
            BusinessLogicError: Si hay error en la lógica de negocio
        """
        try:
            # Obtener todos los productos
            products = self.product_service.get_all_products()
            
            if not products:
                return {
                    "groups": [],
                    "message": "No hay productos registrados"
                }
            
            # Agrupar productos por provider_id
            products_by_provider = self._group_products_by_provider(products)
            
            # Obtener información de proveedores de manera eficiente
            unique_provider_ids = list(products_by_provider.keys())
            provider_names = self._get_provider_names_efficiently(unique_provider_ids)
            
            # Construir respuesta agrupada
            groups = self._build_groups_response(products_by_provider, provider_names)
            
            # Si viene user_id, intentar agregar grupo de recomendados
            if user_id:
                groups = self._add_recommendations_group(groups, products, user_id)
            
            return {
                "groups": groups,
                "message": "Productos agrupados por proveedor obtenidos exitosamente"
            }
            
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener productos agrupados por proveedor: {str(e)}")
    
    def _group_products_by_provider(self, products: List[Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa productos por provider_id
        
        Args:
            products: Lista de productos
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Productos agrupados por provider_id
        """
        from datetime import datetime
        
        products_by_provider = defaultdict(list)
        
        for product in products:
            provider_id = product.provider_id
            
            # Manejar fecha de expiración - devolver como viene de BD
            expiration_date_value = product.expiration_date
            
            # Si es datetime, convertir a ISO string para JSON
            if isinstance(expiration_date_value, datetime):
                expiration_date_value = expiration_date_value.isoformat()
            
            # Crear objeto de producto con campos adicionales
            product_data = {
                "id": product.id,
                "name": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "photo_url": product.photo_url,
                "expiration_date": expiration_date_value,
                "description": product.description
            }
            
            products_by_provider[provider_id].append(product_data)
        
        return dict(products_by_provider)
    
    def _get_provider_names_efficiently(self, provider_ids: List[str]) -> Dict[str, str]:
        """
        Obtiene los nombres de los proveedores de manera eficiente
        
        Args:
            provider_ids: Lista de IDs de proveedores únicos
            
        Returns:
            Dict[str, str]: Diccionario con provider_id como clave y nombre como valor
        """
        provider_names = {}
        
        try:
            # Consultar todos los proveedores de una vez
            providers = self.provider_service.get_providers_batch(provider_ids)
            
            for provider_id, provider in providers.items():
                if provider:
                    provider_names[provider_id] = provider.name
                else:
                    provider_names[provider_id] = "Proveedor no asociado"
                    
        except Exception as e:
            # Si falla la consulta masiva, intentar individualmente
            for provider_id in provider_ids:
                try:
                    provider_name = self.provider_service.get_provider_name(provider_id)
                    provider_names[provider_id] = provider_name
                except Exception:
                    provider_names[provider_id] = "Proveedor no asociado"
        
        return provider_names
    
    def _build_groups_response(self, products_by_provider: Dict[str, List[Dict[str, Any]]], 
                              provider_names: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Construye la respuesta final con los grupos de productos
        
        Args:
            products_by_provider: Productos agrupados por provider_id
            provider_names: Nombres de los proveedores
            
        Returns:
            List[Dict[str, Any]]: Lista de grupos con proveedores y sus productos
        """
        # Agrupar por nombre de proveedor para consolidar productos del mismo proveedor
        products_by_name = defaultdict(list)
        
        for provider_id, products_list in products_by_provider.items():
            provider_name = provider_names.get(provider_id, "Proveedor no asociado")
            products_by_name[provider_name].extend(products_list)
        
        # Construir la lista de grupos
        groups = []
        for provider_name, products_list in products_by_name.items():
            group = {
                "provider": provider_name,
                "products": products_list
            }
            groups.append(group)
        
        return groups
    
    def _add_recommendations_group(self, groups: List[Dict[str, Any]], 
                                   products: List[Any], 
                                   user_id: str) -> List[Dict[str, Any]]:
        """
        Agrega un grupo de recomendados basado en la especialidad del usuario
        
        Args:
            groups: Lista de grupos existentes
            products: Lista de todos los productos
            user_id: ID del usuario
            
        Returns:
            List[Dict[str, Any]]: Lista de grupos con recomendados al inicio (si aplica)
        """
        try:
            # Intentar obtener el usuario
            user = self.authenticator_service.get_user_by_id(user_id)
            
            # Si no existe el usuario o no tiene specialty, retornar grupos sin cambios
            if not user or 'specialty' not in user or not user['specialty']:
                logger.info(f"Usuario {user_id} no encontrado o sin specialty, retornando grupos normales")
                return groups
            
            specialty = user['specialty']
            logger.info(f"Usuario encontrado con specialty: {specialty}")
            
            # Filtrar productos que coincidan con la specialty (usando product_type)
            recommended_products = []
            for product in products:
                if hasattr(product, 'product_type') and product.product_type == specialty:
                    # Usar el mismo formato que en _group_products_by_provider
                    from datetime import datetime
                    
                    expiration_date_value = product.expiration_date
                    if isinstance(expiration_date_value, datetime):
                        expiration_date_value = expiration_date_value.isoformat()
                    
                    product_data = {
                        "id": product.id,
                        "name": product.name,
                        "quantity": product.quantity,
                        "price": product.price,
                        "photo_url": product.photo_url,
                        "expiration_date": expiration_date_value,
                        "description": product.description
                    }
                    recommended_products.append(product_data)
                    
                    # Limitar a 10 productos
                    if len(recommended_products) >= 10:
                        break
            
            # Si no hay productos recomendados, retornar grupos sin cambios
            if not recommended_products:
                logger.info(f"No se encontraron productos con specialty {specialty}")
                return groups
            
            # Crear el grupo de recomendados
            recommendations_group = {
                "provider": "Recomendados",
                "products": recommended_products
            }
            
            # Insertar al inicio de la lista de grupos
            groups.insert(0, recommendations_group)
            logger.info(f"Grupo de recomendados agregado con {len(recommended_products)} productos")
            
            return groups
            
        except Exception as e:
            # Si hay cualquier error, simplemente retornar los grupos sin modificar
            logger.warning(f"Error al agregar grupo de recomendados: {str(e)}, retornando grupos normales")
            return groups
