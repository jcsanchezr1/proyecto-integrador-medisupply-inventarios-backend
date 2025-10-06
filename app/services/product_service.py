from typing import List, Optional, Dict, Any
from datetime import datetime
from werkzeug.datastructures import FileStorage
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class ProductService:
    """
    Servicio para la lógica de negocio de productos
    """
    
    def __init__(self, product_repository=None):
        self.product_repository = product_repository or ProductRepository()
    
    def create_product(self, product_data: Dict[str, Any], photo_file: Optional[FileStorage] = None) -> Product:
        """
        Crea un nuevo producto con validaciones de negocio
        
        Args:
            product_data: Diccionario con los datos del producto
            photo_file: Archivo de foto del producto (opcional)
            
        Returns:
            Product: Producto creado
            
        Raises:
            ValidationError: Si hay errores de validación
            BusinessLogicError: Si hay errores de lógica de negocio
        """
        try:
            # Validar datos requeridos
            self._validate_required_fields(product_data)
            
            # Procesar archivo de foto si se proporciona
            if photo_file is not None:
                photo_filename = self._process_photo_file(photo_file)
                if photo_filename:
                    product_data['photo_filename'] = photo_filename
            
            # Crear instancia del producto
            product = self._create_product_instance(product_data)
            
            # Validar reglas de negocio
            self._validate_business_rules(product)
            
            # Crear producto en el repositorio
            created_product = self.product_repository.create(product)
            
            return created_product
            
        except ValidationError:
            raise
        except BusinessLogicError:
            raise
        except Exception as e:
            raise BusinessLogicError(f"Error al crear producto: {str(e)}")
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            product_id: ID del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.get_by_id(product_id)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener producto: {str(e)}")
    
    def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """
        Obtiene un producto por su SKU
        
        Args:
            sku: SKU del producto
            
        Returns:
            Optional[Product]: Producto encontrado o None
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.get_by_sku(sku)
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener producto por SKU: {str(e)}")
    
    def get_all_products(self) -> List[Product]:
        """
        Obtiene todos los productos
        
        Returns:
            List[Product]: Lista de todos los productos
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.get_all()
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener productos: {str(e)}")
    
    def get_products_summary(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de todos los productos para listado
        
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con datos básicos de productos
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            products = self.product_repository.get_all()
            return [product.to_dict() for product in products]
        except Exception as e:
            raise BusinessLogicError(f"Error al obtener resumen de productos: {str(e)}")
    
    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID
        
        Args:
            product_id: ID del producto a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            # Verificar que el producto existe
            product = self.product_repository.get_by_id(product_id)
            if not product:
                raise BusinessLogicError("Producto no encontrado")
            
            return self.product_repository.delete(product_id)
        except BusinessLogicError:
            raise
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar producto: {str(e)}")
    
    def delete_all_products(self) -> int:
        """
        Elimina todos los productos
        
        Returns:
            int: Número de productos eliminados
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.delete_all()
        except Exception as e:
            raise BusinessLogicError(f"Error al eliminar todos los productos: {str(e)}")
    
    def get_products_count(self) -> int:
        """
        Obtiene el número total de productos
        
        Returns:
            int: Número total de productos
            
        Raises:
            BusinessLogicError: Si hay error en la operación
        """
        try:
            return self.product_repository.count()
        except Exception as e:
            raise BusinessLogicError(f"Error al contar productos: {str(e)}")
    
    def _validate_required_fields(self, product_data: Dict[str, Any]) -> None:
        """
        Valida que todos los campos requeridos estén presentes
        
        Args:
            product_data: Diccionario con los datos del producto
            
        Raises:
            ValidationError: Si faltan campos requeridos
        """
        required_fields = [
            'sku', 'name', 'expiration_date', 'quantity', 
            'price', 'location', 'description', 'product_type'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in product_data or product_data[field] is None or product_data[field] == '':
                missing_fields.append(field)
        
        if missing_fields:
            raise ValidationError(f"Campos requeridos faltantes: {', '.join(missing_fields)}")
    
    def _create_product_instance(self, product_data: Dict[str, Any]) -> Product:
        """
        Crea una instancia de Product a partir de los datos
        
        Args:
            product_data: Diccionario con los datos del producto
            
        Returns:
            Product: Instancia del producto
            
        Raises:
            ValidationError: Si hay error en la conversión de datos
        """
        try:
            # Convertir todos los tipos de datos antes de crear el objeto
            sku = str(product_data['sku'])
            name = str(product_data['name'])
            
            # Convertir fecha de vencimiento
            expiration_date = product_data['expiration_date']
            if isinstance(expiration_date, str):
                try:
                    expiration_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                except ValueError:
                    raise ValidationError("Formato de fecha de vencimiento inválido")
            elif not isinstance(expiration_date, datetime):
                raise ValidationError("La fecha de vencimiento debe ser un datetime o string válido")
            
            # Convertir cantidad y precio
            try:
                quantity = int(product_data['quantity'])
                price = float(product_data['price'])
            except (ValueError, TypeError) as e:
                raise ValidationError(f"Error en conversión de tipos numéricos: {str(e)}")
            
            location = str(product_data['location'])
            description = str(product_data['description'])
            product_type = str(product_data['product_type'])
            photo_filename = str(product_data.get('photo_filename')) if product_data.get('photo_filename') else None
            
            return Product(
                sku=sku,
                name=name,
                expiration_date=expiration_date,
                quantity=quantity,
                price=price,
                location=location,
                description=description,
                product_type=product_type,
                photo_filename=photo_filename
            )
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Error en formato de datos: {str(e)}")
    
    def _validate_business_rules(self, product: Product) -> None:
        """
        Valida reglas de negocio específicas
        
        Args:
            product: Instancia del producto a validar
            
        Raises:
            BusinessLogicError: Si hay violación de reglas de negocio
        """
        # Validar que el SKU sea único
        existing_product = self.product_repository.get_by_sku(product.sku)
        if existing_product:
            raise BusinessLogicError("El SKU ya existe en el sistema. Utilice un SKU único.")
        
        # Validar que el producto sea válido según el modelo
        product.validate()
    
    def _process_photo_file(self, photo_file: Optional[FileStorage]) -> Optional[str]:
        """
        Procesa el archivo de foto y retorna el nombre del archivo
        
        Args:
            photo_file: Archivo de foto del producto
            
        Returns:
            Optional[str]: Nombre del archivo procesado o None
            
        Raises:
            ValidationError: Si hay error en el archivo
        """
        if not photo_file or not photo_file.filename:
            return None
        
        # Validar que el archivo tenga nombre
        if not photo_file.filename.strip():
            raise ValidationError("El campo 'Foto' debe aceptar únicamente archivos de imagen (JPG, PNG, GIF) con un tamaño máximo de 2MB")
        
        # Validar tipo de archivo (JPG, PNG, GIF)
        if not self._is_allowed_file(photo_file.filename):
            raise ValidationError("El archivo debe ser una imagen válida (JPG, PNG, GIF)")
        
        # Validar tamaño del archivo (2MB máximo)
        photo_file.seek(0, 2)  # Ir al final del archivo
        file_size = photo_file.tell()
        photo_file.seek(0)  # Volver al inicio
        
        if file_size == 0:
            raise ValidationError("El archivo está vacío")
        
        if file_size > 2 * 1024 * 1024:  # 2MB en bytes
            raise ValidationError("El archivo debe tener un tamaño máximo de 2MB")
        
        # TODO: Implementar guardado en bucket S3/Azure Storage
        # Por ahora retornamos el nombre del archivo original
        # En implementación real: 
        # - Generar nombre único para el archivo
        # - Subir archivo al bucket
        # - Retornar URL o nombre del archivo en el bucket
        
        return photo_file.filename
    
    def _is_allowed_file(self, filename: str) -> bool:
        """
        Verifica si el archivo está permitido
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si el archivo está permitido
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.lower().split('.')[-1]
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
        
        return extension in allowed_extensions
