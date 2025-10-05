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

## Respuesta del Health Check

```json
"pong"
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