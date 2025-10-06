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

- Python 3.9
- Flask 3.0.3
- Gunicorn 21.2.0
- Docker

## Instalación

### Desarrollo Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   python app.py
   ```

### Con Docker

1. Construir y ejecutar:
   ```bash
   docker-compose up --build
   ```

2. La aplicación estará disponible en `http://localhost:8083`

## Endpoints

### Health Check
- `GET /inventory/ping` - Ping simple

### Productos
- `GET /inventory/products` - Obtener todos los productos
- `GET /inventory/products/{id}` - Obtener producto por ID
- `POST /inventory/products` - Crear nuevo producto
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
  "photo_filename": "paracetamol.jpg"
}
```

### Validaciones de Producto

- **SKU**: Formato "MED-XXXX" (4 dígitos numéricos), único
- **Nombre**: Alfanumérico y espacios, mínimo 3 caracteres
- **Fecha de vencimiento**: Debe ser futura
- **Cantidad**: Entero positivo (1-9999)
- **Precio**: Numérico positivo en COP
- **Ubicación**: Formato "P-EE-NN" (Pasillo: A-Z, Estante: 01-99, Nivel: 01-99)
- **Tipo de producto**: "Alto valor", "Medio valor", "Bajo valor"
- **Foto**: JPG, PNG, GIF, máximo 2MB (opcional)

## Colección de Postman

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

La colección usa la variable `url_local_inventario` configurada por defecto en `http://localhost:8083`.

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

## Variables de Entorno

- `HOST`: Host de la aplicación (default: 0.0.0.0)
- `PORT`: Puerto de la aplicación (default: 8080)
- `DEBUG`: Modo debug (default: True)
- `SECRET_KEY`: Clave secreta de Flask

## Testing

### Ejecutar Tests

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con información detallada
pytest -v

# Ejecutar pruebas específicas
pytest tests/test_health_controller.py
```

### Ejecutar con Coverage

```bash
# Ejecutar pruebas con coverage
pytest --cov=app --cov-report=term-missing

# Generar reporte HTML de coverage
pytest --cov=app --cov-report=html

# Verificar 100% de coverage
pytest --cov=app --cov-fail-under=100
```

## Desarrollo

Este proyecto sigue la arquitectura de microservicios y está diseñado para integrarse con otros servicios de MediSupply:

- **Autenticador**: Puerto 8081
- **Proveedores**: Puerto 8082
- **Inventarios**: Puerto 8083 (este servicio)

Todos los servicios comparten la misma base de datos PostgreSQL y están conectados a través de la red Docker `medisupply-net`.