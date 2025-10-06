import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from app.services.product_service import ProductService
from app.models.product import Product
from app.exceptions.validation_error import ValidationError
from app.exceptions.business_logic_error import BusinessLogicError


class TestProductService:
    """Tests para ProductService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del ProductRepository"""
        return MagicMock()
    
    @pytest.fixture
    def product_service(self, mock_repository):
        """Instancia de ProductService con repository mockeado"""
        return ProductService(product_repository=mock_repository)
    
    @pytest.fixture
    def valid_product_data(self):
        """Datos válidos para crear un producto"""
        return {
            'sku': 'MED-1234',
            'name': 'Producto Test',
            'expiration_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
            'quantity': 100,
            'price': 15000.0,
            'location': 'A-01-01',
            'description': 'Producto de prueba',
            'product_type': 'Alto valor',
            'photo_filename': 'test.jpg'
        }
    
    def test_create_product_success(self, product_service, mock_repository, valid_product_data):
        """Test: Crear producto exitosamente"""
        # Mock del producto creado
        mock_product = MagicMock()
        mock_product.to_dict.return_value = {'id': 1, 'sku': 'MED-1234'}
        mock_repository.create.return_value = mock_product
        mock_repository.get_by_sku.return_value = None  # SKU no existe
        
        result = product_service.create_product(valid_product_data)
        
        assert result == mock_product
        mock_repository.get_by_sku.assert_called_once_with('MED-1234')
        mock_repository.create.assert_called_once()
    
    def test_create_product_validation_error_missing_fields(self, product_service, valid_product_data):
        """Test: Error de validación por campos faltantes"""
        del valid_product_data['sku']
        
        with pytest.raises(ValidationError, match="Campos requeridos faltantes"):
            product_service.create_product(valid_product_data)
    
    def test_create_product_validation_error_invalid_data(self, product_service, valid_product_data):
        """Test: Error de validación por datos inválidos"""
        valid_product_data['quantity'] = 'invalid'
        
        with pytest.raises(ValidationError, match="Error en conversión de tipos numéricos"):
            product_service.create_product(valid_product_data)
    
    def test_create_product_business_logic_error_duplicate_sku(self, product_service, mock_repository, valid_product_data):
        """Test: Error de lógica de negocio por SKU duplicado"""
        mock_repository.get_by_sku.return_value = MagicMock()  # SKU ya existe
        
        with pytest.raises(BusinessLogicError, match="El SKU ya existe en el sistema"):
            product_service.create_product(valid_product_data)
    
    def test_create_product_business_logic_error_repository_exception(self, product_service, mock_repository, valid_product_data):
        """Test: Error de lógica de negocio por excepción del repositorio"""
        mock_repository.get_by_sku.return_value = None
        mock_repository.create.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al crear producto"):
            product_service.create_product(valid_product_data)
    
    def test_get_product_by_id_success(self, product_service, mock_repository):
        """Test: Obtener producto por ID exitosamente"""
        mock_product = MagicMock()
        mock_repository.get_by_id.return_value = mock_product
        
        result = product_service.get_product_by_id(1)
        
        assert result == mock_product
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_product_by_id_not_found(self, product_service, mock_repository):
        """Test: Producto no encontrado por ID"""
        mock_repository.get_by_id.return_value = None
        
        result = product_service.get_product_by_id(1)
        
        assert result is None
    
    def test_get_product_by_id_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al obtener por ID"""
        mock_repository.get_by_id.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al obtener producto"):
            product_service.get_product_by_id(1)
    
    def test_get_product_by_sku_success(self, product_service, mock_repository):
        """Test: Obtener producto por SKU exitosamente"""
        mock_product = MagicMock()
        mock_repository.get_by_sku.return_value = mock_product
        
        result = product_service.get_product_by_sku('MED-1234')
        
        assert result == mock_product
        mock_repository.get_by_sku.assert_called_once_with('MED-1234')
    
    def test_get_product_by_sku_not_found(self, product_service, mock_repository):
        """Test: Producto no encontrado por SKU"""
        mock_repository.get_by_sku.return_value = None
        
        result = product_service.get_product_by_sku('MED-1234')
        
        assert result is None
    
    def test_get_product_by_sku_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al obtener por SKU"""
        mock_repository.get_by_sku.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al obtener producto por SKU"):
            product_service.get_product_by_sku('MED-1234')
    
    def test_get_all_products_success(self, product_service, mock_repository):
        """Test: Obtener todos los productos exitosamente"""
        mock_products = [MagicMock(), MagicMock()]
        mock_repository.get_all.return_value = mock_products
        
        result = product_service.get_all_products()
        
        assert result == mock_products
        mock_repository.get_all.assert_called_once()
    
    def test_get_all_products_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al obtener todos los productos"""
        mock_repository.get_all.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al obtener productos"):
            product_service.get_all_products()
    
    def test_get_products_summary_success(self, product_service, mock_repository):
        """Test: Obtener resumen de productos exitosamente"""
        mock_product1 = MagicMock()
        mock_product1.to_dict.return_value = {'id': 1, 'sku': 'MED-1234'}
        mock_product2 = MagicMock()
        mock_product2.to_dict.return_value = {'id': 2, 'sku': 'MED-5678'}
        
        mock_repository.get_all.return_value = [mock_product1, mock_product2]
        
        result = product_service.get_products_summary()
        
        assert len(result) == 2
        assert result[0] == {'id': 1, 'sku': 'MED-1234'}
        assert result[1] == {'id': 2, 'sku': 'MED-5678'}
        mock_repository.get_all.assert_called_once()
    
    def test_get_products_summary_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al obtener resumen"""
        mock_repository.get_all.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al obtener resumen de productos"):
            product_service.get_products_summary()
    
    def test_delete_product_success(self, product_service, mock_repository):
        """Test: Eliminar producto exitosamente"""
        mock_product = MagicMock()
        mock_repository.get_by_id.return_value = mock_product
        mock_repository.delete.return_value = True
        
        result = product_service.delete_product(1)
        
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(1)
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_product_not_found(self, product_service, mock_repository):
        """Test: Error al eliminar producto no encontrado"""
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(BusinessLogicError, match="Producto no encontrado"):
            product_service.delete_product(1)
    
    def test_delete_product_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al eliminar producto"""
        mock_repository.get_by_id.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al eliminar producto"):
            product_service.delete_product(1)
    
    def test_delete_all_products_success(self, product_service, mock_repository):
        """Test: Eliminar todos los productos exitosamente"""
        mock_repository.delete_all.return_value = 5
        
        result = product_service.delete_all_products()
        
        assert result == 5
        mock_repository.delete_all.assert_called_once()
    
    def test_delete_all_products_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al eliminar todos los productos"""
        mock_repository.delete_all.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al eliminar todos los productos"):
            product_service.delete_all_products()
    
    def test_get_products_count_success(self, product_service, mock_repository):
        """Test: Obtener conteo de productos exitosamente"""
        mock_repository.count.return_value = 10
        
        result = product_service.get_products_count()
        
        assert result == 10
        mock_repository.count.assert_called_once()
    
    def test_get_products_count_repository_exception(self, product_service, mock_repository):
        """Test: Excepción del repositorio al contar productos"""
        mock_repository.count.side_effect = Exception("Database error")
        
        with pytest.raises(BusinessLogicError, match="Error al contar productos"):
            product_service.get_products_count()
    
    def test_validate_required_fields_success(self, product_service, valid_product_data):
        """Test: Validación de campos requeridos exitosa"""
        # No debe lanzar excepción
        product_service._validate_required_fields(valid_product_data)
    
    def test_validate_required_fields_missing_single(self, product_service, valid_product_data):
        """Test: Validación con un campo faltante"""
        del valid_product_data['name']
        
        with pytest.raises(ValidationError, match="Campos requeridos faltantes: name"):
            product_service._validate_required_fields(valid_product_data)
    
    def test_validate_required_fields_missing_multiple(self, product_service, valid_product_data):
        """Test: Validación con múltiples campos faltantes"""
        del valid_product_data['sku']
        del valid_product_data['name']
        del valid_product_data['price']
        
        with pytest.raises(ValidationError, match="Campos requeridos faltantes: sku, name, price"):
            product_service._validate_required_fields(valid_product_data)
    
    def test_validate_required_fields_empty_values(self, product_service, valid_product_data):
        """Test: Validación con valores vacíos"""
        valid_product_data['sku'] = ''
        valid_product_data['name'] = None
        
        with pytest.raises(ValidationError, match="Campos requeridos faltantes: sku, name"):
            product_service._validate_required_fields(valid_product_data)
    
    def test_create_product_instance_success(self, product_service, valid_product_data):
        """Test: Crear instancia de producto exitosamente"""
        result = product_service._create_product_instance(valid_product_data)
        
        assert isinstance(result, Product)
        assert result.sku == 'MED-1234'
        assert result.name == 'Producto Test'
        assert result.quantity == 100
        assert result.price == 15000.0
    
    def test_create_product_instance_invalid_date_format(self, product_service, valid_product_data):
        """Test: Error al crear instancia con formato de fecha inválido"""
        valid_product_data['expiration_date'] = 'invalid-date'
        
        with pytest.raises(ValidationError, match="Formato de fecha de vencimiento inválido"):
            product_service._create_product_instance(valid_product_data)
    
    def test_create_product_instance_invalid_quantity_type(self, product_service, valid_product_data):
        """Test: Error al crear instancia con tipo de cantidad inválido"""
        valid_product_data['quantity'] = 'invalid'
        
        with pytest.raises(ValidationError, match="Error en conversión de tipos numéricos"):
            product_service._create_product_instance(valid_product_data)
    
    def test_create_product_instance_invalid_price_type(self, product_service, valid_product_data):
        """Test: Error al crear instancia con tipo de precio inválido"""
        valid_product_data['price'] = 'invalid'
        
        with pytest.raises(ValidationError, match="Error en conversión de tipos numéricos"):
            product_service._create_product_instance(valid_product_data)
    
    def test_validate_business_rules_duplicate_sku(self, product_service, mock_repository):
        """Test: Validación de reglas de negocio con SKU duplicado"""
        mock_product = MagicMock()
        mock_repository.get_by_sku.return_value = MagicMock()  # SKU existe
        
        with pytest.raises(BusinessLogicError, match="El SKU ya existe en el sistema"):
            product_service._validate_business_rules(mock_product)
    
    def test_validate_business_rules_valid_product(self, product_service, mock_repository):
        """Test: Validación de reglas de negocio con producto válido"""
        mock_product = MagicMock()
        mock_repository.get_by_sku.return_value = None  # SKU no existe
        
        # No debe lanzar excepción
        product_service._validate_business_rules(mock_product)
        
        mock_product.validate.assert_called_once()
    
    def test_process_photo_file_invalid_extension(self, product_service):
        """Test: Procesamiento de archivo con extensión inválida"""
        mock_file = MagicMock()
        mock_file.filename = "document.pdf"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024)
        
        with pytest.raises(ValidationError, match="El archivo debe ser una imagen válida"):
            product_service._process_photo_file(mock_file)
    
    def test_process_photo_file_empty_filename(self, product_service):
        """Test: Procesamiento de archivo con nombre vacío"""
        mock_file = MagicMock()
        mock_file.filename = "   "
        
        with pytest.raises(ValidationError, match="El campo 'Foto' debe aceptar únicamente archivos de imagen"):
            product_service._process_photo_file(mock_file)
    
    def test_process_photo_file_empty_file(self, product_service):
        """Test: Procesamiento de archivo vacío"""
        mock_file = MagicMock()
        mock_file.filename = "test.jpg"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=0)
        
        with pytest.raises(ValidationError, match="El archivo está vacío"):
            product_service._process_photo_file(mock_file)
    
    def test_process_photo_file_too_large(self, product_service):
        """Test: Procesamiento de archivo muy grande"""
        mock_file = MagicMock()
        mock_file.filename = "test.jpg"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=3 * 1024 * 1024)  # 3MB
        
        with pytest.raises(ValidationError, match="El archivo debe tener un tamaño máximo de 2MB"):
            product_service._process_photo_file(mock_file)
    
    def test_process_photo_file_valid_size(self, product_service):
        """Test: Procesamiento de archivo con tamaño válido"""
        mock_file = MagicMock()
        mock_file.filename = "test.jpg"
        mock_file.seek = MagicMock()
        mock_file.tell = MagicMock(return_value=1024 * 1024)  # 1MB
        
        result = product_service._process_photo_file(mock_file)
        assert result == "test.jpg"
        mock_file.seek.assert_any_call(0, 2)  # Verificar que se fue al final
        mock_file.seek.assert_any_call(0)    # Verificar que volvió al inicio
    
    def test_is_allowed_file_valid_extensions(self, product_service):
        """Test: Validación de extensiones permitidas"""
        assert product_service._is_allowed_file("test.jpg") is True
        assert product_service._is_allowed_file("test.jpeg") is True
        assert product_service._is_allowed_file("test.png") is True
        assert product_service._is_allowed_file("test.gif") is True
        assert product_service._is_allowed_file("TEST.JPG") is True  # Case insensitive
    
    def test_is_allowed_file_invalid_extensions(self, product_service):
        """Test: Validación de extensiones no permitidas"""
        assert product_service._is_allowed_file("test.pdf") is False
        assert product_service._is_allowed_file("test.doc") is False
        assert product_service._is_allowed_file("test.txt") is False
        assert product_service._is_allowed_file("test") is False  # Sin extensión
        assert product_service._is_allowed_file("") is False  # Nombre vacío
        assert product_service._is_allowed_file(None) is False  # None
