"""
Repositorio de Productos - Implementación con SQLAlchemy
"""
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import uuid

from .base_repository import BaseRepository
from ..models.product import Product
from ..config.settings import Config

# Configuración de SQLAlchemy
Base = declarative_base()


class ProductDB(Base):
    """Modelo de base de datos para productos"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String(20), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    location = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    product_type = Column(String(50), nullable=False)
    provider_id = Column(String(36), nullable=False)
    photo_filename = Column(String(255), nullable=True)
    photo_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProductRepository(BaseRepository):
    """
    Repositorio para operaciones de productos en la base de datos
    """
    
    def __init__(self):
        # Configuración de la base de datos
        self.engine = create_engine(Config.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # Crear tablas si no existen
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            print(f"Error creando tablas: {e}")
    
    def _get_session(self) -> Session:
        """Obtiene una sesión de base de datos"""
        return self.Session()
    
    def _db_to_model(self, db_product: ProductDB) -> Product:
        """Convierte un objeto de base de datos a modelo de dominio"""
        return Product(
            id=db_product.id,
            sku=db_product.sku,
            name=db_product.name,
            expiration_date=db_product.expiration_date.isoformat() if db_product.expiration_date else None,
            quantity=db_product.quantity,
            price=db_product.price,
            location=db_product.location,
            description=db_product.description,
            product_type=db_product.product_type,
            provider_id=db_product.provider_id,
            photo_filename=db_product.photo_filename,
            photo_url=db_product.photo_url
        )
    
    def _model_to_db(self, product: Product) -> ProductDB:
        """Convierte un modelo de dominio a objeto de base de datos"""
        return ProductDB(
            sku=product.sku,
            name=product.name,
            expiration_date=product.expiration_date if isinstance(product.expiration_date, datetime) else datetime.fromisoformat(product.expiration_date.replace('Z', '+00:00')) if product.expiration_date else None,
            quantity=product.quantity,
            price=product.price,
            location=product.location,
            description=product.description,
            product_type=product.product_type,
            provider_id=product.provider_id,
            photo_filename=product.photo_filename,
            photo_url=product.photo_url
        )
    
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
        session = self._get_session()
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Convertir a objeto de base de datos
            db_product = self._model_to_db(product)
            
            # Guardar en base de datos
            session.add(db_product)
            session.commit()
            
            # Asignar ID al producto original
            product.id = db_product.id
            
            return product
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al crear producto: {str(e)}")
        finally:
            session.close()
    
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
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if db_product:
                return self._db_to_model(db_product)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener producto por ID: {str(e)}")
        finally:
            session.close()
    
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
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.sku == sku).first()
            if db_product:
                return self._db_to_model(db_product)
            return None
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener producto por SKU: {str(e)}")
        finally:
            session.close()
    
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos
        
        Returns:
            List[Product]: Lista de todos los productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            db_products = session.query(ProductDB).all()
            return [self._db_to_model(db_product) for db_product in db_products]
        except SQLAlchemyError as e:
            raise Exception(f"Error al obtener todos los productos: {str(e)}")
        finally:
            session.close()
    
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
        session = self._get_session()
        try:
            # Validar que el producto sea válido
            product.validate()
            
            # Buscar el producto existente
            db_product = session.query(ProductDB).filter(ProductDB.id == product.id).first()
            if db_product:
                # Actualizar campos
                db_product.sku = product.sku
                db_product.name = product.name
                db_product.expiration_date = product.expiration_date if isinstance(product.expiration_date, datetime) else datetime.fromisoformat(product.expiration_date.replace('Z', '+00:00')) if product.expiration_date else None
                db_product.quantity = product.quantity
                db_product.price = product.price
                db_product.location = product.location
                db_product.description = product.description
                db_product.product_type = product.product_type
                db_product.photo_filename = product.photo_filename
                db_product.updated_at = datetime.utcnow()
                
                session.commit()
            
            return product
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al actualizar producto: {str(e)}")
        finally:
            session.close()
    
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
        session = self._get_session()
        try:
            db_product = session.query(ProductDB).filter(ProductDB.id == product_id).first()
            if db_product:
                session.delete(db_product)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar producto: {str(e)}")
        finally:
            session.close()
    
    def delete_all(self) -> int:
        """
        Elimina todos los productos
        
        Returns:
            int: Número de productos eliminados
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            count = session.query(ProductDB).count()
            session.query(ProductDB).delete()
            session.commit()
            return count
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error al eliminar todos los productos: {str(e)}")
        finally:
            session.close()
    
    def count(self) -> int:
        """
        Cuenta el total de productos
        
        Returns:
            int: Número total de productos
            
        Raises:
            Exception: Si hay error en la base de datos
        """
        session = self._get_session()
        try:
            return session.query(ProductDB).count()
        except SQLAlchemyError as e:
            raise Exception(f"Error al contar productos: {str(e)}")
        finally:
            session.close()