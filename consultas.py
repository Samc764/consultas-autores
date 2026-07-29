# ============================================================================
# CONSULTAS.PY - Funciones de consultas a la base de datos
# ============================================================================
# Todas las funciones que interactúan con PostgreSQL están aquí

import asyncpg
from fastapi import HTTPException, status
from loguru import logger  # Para logging de eventos/errors


# FUNCIÓN 1: Obtener autores
async def obtener_autores(db: asyncpg.Connection):
    """Obtiene primeros 10 autores de tabla 'autores'"""
    try:
        query = "SELECT * FROM autores LIMIT 10;"
        rows = await db.fetch(query)  # Ejecutar query
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error al consultar autores: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al consultar los autores."
        )


# FUNCIÓN 2: Buscar títulos de libros (Muestra simple)
async def buscar_titulo_muestra(conn: asyncpg.Connection):
    """Obtiene primeros 10 títulos de tabla 'libros'"""
    try:
        query = "SELECT titulo FROM libros LIMIT 10;"  # Query SQL
        filas = await conn.fetch(query)  # Ejecutar
        return [dict(fila) for fila in filas]  # Convertir a dicts
    except Exception as e:
        logger.error(f"Error al consultar títulos de muestra: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener la muestra de títulos."
        )


# FUNCIÓN 3: Buscar títulos con filtros dinámicos
async def buscar_titulos_con_filtros(db: asyncpg.Connection, titulo: str = None, autor: str = None):
    """
    Busca títulos en lista_larga del año 2023 con filtros opcionales de título y autor
    Usa consultas parametrizadas para seguridad contra Inyección SQL
    """
    try:
        if titulo and autor:
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                    AND LOWER(titulo) LIKE LOWER($1)
                    AND LOWER(autor) LIKE LOWER($2)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{titulo}%", f"%{autor}%")
        
        elif titulo:
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                    AND LOWER(titulo) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{titulo}%")
        
        elif autor:
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                    AND LOWER(autor) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{autor}%")
        
        else:
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query)

        return [dict(fila) for fila in filas]

    except Exception as e:
        logger.error(f"Error al consultar títulos con filtros: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al filtrar los títulos."
        )


# FUNCIÓN 4: Obtener todos los títulos del 2023
async def buscar_todos_los_titulos(db: asyncpg.Connection):
    """Obtiene TODOS los títulos del año 2023"""
    try:
        query = """SELECT titulo, autor FROM lista_larga
                   WHERE anio = 2023 ORDER BY titulo ASC;"""
        filas = await db.fetch(query)  # Ejecutar query
        return [dict(fila) for fila in filas]  # Convertir a dicts
    except Exception as e:
        logger.error(f"Error al obtener todos los títulos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al obtener el listado completo de títulos."
        )
