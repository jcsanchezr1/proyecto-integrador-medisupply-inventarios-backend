# MediSupply Inventory Backend

Sistema de inventarios backend para el proyecto integrador MediSupply.

## Arquitectura

Estructura básica preparada para escalar:

```
├── app/
│   ├── config/          # Configuración
│   ├── controllers/     # Controladores REST
│   │   └── health_controller.py  # Healthcheck funcional
│   ├── services/        # Lógica de negocio (estructura)
│   ├── repositories/    # Acceso a datos (estructura)
│   ├── models/          # Modelos de datos (estructura)
│   ├── exceptions/      # Excepciones (estructura)
│   └── utils/           # Utilidades (estructura)
├── tests/               # Tests (estructura)
├── app.py              # Punto de entrada
├── requirements.txt    # Dependencias del proyecto
├── Dockerfile         # Containerización
└── README.md          # Documentación
```

## Características

- **Health Check**: Endpoint de monitoreo del servicio
- **Docker**: Containerización para local y Cloud Run
- **Flask**: Framework web minimalista
- **CORS**: Habilitado para desarrollo

## Tecnologías

- Python 3.11
- Flask 3.0.3
- Flask-RESTful 0.3.10
- SQLAlchemy 2.0.23
- PostgreSQL (psycopg2-binary)
- Gunicorn 21.2.0
- Docker
- pytest 8.3.4

## Instalación

### Desarrollo Local

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar base de datos PostgreSQL:**
   ```bash
   # Asegúrate de que PostgreSQL esté ejecutándose
   # Crear base de datos y usuario (opcional, se crea automáticamente)
   createdb medisupply_local_db
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```

4. **La aplicación estará disponible en:** `http://localhost:8080`

### Con Docker

1. **Usar docker-compose desde el directorio de infraestructura:**
   ```bash
   cd ../proyecto-integrador-medisupply-infraestructura
   docker-compose up --build
   ```

2. **La aplicación estará disponible en:** `http://localhost:8084`

3. **Verificar que todos los servicios estén ejecutándose:**
   ```bash
   docker-compose ps
   ```

## Endpoints

### Health Check
- `GET /inventory/ping` - Ping simple

### Productos
- `GET /inventory/products` - Obtener todos los productos (con paginación)
- `GET /inventory/products/filter` - Filtrar productos con criterios específicos
- `GET /inventory/products/{id}` - Obtener producto por ID
- `POST /inventory/products` - Crear nuevo producto
- `PUT /inventory/products/{id}/stock` - Actualizar stock de un producto
- `DELETE /inventory/products/{id}` - Eliminar producto por ID
- `DELETE /inventory/products/delete-all` - Eliminar todos los productos

## Respuesta del Health Check

```json
"pong"
```

## Estructura de Producto

```json
{
  "sku": "MED-1234",
  "name": "Paracetamol 500mg",
  "expiration_date": "2025-12-31T00:00:00.000Z",
  "quantity": 100,
  "price": 15000.0,
  "location": "A-01-01",
  "description": "Analgésico y antipirético",
  "product_type": "Alto valor",
  "photo_filename": "product_uuid.png",
  "photo_url": "https://storage.googleapis.com/medisupply-images-bucket/products/product_uuid.png?Expires=...&GoogleAccessId=...&Signature=..."
}
```

### Validaciones de Producto

- **SKU**: Formato "MED-XXXX" (4 dígitos numéricos), único
- **Nombre**: Alfanumérico, espacios y tildes, mínimo 3 caracteres
- **Fecha de vencimiento**: Debe ser futura
- **Cantidad**: Entero positivo (1-9999)
- **Precio**: Numérico positivo en COP
- **Ubicación**: Formato "P-EE-NN" (Pasillo: A-Z, Estante: 01-99, Nivel: 01-99)
- **Tipo de producto**: "Alto valor", "Seguridad", "Cadena fría"
- **Foto**: JPG, PNG, GIF, máximo 5MB (opcional)

## Almacenamiento de Imágenes

### Google Cloud Storage
El servicio utiliza Google Cloud Storage para almacenar las fotos de los productos:

