import pytest
from unittest.mock import Mock, patch
from app.services.provider_products_service import ProviderProductsService
from app.models.product import Product
from app.models.provider import Provider
from app.exceptions.business_logic_error import BusinessLogicError
from datetime import datetime, timedelta


class TestProviderProductsService:
    """Tests para el servicio de productos agrupados por proveedor"""
    
    @pytest.fixture
    def sample_products(self):
        """Productos de prueba"""
        future_date = datetime.utcnow() + timedelta(days=30)
        
        return [
            Product(
                sku="MED-0001",
                name="Paracetamol 500mg",
                expiration_date=future_date,
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Analgésico",
                product_type="Cadena de frío",
                provider_id="32892e80-fbf9-4c7f-b211-228b3aa43985"
            ),
            Product(
                sku="MED-0002",
                name="Ibuprofeno 400mg",
                expiration_date=future_date,
                quantity=50,
                price=8000.0,
                location="A-01-02",
                description="Antiinflamatorio",
                product_type="Seguridad",
                provider_id="32892e80-fbf9-4c7f-b211-228b3aa43985"
            ),
            Product(
                sku="MED-0003",
                name="Vitamina C",
                expiration_date=future_date,
                quantity=200,
                price=12000.0,
                location="B-02-01",
                description="Suplemento vitamínico",
                product_type="Alto valor",
                provider_id="12345678-1234-1234-1234-123456789012"
            )
        ]
    
    @pytest.fixture
    def mock_product_service(self, sample_products):
        """Mock del servicio de productos"""
        with patch('app.services.provider_products_service.ProductService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            service_instance.get_all_products.return_value = sample_products
            yield service_instance
    
    @pytest.fixture
    def mock_provider_service(self):
        """Mock del servicio de proveedores"""
        with patch('app.services.provider_products_service.ProviderService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            
            # Configurar respuestas del mock
            service_instance.get_providers_batch.return_value = {
                "32892e80-fbf9-4c7f-b211-228b3aa43985": Provider(
                    id="32892e80-fbf9-4c7f-b211-228b3aa43985",
                    name="Farmacia ABC",
                    email="abc@farmacia.com",
                    phone="1234567890"
                ),
                "12345678-1234-1234-1234-123456789012": Provider(
                    id="12345678-1234-1234-1234-123456789012",
                    name="Farmacia XYZ",
                    email="xyz@farmacia.com",
                    phone="0987654321"
                )
            }
            
            yield service_instance
    
    def test_get_products_grouped_by_provider_success(self, mock_product_service, mock_provider_service):
        """Test exitoso del servicio de productos agrupados por proveedor"""
        service = ProviderProductsService()
        result = service.get_products_grouped_by_provider()
        
        # Verificar estructura de respuesta
        assert "groups" in result
        assert "message" in result
        assert len(result["groups"]) == 2  # Dos proveedores únicos
        
        # Verificar que se llamó al servicio de productos
        mock_product_service.get_all_products.assert_called_once()
        
        # Verificar que se llamó al servicio de proveedores
        mock_provider_service.get_providers_batch.assert_called_once()
        
        # Verificar estructura de grupos
        for group in result["groups"]:
            assert "provider" in group
            assert "products" in group
            assert isinstance(group["products"], list)
            assert len(group["products"]) > 0
            
            # Verificar estructura de productos
            for product in group["products"]:
                assert "name" in product
                assert "quantity" in product
                assert "price" in product
    
    def test_get_products_grouped_by_provider_empty(self, mock_provider_service):
        """Test cuando no hay productos"""
        with patch('app.services.provider_products_service.ProductService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            service_instance.get_all_products.return_value = []
            
            service = ProviderProductsService()
            result = service.get_products_grouped_by_provider()
            
            assert result["groups"] == []
            assert result["message"] == "No hay productos registrados"
    
    def test_get_products_grouped_by_provider_provider_service_error(self, mock_product_service):
        """Test cuando falla el servicio de proveedores"""
        with patch('app.services.provider_products_service.ProviderService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            service_instance.get_providers_batch.side_effect = Exception("Error de conexión")
            service_instance.get_provider_name.return_value = "Proveedor no asociado"
            
            service = ProviderProductsService()
            result = service.get_products_grouped_by_provider()
            
            # Verificar que se retorna resultado con "Proveedor no asociado"
            assert "groups" in result
            for group in result["groups"]:
                assert group["provider"] == "Proveedor no asociado"
    
    def test_group_products_by_provider(self, mock_provider_service):
        """Test del método de agrupación de productos"""
        service = ProviderProductsService()
        
        # Crear productos de prueba
        future_date = datetime.utcnow() + timedelta(days=30)
        products = [
            Product(
                sku="MED-0001",
                name="Producto 1",
                expiration_date=future_date,
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Test",
                product_type="Cadena de frío",
                provider_id="provider-1"
            ),
            Product(
                sku="MED-0002",
                name="Producto 2",
                expiration_date=future_date,
                quantity=50,
                price=8000.0,
                location="A-01-02",
                description="Test",
                product_type="Seguridad",
                provider_id="provider-1"
            ),
            Product(
                sku="MED-0003",
                name="Producto 3",
                expiration_date=future_date,
                quantity=200,
                price=12000.0,
                location="B-02-01",
                description="Test",
                product_type="Alto valor",
                provider_id="provider-2"
            )
        ]
        
        # Llamar al método privado usando reflection
        grouped = service._group_products_by_provider(products)
        
        # Verificar agrupación
        assert len(grouped) == 2  # Dos proveedores únicos
        assert "provider-1" in grouped
        assert "provider-2" in grouped
        assert len(grouped["provider-1"]) == 2  # Dos productos del proveedor 1
        assert len(grouped["provider-2"]) == 1  # Un producto del proveedor 2
        
        # Verificar estructura de productos con nuevos campos
        for provider_id, products_list in grouped.items():
            for product in products_list:
                # Campos existentes
                assert "name" in product
                assert "quantity" in product
                assert "price" in product
                assert isinstance(product["quantity"], int)
                assert isinstance(product["price"], (int, float))
                
                # Nuevos campos
                assert "id" in product
                assert "expiration_date" in product
                assert "description" in product
                assert "photo_url" in product
    
    def test_get_provider_names_efficiently(self, mock_product_service):
        """Test del método de obtención eficiente de nombres de proveedores"""
        service = ProviderProductsService()
        
        # Mock del servicio de proveedores
        with patch.object(service, 'provider_service') as mock_provider:
            mock_provider.get_providers_batch.return_value = {
                "provider-1": Provider(id="provider-1", name="Proveedor 1", email="test1@test.com", phone="123"),
                "provider-2": Provider(id="provider-2", name="Proveedor 2", email="test2@test.com", phone="456")
            }
            
            provider_ids = ["provider-1", "provider-2"]
            result = service._get_provider_names_efficiently(provider_ids)
            
            assert result["provider-1"] == "Proveedor 1"
            assert result["provider-2"] == "Proveedor 2"
            mock_provider.get_providers_batch.assert_called_once_with(provider_ids)
    
    def test_get_provider_names_efficiently_with_errors(self, mock_product_service):
        """Test del método de obtención de nombres con errores"""
        service = ProviderProductsService()
        
        # Mock del servicio de proveedores que falla
        with patch.object(service, 'provider_service') as mock_provider:
            mock_provider.get_providers_batch.side_effect = Exception("Error de conexión")
            mock_provider.get_provider_name.return_value = "Proveedor no asociado"
            
            provider_ids = ["provider-1", "provider-2"]
            result = service._get_provider_names_efficiently(provider_ids)
            
            # Debe retornar "Proveedor no asociado" para todos
            assert result["provider-1"] == "Proveedor no asociado"
            assert result["provider-2"] == "Proveedor no asociado"
    
    def test_build_groups_response(self, mock_product_service, mock_provider_service):
        """Test del método de construcción de respuesta de grupos"""
        service = ProviderProductsService()
        
        products_by_provider = {
            "provider-1": [
                {"name": "Producto 1", "quantity": 100, "price": 5000.0},
                {"name": "Producto 2", "quantity": 50, "price": 8000.0}
            ],
            "provider-2": [
                {"name": "Producto 3", "quantity": 200, "price": 12000.0}
            ]
        }
        
        provider_names = {
            "provider-1": "Proveedor 1",
            "provider-2": "Proveedor 2"
        }
        
        result = service._build_groups_response(products_by_provider, provider_names)
        
        assert len(result) == 2
        
        # Verificar primer grupo
        group1 = result[0]
        assert group1["provider"] in ["Proveedor 1", "Proveedor 2"]
        assert len(group1["products"]) in [1, 2]  # Depende del orden
        
        # Verificar estructura de cada grupo
        for group in result:
            assert "provider" in group
            assert "products" in group
            assert isinstance(group["products"], list)
            assert len(group["products"]) > 0
    
    def test_service_exception_handling(self, mock_provider_service):
        """Test de manejo de excepciones en el servicio"""
        with patch('app.services.provider_products_service.ProductService') as mock:
            service_instance = Mock()
            mock.return_value = service_instance
            service_instance.get_all_products.side_effect = Exception("Error en base de datos")
            
            service = ProviderProductsService()
            
            with pytest.raises(BusinessLogicError) as exc_info:
                service.get_products_grouped_by_provider()
            
            assert "Error al obtener productos agrupados por proveedor" in str(exc_info.value)
    
    def test_expiration_date_format(self, mock_provider_service):
        """Test que verifica que la fecha de expiración se devuelve en formato ISO"""
        service = ProviderProductsService()
        
        # Crear una fecha específica para probar el formato
        test_date = datetime(2025, 10, 23)  # 23 de octubre de 2025
        
        products = [
            Product(
                sku="MED-0001",
                name="Producto Test",
                expiration_date=test_date,
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Producto de prueba",
                product_type="Cadena de frío",
                provider_id="provider-1"
            )
        ]
        
        # Llamar al método privado
        grouped = service._group_products_by_provider(products)
        
        # Obtener el producto del resultado
        product = grouped["provider-1"][0]
        
        # Verificar que la fecha se devuelve en formato ISO
        assert product["expiration_date"] == "2025-10-23T00:00:00", \
            f"El formato de fecha debe ser ISO (YYYY-MM-DDTHH:MM:SS), pero se obtuvo: {product['expiration_date']}"
        
        # Verificar que es un string
        assert isinstance(product["expiration_date"], str), \
            "La fecha debe ser un string en formato ISO"
    
    def test_expiration_date_none(self, mock_provider_service):
        """Test que verifica el manejo de fecha de expiración nula"""
        service = ProviderProductsService()
        
        products = [
            Product(
                sku="MED-0001",
                name="Producto Test",
                expiration_date=None,
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Producto de prueba",
                product_type="Cadena de frío",
                provider_id="provider-1"
            )
        ]
        
        # Llamar al método privado
        grouped = service._group_products_by_provider(products)
        
        # Obtener el producto del resultado
        product = grouped["provider-1"][0]
        
        # Verificar que la fecha es None cuando no existe
        assert product["expiration_date"] is None, \
            "La fecha de expiración debe ser None cuando el producto no tiene fecha"
    
    def test_expiration_date_as_string(self, mock_provider_service):
        """Test que verifica el manejo de fecha de expiración cuando viene como string desde la BD"""
        service = ProviderProductsService()
        
        # Crear un producto con fecha como string (como viene de la base de datos)
        test_date_str = "2025-10-23T00:00:00"
        
        products = [
            Product(
                sku="MED-0001",
                name="Producto Test",
                expiration_date=datetime(2025, 10, 23),  # Lo creamos con datetime para que pase la validación
                quantity=100,
                price=5000.0,
                location="A-01-01",
                description="Producto de prueba",
                product_type="Cadena de frío",
                provider_id="provider-1"
            )
        ]
        
        # Simular que la fecha viene como string desde la BD
        products[0].expiration_date = test_date_str
        
        # Llamar al método privado
        grouped = service._group_products_by_provider(products)
        
        # Obtener el producto del resultado
        product = grouped["provider-1"][0]
        
        # Verificar que la fecha se mantiene como string (como viene de BD)
        assert product["expiration_date"] == test_date_str, \
            f"La fecha debe mantenerse como viene de BD: '{test_date_str}', pero se obtuvo: {product['expiration_date']}"
        
        # Verificar que es un string
        assert isinstance(product["expiration_date"], str), \
            "La fecha debe ser un string"
    
    def test_consolidate_products_with_same_provider_name(self):
        """Test que verifica que productos con diferentes provider_id pero mismo nombre de proveedor se consolidan en un solo grupo"""
        # Crear productos de prueba con diferentes provider_id que mapean a "Proveedor no asociado"
        future_date = datetime.utcnow() + timedelta(days=30)
        
        with patch('app.services.provider_products_service.ProductService') as mock_product:
            with patch('app.services.provider_products_service.ProviderService') as mock_provider:
                # Configurar productos con diferentes provider_id
                products = [
                    Product(
                        sku="MED-0001",
                        name="Paracetamol 500mg",
                        expiration_date=future_date,
                        quantity=150,
                        price=5500.0,
                        location="A-01-01",
                        description="Test",
                        product_type="Cadena de frío",
                        provider_id=None  # Sin proveedor
                    ),
                    Product(
                        sku="MED-0002",
                        name="Amoxicilina 500mg",
                        expiration_date=future_date,
                        quantity=200,
                        price=12500.0,
                        location="A-01-02",
                        description="Test",
                        product_type="Seguridad",
                        provider_id=""  # Proveedor vacío
                    ),
                    Product(
                        sku="MED-0003",
                        name="Insulina Glargina",
                        expiration_date=future_date,
                        quantity=75,
                        price=85000.0,
                        location="B-01-01",
                        description="Test",
                        product_type="Alto valor",
                        provider_id="non-existent-id"  # Proveedor que no existe
                    )
                ]
                
                # Configurar mocks
                product_service_instance = Mock()
                mock_product.return_value = product_service_instance
                product_service_instance.get_all_products.return_value = products
                
                provider_service_instance = Mock()
                mock_provider.return_value = provider_service_instance
                # Simular que ninguno de los provider_id tiene proveedor asociado
                provider_service_instance.get_providers_batch.return_value = {
                    None: None,
                    "": None,
                    "non-existent-id": None
                }
                
                # Ejecutar servicio
                service = ProviderProductsService()
                result = service.get_products_grouped_by_provider()
                
                # Verificar que solo hay UN grupo con "Proveedor no asociado"
                assert len(result["groups"]) == 1, f"Se esperaba 1 grupo, pero se obtuvieron {len(result['groups'])}"
                
                # Verificar que el grupo tiene el nombre correcto
                assert result["groups"][0]["provider"] == "Proveedor no asociado"
                
                # Verificar que todos los productos están en ese único grupo
                assert len(result["groups"][0]["products"]) == 3, f"Se esperaban 3 productos consolidados, pero se obtuvieron {len(result['groups'][0]['products'])}"
                
                # Verificar que los productos son los correctos
                product_names = [p["name"] for p in result["groups"][0]["products"]]
                assert "Paracetamol 500mg" in product_names
                assert "Amoxicilina 500mg" in product_names
                assert "Insulina Glargina" in product_names