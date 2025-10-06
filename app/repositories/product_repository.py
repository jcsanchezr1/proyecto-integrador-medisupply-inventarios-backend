from typing import List, Optional
from app.models.product import Product
from app.repositories.base_repository import BaseRepository

# Variables de clase a nivel de módulo para mantener estado entre instancias
_products_db = {}  # {sku: Product}
_products_by_id = {}  # {id: Product}
_next_id = 1


class ProductRepository(BaseRepository):
    """
    Repositorio para operaciones de productos en la base de datos
    """
    
    def __init__(self):
        # Base de datos en memoria para desarrollo/testing
        # En producción esto sería reemplazado por conexión real a PostgreSQL
        pass
    
    def create(self, product: Product) -> Product:
        """
        Crea un nuevo producto en la base de datos
        
        Args:
            product: Instancia del producto a crear
            
        Returns:
            Product: Producto creado con ID asignado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Asignar ID único
            global _next_id
            product.id = _next_id
            _next_id += 1
            
            # Guardar en base de datos en memoria
            _products_db[product.sku] = product
            _products_by_id[product.id] = product
            
            return product
        except Exception as e:
            raise Exception(f"Error al crear producto: {str(e)}")
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            return _products_by_id.get(product_id)
        except Exception as e:
            raise Exception(f"Error al obtener producto por ID: {str(e)}")
    
    def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Obtiene un producto por su SKU
        
        Args:
            sku: SKU del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            return _products_db.get(sku)
        except Exception as e:
            raise Exception(f"Error al obtener producto por SKU: {str(e)}")
    
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos
        
        Returns:
            List[Product]: Lista de todos los productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            return list(_products_by_id.values())
        except Exception as e:
            raise Exception(f"Error al obtener todos los productos: {str(e)}")
    
    def update(self, product: Product) -> Product:
        """
        Actualiza un producto existente
        
        Args:
            product: Producto con datos actualizados
            
        Returns:
            Product: Producto actualizado
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Actualizar en base de datos en memoria
            if product.id in _products_by_id:
                _products_by_id[product.id] = product
                _products_db[product.sku] = product
            
            return product
        except Exception as e:
            raise Exception(f"Error al actualizar producto: {str(e)}")
    
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            if product_id in _products_by_id:
                product = _products_by_id[product_id]
                del _products_by_id[product_id]
                del _products_db[product.sku]
                return True
            return False
        except Exception as e:
            raise Exception(f"Error al eliminar producto: {str(e)}")
    
    def delete_all(self) -> int:
        """
        Elimina todos los productos
        
        Returns:
            int: Número de productos eliminados
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            count = len(_products_by_id)
            _products_by_id.clear()
            _products_db.clear()
            return count
        except Exception as e:
            raise Exception(f"Error al eliminar todos los productos: {str(e)}")
    
    def count(self) -> int:
        """
        Cuenta el total de productos
        
        Returns:
            int: Número total de productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        try:
            return len(_products_by_id)
        except Exception as e:
            raise Exception(f"Error al contar productos: {str(e)}")