- **Bucket**: `medisupply-images-bucket`
- **Carpeta**: `products/`
- **Acceso**: Privado con URLs firmadas
- **Expiración**: 3 meses (2160 horas)

### Campos de Imagen
Cada producto puede tener asociada una foto con los siguientes campos:

- **`photo_filename`**: Nombre único del archivo (ej: `product_uuid.png`)
- **`photo_url`**: URL firmada para acceder a la imagen (generada dinámicamente)

### Generación de URLs
- Las URLs se generan automáticamente al crear un producto
- Las URLs se regeneran en cada consulta para mantenerlas válidas
- Formato: `https://storage.googleapis.com/medisupply-images-bucket/products/product_uuid.png?Expires=...&GoogleAccessId=...&Signature=...`

### Configuración
Las credenciales se configuran mediante variables de entorno:
```bash
GCP_PROJECT_ID=soluciones-cloud-2024-02
BUCKET_NAME=medisupply-images-bucket
BUCKET_FOLDER=products
GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-credentials.json
```

## Filtrado de Productos

### Endpoint de Filtros
`GET /inventory/products/filter` - Permite filtrar productos usando múltiples criterios

### Parámetros de Filtro Disponibles

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `sku` | string | Búsqueda parcial en SKU (case-insensitive) | `sku=MED` |
| `name` | string | Búsqueda parcial en nombre (case-insensitive) | `name=Paracetamol` |
| `expiration_date` | string | Fecha exacta de vencimiento (YYYY-MM-DD) | `expiration_date=2025-12-31` |
| `quantity` | integer | Cantidad exacta | `quantity=100` |
| `price` | float | Precio exacto | `price=15.50` |
| `location` | string | Búsqueda parcial en ubicación (case-insensitive) | `location=A-01` |

### Parámetros de Paginación

| Parámetro | Tipo | Descripción | Valor por defecto | Rango |
|-----------|------|-------------|-------------------|------|
| `page` | integer | Número de página | 1 | ≥ 1 |
| `per_page` | integer | Elementos por página | 10 | 1-100 |

### Combinaciones de Filtros

Puedes combinar múltiples filtros en la misma consulta:

```bash
# Filtro simple
curl "http://localhost:8084/inventory/products/filter?sku=MED"

# Dos filtros
curl "http://localhost:8084/inventory/products/filter?sku=MED&name=Paracetamol"

# Tres filtros
curl "http://localhost:8084/inventory/products/filter?sku=MED&name=Paracetamol&quantity=100"

# Todos los filtros
curl "http://localhost:8084/inventory/products/filter?sku=MED&name=Paracetamol&quantity=100&price=15.50&location=A-01&expiration_date=2025-12-31"

# Con paginación
curl "http://localhost:8084/inventory/products/filter?sku=MED&page=1&per_page=5"
```

### Respuesta del Endpoint de Filtros

```json
{
  "success": true,
  "message": "Productos filtrados obtenidos exitosamente",
  "data": {
    "products": [
      {
        "id": 65,
        "sku": "MED-1234",
        "name": "Paracetamol 500mg",
        "expiration_date": "2025-12-31T00:00:00",
        "quantity": 100,
        "price": 15.5,
        "location": "A-01-01",
        "description": "Analgésico y antipirético",
        "product_type": "Alto valor",
        "provider_id": "df3bdc3f-7783-4c1e-981a-8060b114dfb2",
        "photo_filename": null,
        "photo_url": null,
        "created_at": "2025-10-21T01:27:51.224416",
        "updated_at": "2025-10-21T01:27:51.224420"
      }
    ],
    "filters_applied": {
      "sku": "MED",
      "name": null,
      "expiration_date": null,
      "quantity": null,
      "price": null,
      "location": null
    },
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 4,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false,
      "next_page": null,
      "prev_page": null
    }
  }
}
```

### Validaciones y Errores

#### Error: Sin filtros
```json
{
  "success": false,
  "error": "Debe proporcionar al menos un filtro de búsqueda"
}
```

#### Error: Formato de fecha inválido
```json
{
  "success": false,
  "error": "El formato de 'expiration_date' debe ser YYYY-MM-DD"
}
```

