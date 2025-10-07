"""
Servicio de Google Cloud Storage para manejo de imágenes
"""
import os
import uuid
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError
from PIL import Image
import io

from ..config.settings import Config


class CloudStorageService:
    """Servicio para manejar operaciones con Google Cloud Storage"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self._client = None
        self._bucket = None
    
    @property
    def client(self) -> storage.Client:
        """Obtiene el cliente de Google Cloud Storage"""
        if self._client is None:
            try:
                # Configurar credenciales si están disponibles
                if self.config.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.GOOGLE_APPLICATION_CREDENTIALS
                
                self._client = storage.Client(project=self.config.GCP_PROJECT_ID)
            except Exception as e:
                raise GoogleCloudError(f"Error al inicializar cliente de GCS: {str(e)}")
        
        return self._client
    
    @property
    def bucket(self) -> storage.Bucket:
        """Obtiene el bucket de Google Cloud Storage"""
        if self._bucket is None:
            try:
                self._bucket = self.client.bucket(self.config.BUCKET_NAME)
            except Exception as e:
                raise GoogleCloudError(f"Error al obtener bucket '{self.config.BUCKET_NAME}': {str(e)}")
        
        return self._bucket
    
    def validate_image_file(self, file: FileStorage) -> Tuple[bool, str]:
        """
        Valida que el archivo sea una imagen válida
        
        Args:
            file: Archivo a validar
            
        Returns:
            Tuple[bool, str]: (es_válido, mensaje_error)
        """
        if not file or not file.filename:
            return False, "No se proporcionó archivo"
        
        # Verificar extensión
        if '.' not in file.filename:
            return False, "El archivo no tiene extensión"
        
        extension = file.filename.lower().split('.')[-1]
        if extension not in self.config.ALLOWED_EXTENSIONS:
            return False, f"Extensión no permitida. Use: {', '.join(self.config.ALLOWED_EXTENSIONS)}"
        
        # Verificar tamaño del archivo
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size == 0:
            return False, "El archivo está vacío"
        
        if file_size > self.config.MAX_CONTENT_LENGTH:
            max_mb = self.config.MAX_CONTENT_LENGTH / (1024 * 1024)
            return False, f"El archivo es demasiado grande. Máximo: {max_mb}MB"
        
        # Verificar que sea una imagen válida usando PIL
        try:
            file.seek(0)
            image = Image.open(file)
            image.verify()  # Verificar que sea una imagen válida
            file.seek(0)  # Volver al inicio
        except Exception as e:
            return False, f"El archivo no es una imagen válida: {str(e)}"
        
        return True, ""
    
    def generate_unique_filename(self, original_filename: str, prefix: str = "product") -> str:
        """
        Genera un nombre único para el archivo
        
        Args:
            original_filename: Nombre original del archivo
            prefix: Prefijo para el nombre del archivo
            
        Returns:
            str: Nombre único del archivo
        """
        if not original_filename or '.' not in original_filename:
            return f"{prefix}_{uuid.uuid4()}.jpg"
        
        extension = original_filename.lower().split('.')[-1]
        unique_id = str(uuid.uuid4())
        return f"{prefix}_{unique_id}.{extension}"
    
    def upload_image(self, file: FileStorage, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Sube una imagen al bucket de Google Cloud Storage en la carpeta específica
        
        Args:
            file: Archivo de imagen
            filename: Nombre del archivo en el bucket
            
        Returns:
            Tuple[bool, str, Optional[str]]: (éxito, mensaje, url_pública)
        """
        try:
            # Validar archivo
            is_valid, error_message = self.validate_image_file(file)
            if not is_valid:
                return False, error_message, None
            
            # Crear ruta completa con carpeta
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            
            # Crear blob en el bucket
            blob = self.bucket.blob(full_path)
            
            # Configurar metadatos
            blob.metadata = {
                'original_filename': file.filename,
                'content_type': f'image/{filename.split(".")[-1].lower()}',
                'uploaded_by': 'medisupply-inventories',
                'folder': self.config.BUCKET_FOLDER
            }
            
            # Subir archivo
            file.seek(0)
            blob.upload_from_file(file, content_type=blob.metadata['content_type'])
            
            # Generar URL pública
            public_url = f"https://storage.googleapis.com/{self.config.BUCKET_NAME}/{full_path}"
            
            return True, "Imagen subida exitosamente", public_url
            
        except GoogleCloudError as e:
            return False, f"Error de Google Cloud Storage: {str(e)}", None
        except Exception as e:
            return False, f"Error al subir imagen: {str(e)}", None
    
    def delete_image(self, filename: str) -> Tuple[bool, str]:
        """
        Elimina una imagen del bucket
        
        Args:
            filename: Nombre del archivo a eliminar
            
        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        try:
            # Crear ruta completa con carpeta
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            blob = self.bucket.blob(full_path)
            
            if not blob.exists():
                return False, "El archivo no existe en el bucket"
            
            blob.delete()
            return True, "Imagen eliminada exitosamente"
            
        except GoogleCloudError as e:
            return False, f"Error de Google Cloud Storage: {str(e)}"
        except Exception as e:
            return False, f"Error al eliminar imagen: {str(e)}"
    
    def get_image_url(self, filename: str, expiration_hours: int = 2160) -> str:
        """
        Obtiene la URL firmada de una imagen
        
        Args:
            filename: Nombre del archivo
            expiration_hours: Horas de validez de la URL (default: 2160 = 3 meses)
            
        Returns:
            str: URL firmada de la imagen
        """
        try:
            from datetime import datetime, timedelta
            
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            blob = self.bucket.blob(full_path)
            
            # Verificar que el blob existe
            if not blob.exists():
                return ""
            
            # Generar URL firmada con expiración
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            signed_url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            
            return signed_url
            
        except Exception as e:
            # Fallback a URL directa si hay error
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            return f"https://storage.googleapis.com/{self.config.BUCKET_NAME}/{full_path}"
    
    def image_exists(self, filename: str) -> bool:
        """
        Verifica si una imagen existe en el bucket
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            bool: True si existe, False en caso contrario
        """
        try:
            full_path = f"{self.config.BUCKET_FOLDER}/{filename}"
            blob = self.bucket.blob(full_path)
            return blob.exists()
        except Exception:
            return False
