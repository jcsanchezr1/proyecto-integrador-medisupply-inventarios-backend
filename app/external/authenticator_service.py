import requests
import logging
from typing import Dict, Optional
from app.config.settings import get_config
from app.exceptions.business_logic_error import BusinessLogicError

logger = logging.getLogger(__name__)


class AuthenticatorService:
    """
    Servicio para comunicación con el microservicio de autenticación
    """
    
    def __init__(self):
        self.config = get_config()
        self.base_url = self.config.AUTHENTICATOR_SERVICE_URL
        self.timeout = 10  # Timeout en segundos
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene un usuario por su ID desde el servicio externo
        
        Args:
            user_id: ID del usuario (UUID)
            
        Returns:
            Optional[Dict]: Datos del usuario o None si no existe
            
        Raises:
            BusinessLogicError: Si hay error en la comunicación con el servicio
        """
        try:
            url = f"{self.base_url}/auth/user/{user_id}"
            
            logger.info(f"Consultando usuario: {url}")
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'Usuario obtenido exitosamente' and 'data' in data:
                    return data['data']
                else:
                    logger.warning(f"Respuesta inesperada del servicio de autenticación: {data}")
                    return None
            elif response.status_code == 404:
                logger.warning(f"Usuario no encontrado: {user_id}")
                return None
            else:
                logger.error(f"Error en servicio de autenticación: {response.status_code} - {response.text}")
                raise BusinessLogicError(f"Error en servicio de autenticación: {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al consultar usuario {user_id}")
            raise BusinessLogicError("Timeout al consultar el servicio de autenticación")
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al consultar usuario {user_id}")
            raise BusinessLogicError("Error de conexión con el servicio de autenticación")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición al servicio de autenticación: {str(e)}")
            raise BusinessLogicError(f"Error al consultar usuario: {str(e)}")
        except Exception as e:
            logger.error(f"Error inesperado al consultar usuario {user_id}: {str(e)}")
            raise BusinessLogicError(f"Error inesperado al consultar usuario: {str(e)}")
    
    def get_user_name(self, user_id: str) -> str:
        """
        Obtiene el nombre de un usuario, retornando "Usuario no disponible" si falla
        
        Args:
            user_id: ID del usuario
            
        Returns:
            str: Nombre del usuario o "Usuario no disponible" si falla
        """
        try:
            user = self.get_user_by_id(user_id)
            if user and 'name' in user:
                return user['name']
            else:
                return "Usuario no disponible"
        except Exception as e:
            logger.error(f"Error al obtener nombre del usuario {user_id}: {str(e)}")
            return "Usuario no disponible"

