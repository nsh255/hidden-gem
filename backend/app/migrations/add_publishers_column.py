"""
Script de migración para añadir la columna 'publishers' a la tabla de juegos.
"""
import os
import sys
from sqlalchemy import create_engine, Column, ARRAY, String
from sqlalchemy.ext.declarative import declarative_base
from alembic import op
import sqlalchemy as sa
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Obtener la URL de la base de datos desde variables de entorno
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    logger.error("No se encontró la variable de entorno DATABASE_URL")
    sys.exit(1)

# Crear motor de base de datos
engine = create_engine(database_url)

def upgrade():
    """Añade la columna publishers a la tabla de juegos."""
    try:
        # Usando SQLAlchemy Core para añadir la columna
        op.add_column('games', sa.Column('publishers', sa.ARRAY(sa.String()), nullable=True))
        logger.info("Columna 'publishers' añadida exitosamente a la tabla 'games'")
    except Exception as e:
        logger.error(f"Error al añadir la columna 'publishers': {str(e)}")
        raise

def downgrade():
    """Elimina la columna publishers de la tabla de juegos."""
    try:
        op.drop_column('games', 'publishers')
        logger.info("Columna 'publishers' eliminada exitosamente de la tabla 'games'")
    except Exception as e:
        logger.error(f"Error al eliminar la columna 'publishers': {str(e)}")
        raise

if __name__ == "__main__":
    upgrade()