#### Error: Parámetros de paginación inválidos
```json
{
  "success": false,
  "error": "El parámetro 'page' debe ser mayor a 0"
}
```

```json
{
  "success": false,
  "error": "El parámetro 'per_page' debe estar entre 1 y 100"
}
```


El proyecto incluye una colección de Postman completa con casos de prueba:

- Casos exitosos con datos aleatorios generados automáticamente
- Validaciones de campos obligatorios
- Validaciones de formato de datos (SKU, ubicación, fecha)
- Validaciones de rangos (cantidad, precio)
- Casos de error (producto no encontrado, SKU duplicado)
- Tests automatizados con pre-scripts y post-scripts

**Archivo:** `MediSupply-Inventory.postman_collection.json`

### Casos de Prueba Incluidos

1. **Health Check** - Verificación del estado del servicio
2. **Crear Producto - Datos Válidos** - Creación exitosa con datos aleatorios
3. **Crear Producto - SKU Duplicado** - Validación de unicidad
4. **Crear Producto - Campos Faltantes** - Validación de campos obligatorios
5. **Crear Producto - SKU Inválido** - Validación de formato SKU
6. **Crear Producto - Fecha Pasada** - Validación de fecha futura
7. **Crear Producto - Cantidad Inválida** - Validación de rango de cantidad
8. **Crear Producto - Ubicación Inválida** - Validación de formato ubicación
9. **Obtener Todos los Productos** - Listado completo
10. **Obtener Producto por ID** - Consulta individual
11. **Obtener Producto por ID - No Encontrado** - Manejo de errores
12. **Eliminar Producto por ID** - Eliminación individual
13. **Eliminar Producto por ID - No Encontrado** - Manejo de errores
14. **Eliminar Todos los Productos** - Limpieza completa

### Configuración

La colección usa la variable `url_local_inventario` configurada por defecto en `http://localhost:8084`.

## Ejemplos de Uso de la API

### Crear un Producto

```bash
curl -X POST http://localhost:8084/inventory/products \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "MED-1234",
    "name": "Paracetamol 500mg",
    "expiration_date": "2025-12-31T00:00:00.000Z",
    "quantity": 100,
    "price": 15000,
    "location": "A-01-01",
    "description": "Analgésico y antipirético",
    "product_type": "Alto valor"
  }'
```

### Obtener Todos los Productos

```bash
curl -X GET http://localhost:8084/inventory/products
```

### Obtener Producto por ID

```bash
curl -X GET http://localhost:8084/inventory/products/1
```

### Eliminar Producto

```bash
curl -X DELETE http://localhost:8084/inventory/products/1
```

### Health Check

```bash
curl -X GET http://localhost:8084/inventory/ping
```

## Cloud Run

Para desplegar en Google Cloud Run:

1. Construir imagen:
   ```bash
   docker build -t gcr.io/PROJECT_ID/medisupply-inventory .
   ```

2. Subir imagen:
   ```bash
   docker push gcr.io/PROJECT_ID/medisupply-inventory
   ```

3. Desplegar:
   ```bash
   gcloud run deploy medisupply-inventory \
     --image gcr.io/PROJECT_ID/medisupply-inventory \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Base de Datos

El proyecto utiliza PostgreSQL como base de datos principal:

- **Desarrollo local**: `postgresql://medisupply_local_user:medisupply_local_password@localhost:5432/medisupply_local_db`
- **Docker**: Conecta automáticamente a la base de datos del contenedor `medisupply-db`
- **Tablas**: Se crean automáticamente al iniciar la aplicación
- **Persistencia**: Los datos se mantienen en volúmenes Docker

## Variables de Entorno

- `HOST`: Host de la aplicación (default: 0.0.0.0)
- `PORT`: Puerto de la aplicación (default: 8080)
- `DEBUG`: Modo debug (default: True)
- `SECRET_KEY`: Clave secreta de Flask
- `DATABASE_URL`: URL de conexión a PostgreSQL

## Testing

### Ejecutar Tests

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con información detallada
pytest -v

# Ejecutar pruebas específicas
pytest tests/test_health_controller.py

