from typing import Dict, List, Any
from collections import defaultdict
from app.services.product_service import ProductService
from app.external.provider_service import ProviderService
from app.exceptions.business_logic_error import BusinessLogicError


class ProviderProductsService:
    """
    Servicio para la lógica de negocio de productos agrupados por proveedor
    """
    
    def __init__(self, product_service=None, provider_service=None):
        self.product_service = product_service or ProductService()
        self.provider_service = provider_service or ProviderService()
    
    def get_products_grouped_by_provider(self) -> Dict[str, Any]:
        """
        Obtiene todos los productos agrupados por proveedor
        
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
        
        # Mapeo de meses en español
        MESES_ES = {
            1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR",
            5: "MAY", 6: "JUN", 7: "JUL", 8: "AGO",
            9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
        }
        
        products_by_provider = defaultdict(list)
        
        for product in products:
            provider_id = product.provider_id
            
            # Formatear fecha de expiración
            expiration_date_formatted = None
            if product.expiration_date:
                # Manejar tanto datetime como string
                date_obj = None
                if isinstance(product.expiration_date, datetime):
                    date_obj = product.expiration_date
                elif isinstance(product.expiration_date, str):
                    # Si es string, convertir a datetime primero
                    try:
                        date_obj = datetime.fromisoformat(product.expiration_date.replace('Z', '+00:00'))
                        # Convertir a naive si tiene timezone
                        if date_obj.tzinfo is not None:
                            date_obj = date_obj.replace(tzinfo=None)
                    except (ValueError, AttributeError):
                        # Si no se puede convertir, dejar como None
                        date_obj = None
                
                # Formatear con mes en español
                if date_obj:
                    mes_es = MESES_ES.get(date_obj.month, "")
                    expiration_date_formatted = f"{mes_es} {date_obj.day:02d}, {date_obj.year}"
            
            # Crear objeto de producto con campos adicionales
            product_data = {
                "id": product.id,
                "name": product.name,
                "quantity": product.quantity,
                "price": product.price,
                "photo_url": product.photo_url,
                "expiration_date": expiration_date_formatted,
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
