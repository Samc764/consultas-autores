# ============================================================================
# DATABASE.PY - Gestión de conexiones a PostgreSQL
# ============================================================================
# Pool de conexiones reutilizables para mejor rendimiento
# Automáticamente crea, recicla y cierra conexiones

from typing import AsyncGenerator
import asyncpg
from loguru import logger  # Para logging

# ============================================================================
# CONFIGURACIÓN DE CONEXIÓN
# ============================================================================
# La URL de la base de datos se toma de la variable de entorno DATABASE_URL.
# En Vercel debes configurar DATABASE_URL en el panel de Variables de Entorno.
from os import getenv

DATABASE_URL = getenv(
    "DATABASE_URL",
    "postgresql://estudiantes:npg_FtxeYOVU8yD7@ep-withered-wind-apq7hmfj-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Pool global: instancia única para toda la aplicación
_pool: asyncpg.Pool | None = None

# ============================================================================
# FUNCIÓN 1: init_db_pool - Inicializar pool de conexiones
# ============================================================================
async def init_db_pool():
    """
    Crear pool de conexiones reutilizables a PostgreSQL.
    - Llamado automáticamente al iniciar la aplicación
    - Crea 10-20 conexiones en memoria
    - Las reutiliza para todas las consultas
    """
    global _pool
    if _pool is None:
        try:
            # Crear pool con configuración
            _pool = await asyncpg.create_pool(
                DATABASE_URL,
                min_size=10,        # 10 conexiones siempre abiertas
                max_size=20,        # Máximo 20 conexiones simultáneas
                max_queries=50000,  # Reciclar después de 50k queries
                max_inactive_connection_lifetime=300.0, # Cerrar después de 5 min inactivas
            )
            logger.info("✓ Pool de conexiones creado exitosamente")
        except Exception as e:
            logger.error(f"✗ Error al crear el pool: {e}")
            raise e


# ============================================================================
# FUNCIÓN 2: close_db_pool - Cerrar pool de conexiones
# ============================================================================
async def close_db_pool():
    """
    Cerrar todas las conexiones del pool.
    - Llamado automáticamente al detener la aplicación
    - Limpia todas las conexiones activas
    - Libera recursos
    """
    global _pool
    if _pool is not None:
        await _pool.close()  # Cerrar todas las conexiones
        _pool = None  # Resetear variable
        logger.info("✓ Pool de conexiones cerrado")


# ============================================================================
# FUNCIÓN 3: get_db - Obtener conexión del pool
# ============================================================================
async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    Obtener una conexión del pool para usar en un endpoint.
    - Se inyecta automáticamente con Depends(get_db)
    - Adquiere conexión del pool
    - La libera automáticamente cuando termina
    
    Ejemplo de uso:
        @app.get("/ruta")
        async def mi_endpoint(db: asyncpg.Connection = Depends(get_db)):
            resultado = await db.fetch("SELECT * FROM tabla")
    """
    if _pool is None:
        raise RuntimeError("El pool no fue inicializado")

    # Adquirir conexión del pool y devolverla automáticamente
    async with _pool.acquire() as connection:
        yield connection  # Proporcionar conexión al endpoint