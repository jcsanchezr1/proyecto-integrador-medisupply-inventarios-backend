import pytest
from datetime import datetime, timedelta
from app.models.product import Product


class TestProduct:
    """Tests para el modelo Product"""
    
    @pytest.fixture
    def valid_product_data(self):
        """Datos válidos para crear un producto"""
        return {
            'sku': 'MED-1234',
            'name': 'Producto Test',
            'expiration_date': datetime.utcnow() + timedelta(days=30),
            'quantity': 100,
            'price': 15000.0,
            'location': 'A-01-01',
            'description': 'Producto de prueba',
            'product_type': 'Alto valor',
            'provider_id': '550e8400-e29b-41d4-a716-446655440000',
            'photo_filename': 'test.jpg'
        }
    
    def test_create_product_with_valid_data(self, valid_product_data):
        """Test: Crear producto con datos válidos"""
        product = Product(**valid_product_data)
        
        assert product.sku == 'MED-1234'
        assert product.name == 'Producto Test'
        assert product.quantity == 100
        assert product.price == 15000.0
        assert product.location == 'A-01-01'
        assert product.description == 'Producto de prueba'
        assert product.product_type == 'Alto valor'
        assert product.provider_id == '550e8400-e29b-41d4-a716-446655440000'
        assert product.photo_filename == 'test.jpg'
        assert product.created_at is not None
        assert product.updated_at is not None
    
    def test_create_product_without_photo(self, valid_product_data):
        """Test: Crear producto sin foto"""
        del valid_product_data['photo_filename']
        product = Product(**valid_product_data)
        
        assert product.photo_filename is None
    
    def test_validate_sku_valid(self, valid_product_data):
        """Test: Validar SKU válido"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_sku_empty(self, valid_product_data):
        """Test: Validar SKU vacío"""
        valid_product_data['sku'] = ''
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El SKU es obligatorio"):
            product.validate()
    
    def test_validate_sku_invalid_format(self, valid_product_data):
        """Test: Validar SKU con formato inválido"""
        test_cases = ['MED-123', 'MED-12345', 'ABC-1234', 'med-1234', 'MED-ABCD']
        
        for invalid_sku in test_cases:
            valid_product_data['sku'] = invalid_sku
            product = Product(**valid_product_data)
            
            with pytest.raises(ValueError, match="El SKU debe seguir el formato MED-XXXX"):
                product.validate()
    
    def test_validate_name_valid(self, valid_product_data):
        """Test: Validar nombre válido"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_name_empty(self, valid_product_data):
        """Test: Validar nombre vacío"""
        valid_product_data['name'] = ''
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El nombre es obligatorio"):
            product.validate()
    
    def test_validate_name_too_short(self, valid_product_data):
        """Test: Validar nombre muy corto"""
        valid_product_data['name'] = 'AB'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El nombre debe tener al menos 3 caracteres"):
            product.validate()
    
    def test_validate_name_invalid_characters(self, valid_product_data):
        """Test: Validar nombre con caracteres inválidos"""
        test_cases = ['Product@', 'Product#', 'Product$', 'Product%']
        
        for invalid_name in test_cases:
            valid_product_data['name'] = invalid_name
            product = Product(**valid_product_data)
            
            with pytest.raises(ValueError, match="El nombre debe contener únicamente caracteres alfanuméricos y espacios"):
                product.validate()
    
    def test_validate_expiration_date_valid(self, valid_product_data):
        """Test: Validar fecha de vencimiento válida"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_expiration_date_past(self, valid_product_data):
        """Test: Validar fecha de vencimiento pasada"""
        valid_product_data['expiration_date'] = datetime.utcnow() - timedelta(days=1)
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="La fecha de vencimiento debe ser posterior a la fecha actual"):
            product.validate()
    
    def test_validate_expiration_date_string(self, valid_product_data):
        """Test: Validar fecha de vencimiento como string"""
        future_date = datetime.utcnow() + timedelta(days=30)
        valid_product_data['expiration_date'] = future_date.isoformat()
        product = Product(**valid_product_data)
        
        product.validate()  # No debe lanzar excepción
        assert isinstance(product.expiration_date, datetime)
    
    def test_validate_expiration_date_invalid_string(self, valid_product_data):
        """Test: Validar fecha de vencimiento con string inválido"""
        valid_product_data['expiration_date'] = 'invalid-date'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="Formato de fecha inválido"):
            product.validate()
    
    def test_validate_quantity_valid(self, valid_product_data):
        """Test: Validar cantidad válida"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_quantity_invalid_type(self, valid_product_data):
        """Test: Validar cantidad con tipo inválido"""
        valid_product_data['quantity'] = '100'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="La cantidad debe ser un número entero"):
            product.validate()
    
    def test_validate_quantity_out_of_range(self, valid_product_data):
        """Test: Validar cantidad fuera de rango"""
        test_cases = [0, -1, 10000]
        
        for invalid_quantity in test_cases:
            valid_product_data['quantity'] = invalid_quantity
            product = Product(**valid_product_data)
            
            with pytest.raises(ValueError, match="La cantidad debe estar entre 1 y 9999"):
                product.validate()
    
    def test_validate_price_valid(self, valid_product_data):
        """Test: Validar precio válido"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_price_invalid_type(self, valid_product_data):
        """Test: Validar precio con tipo inválido"""
        valid_product_data['price'] = '15000'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El precio debe ser un valor numérico"):
            product.validate()
    
    def test_validate_price_negative(self, valid_product_data):
        """Test: Validar precio negativo"""
        valid_product_data['price'] = -1000
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El precio debe ser un valor positivo"):
            product.validate()
    
    def test_validate_location_valid(self, valid_product_data):
        """Test: Validar ubicación válida"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_location_empty(self, valid_product_data):
        """Test: Validar ubicación vacía"""
        valid_product_data['location'] = ''
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="La ubicación es obligatoria"):
            product.validate()
    
    def test_validate_location_invalid_format(self, valid_product_data):
        """Test: Validar ubicación con formato inválido"""
        test_cases = ['A-1-1', 'A-001-001', '1-01-01', 'A-01-1', 'a-01-01']
        
        for invalid_location in test_cases:
            valid_product_data['location'] = invalid_location
            product = Product(**valid_product_data)
            
            with pytest.raises(ValueError, match="La ubicación debe seguir el formato P-EE-NN"):
                product.validate()
    
    def test_validate_product_type_valid(self, valid_product_data):
        """Test: Validar tipo de producto válido"""
        valid_types = ["Alto valor", "Seguridad", "Cadena fría"]
        
        for product_type in valid_types:
            valid_product_data['product_type'] = product_type
            product = Product(**valid_product_data)
            product.validate()  # No debe lanzar excepción
    
    def test_validate_product_type_invalid(self, valid_product_data):
        """Test: Validar tipo de producto inválido"""
        valid_product_data['product_type'] = 'Tipo inválido'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El tipo de producto debe ser: Alto valor, Seguridad o Cadena fría"):
            product.validate()
    
    def test_validate_product_type_empty(self, valid_product_data):
        """Test: Validar tipo de producto vacío"""
        valid_product_data['product_type'] = ''
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El tipo de producto es obligatorio"):
            product.validate()
    
    def test_validate_provider_id_valid(self, valid_product_data):
        """Test: Validar provider_id válido"""
        product = Product(**valid_product_data)
        product.validate()  # No debe lanzar excepción
    
    def test_validate_provider_id_invalid_type(self, valid_product_data):
        """Test: Validar provider_id con tipo inválido"""
        valid_product_data['provider_id'] = 123
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El ID del proveedor debe ser un string"):
            product.validate()
    
    def test_validate_provider_id_invalid_uuid_format(self, valid_product_data):
        """Test: Validar provider_id con formato UUID inválido"""
        valid_product_data['provider_id'] = 'invalid-uuid'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El ID del proveedor debe ser un UUID válido"):
            product.validate()
    
    def test_validate_provider_id_empty(self, valid_product_data):
        """Test: Validar provider_id vacío"""
        valid_product_data['provider_id'] = ''
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El ID del proveedor es obligatorio"):
            product.validate()
    
    def test_validate_provider_id_none(self, valid_product_data):
        """Test: Validar provider_id None"""
        valid_product_data['provider_id'] = None
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="El ID del proveedor es obligatorio"):
            product.validate()
    
    def test_validate_photo_filename_valid(self, valid_product_data):
        """Test: Validar nombre de archivo de foto válido"""
        valid_extensions = ['test.jpg', 'test.jpeg', 'test.png', 'test.gif', 'TEST.JPG']
        
        for filename in valid_extensions:
            valid_product_data['photo_filename'] = filename
            product = Product(**valid_product_data)
            product.validate()  # No debe lanzar excepción
    
    def test_validate_photo_filename_invalid_extension(self, valid_product_data):
        """Test: Validar nombre de archivo con extensión inválida"""
        valid_product_data['photo_filename'] = 'test.pdf'
        product = Product(**valid_product_data)
        
        with pytest.raises(ValueError, match="La foto debe ser un archivo JPG, PNG o GIF"):
            product.validate()
    
    def test_to_dict(self, valid_product_data):
        """Test: Convertir producto a diccionario"""
        product = Product(**valid_product_data)
        product_dict = product.to_dict()
        
        assert isinstance(product_dict, dict)
        assert product_dict['sku'] == 'MED-1234'
        assert product_dict['name'] == 'Producto Test'
        assert product_dict['quantity'] == 100
        assert product_dict['price'] == 15000.0
        assert product_dict['location'] == 'A-01-01'
        assert product_dict['description'] == 'Producto de prueba'
        assert product_dict['product_type'] == 'Alto valor'
        assert product_dict['provider_id'] == '550e8400-e29b-41d4-a716-446655440000'
        assert product_dict['photo_filename'] == 'test.jpg'
        assert 'created_at' in product_dict
        assert 'updated_at' in product_dict
    
    def test_to_dict_with_datetime_conversion(self, valid_product_data):
        """Test: Conversión de datetime a string en to_dict"""
        product = Product(**valid_product_data)
        product_dict = product.to_dict()
        
        assert isinstance(product_dict['expiration_date'], str)
        assert isinstance(product_dict['created_at'], str)
        assert isinstance(product_dict['updated_at'], str)
    
    def test_repr(self, valid_product_data):
        """Test: Representación string del producto"""
        product = Product(**valid_product_data)
        repr_str = repr(product)
        
        assert 'Product' in repr_str
        assert 'MED-1234' in repr_str
        assert 'Producto Test' in repr_str
        assert '100' in repr_str
