# ============================================================================
# CONSULTAS.PY - Funciones de consultas a la base de datos (Nombres Originales)
# ============================================================================

import asyncpg
from fastapi import HTTPException, status
from loguru import logger 

# FUNCIÓN 1: Mantienes el nombre 'autores' pero sin el Depends interno
async def autores(db: asyncpg.Connection):
    """Obtiene primeros 10 autores de tabla 'autores'"""
    try:
        query = "SELECT * FROM autores LIMIT 10;"
        rows = await db.fetch(query)  
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al consultar autores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar los autores."
        )

# FUNCIÓN 2: Conserva el nombre 'buscar_titulo'
async def buscar_titulo(conn: asyncpg.Connection):
    """Obtiene primeros 10 títulos de tabla 'libros'"""
    try:
        query = "SELECT titulo FROM libros LIMIT 10;"  
        filas = await conn.fetch(query)  
        return [dict(fila) for fila in filas]  
    except Exception as e:
        logger.error(f"Error al consultar títulos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener títulos de muestra."
        )

# FUNCIÓN 3: Conserva el nombre original
async def buscar_titulos_con_filtros(db: asyncpg.Connection, titulo: str = None, autor: str = None):
    """Busca títulos en lista_larga del año 2023 con filtros opcionales"""
    try:
        if titulo and autor:
            query = """
                SELECT titulo, autor FROM lista_larga
                WHERE anio = 2023 AND LOWER(titulo) LIKE LOWER($1) AND LOWER(autor) LIKE LOWER($2)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{titulo}%", f"%{autor}%")
        elif titulo:
            query = """
                SELECT titulo, autor FROM lista_larga
                WHERE anio = 2023 AND LOWER(titulo) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{titulo}%")
        elif autor:
            query = """
                SELECT titulo, autor FROM lista_larga
                WHERE anio = 2023 AND LOWER(autor) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{autor}%")
        else:
            query = """
                SELECT titulo, autor FROM lista_larga
                WHERE anio = 2023 ORDER BY titulo ASC;
            """
            filas = await db.fetch(query)

        return [dict(fila) for fila in filas]
    except Exception as e:
        logger.error(f"Error al consultar títulos con filtros: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al filtrar los títulos."
        )

# FUNCIÓN 4: Conserva el nombre 'buscar_titulos'
async def buscar_titulos(db: asyncpg.Connection):
    """Obtiene TODOS los títulos del año 2023"""
    try:
        query = """SELECT titulo, autor FROM lista_larga
                   WHERE anio = 2023 ORDER BY titulo ASC;"""
        filas = await db.fetch(query)  
        return [dict(fila) for fila in filas]  
    except Exception as e:
        logger.error(f"Error al obtener títulos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener el listado completo de títulos."
        )