# Ejecutar pruebas de un módulo específico
pytest tests/test_product_service.py -v
```

### Ejecutar con Coverage

```bash
# Ejecutar pruebas con coverage
pytest --cov=app --cov-report=term-missing

# Generar reporte HTML de coverage
pytest --cov=app --cov-report=html

# Verificar coverage mínimo del 95%
pytest --cov=app --cov-fail-under=95

# Ejecutar solo tests que fallan
pytest --lf
```

- **Arquitectura de testing robusta con mocking completo**

### Estructura de Tests

```
tests/
├── test_app.py                    # Tests de aplicación principal
├── test_base_controller.py        # Tests de controlador base
├── test_base_model.py             # Tests de modelo base
├── test_base_repository.py        # Tests de repositorio base
├── test_base_service.py           # Tests de servicio base
├── test_config_settings.py        # Tests de configuración
├── test_exceptions.py             # Tests de excepciones
├── test_health_controller.py      # Tests de health check
├── test_product_controller.py     # Tests de controlador de productos
├── test_product_model.py          # Tests de modelo de productos
├── test_product_repository.py     # Tests de repositorio de productos
└── test_product_service.py        # Tests de servicio de productos
```



## Actualización de Stock

### Endpoint: `PUT /inventory/products/{product_id}/stock`

Permite actualizar el stock de un producto específico mediante operaciones de suma o resta.

#### Request Body
```json
{
    "operation": "add|subtract",
    "quantity": 10,
    "reason": "restock|order_fulfillment|adjustment"
}
```

#### Parámetros
- **operation** (string, requerido): Operación a realizar
  - `"add"`: Sumar cantidad al stock
  - `"subtract"`: Restar cantidad del stock
- **quantity** (integer, requerido): Cantidad a sumar o restar (debe ser > 0)
- **reason** (string, opcional): Motivo del cambio de stock

#### Respuesta Exitosa (200)
```json
{
    "success": true,
    "message": "Stock actualizado exitosamente",
    "data": {
        "product_id": 1,
        "previous_quantity": 50,
        "new_quantity": 60,
        "operation": "add",
        "quantity_changed": 10
    }
}
```

#### Errores

**400 - Error de Validación:**
```json
{
    "success": false,
    "error": "Error de validación",
    "details": "La operación debe ser 'add' o 'subtract'"
}
```

**422 - Error de Lógica de Negocio:**
```json
{
    "success": false,
    "error": "Error de lógica de negocio",
    "details": "Stock insuficiente. Disponible: 5, Solicitado: 10"
}
```

#### Casos de Uso

1. **Restock de productos**: `{"operation": "add", "quantity": 100}`
2. **Fulfillment de pedidos**: `{"operation": "subtract", "quantity": 5}`
3. **Ajustes de inventario**: `{"operation": "add", "quantity": 2, "reason": "adjustment"}`

#### Validaciones

- El producto debe existir
- La operación debe ser válida (`add` o `subtract`)
- La cantidad debe ser mayor a 0
- Para operaciones `subtract`, debe haber stock suficiente
- El `product_id` debe ser un entero válido

## Desarrollo

Este proyecto sigue la arquitectura de microservicios y está diseñado para integrarse con otros servicios de MediSupply:

- **Autenticador**: Puerto 8081
- **Proveedores**: Puerto 8082
- **Inventarios**: Puerto 8084 (este servicio)

Todos los servicios comparten la misma base de datos PostgreSQL y están conectados a través de la red Docker `medisupply-net`.

### Arquitectura del Proyecto

```
app/
├── config/              # Configuración de la aplicación
├── controllers/         # Controladores REST (API endpoints)
├── services/           # Lógica de negocio
├── repositories/       # Acceso a datos (SQLAlchemy)
├── models/             # Modelos de datos
├── exceptions/         # Excepciones personalizadas
└── utils/              # Utilidades comunes
```

### Flujo de Datos

1. **Request** → Controller
2. **Controller** → Service (lógica de negocio)
3. **Service** → Repository (acceso a datos)
4. **Repository** → Database (PostgreSQL)
5. **Response** ← Controller ← Service ← Repository.