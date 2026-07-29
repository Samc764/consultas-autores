# ============================================================================
# CONSULTAS.PY - Funciones de consultas a la base de datos
# ============================================================================
# Todas las funciones que interactúan con PostgreSQL están aquí

import asyncpg
from fastapi import Depends, HTTPException
from loguru import logger  # Para logging de eventos/errores

from database import get_db


# FUNCIÓN 1: Obtener autores
async def autores(db: asyncpg.Connection = Depends(get_db)):
    """Obtiene primeros 10 autores de tabla 'autores'"""
    try:
        query = "SELECT * FROM autores LIMIT 10;"
        rows = await db.fetch(query)  # Ejecutar query
        registros = [dict(row) for row in rows]  # Convertir a dicts
        return registros if registros else []
    except Exception as e:
        logger.error(f"Error al consultar autores: {e}")
        return []


# FUNCIÓN 2: Buscar títulos de libros
async def buscar_titulo(conn: asyncpg.Connection):
    """Obtiene primeros 10 títulos de tabla 'libros'"""
    try:
        query = "SELECT titulo FROM libros LIMIT 10;"  # Query SQL
        filas = await conn.fetch(query)  # Ejecutar
        return [dict(fila) for fila in filas]  # Convertir a dicts
    except Exception as e:
        logger.error(f"Error al consultar títulos: {e}")
        return []


async def buscar_titulos_con_filtros(db: asyncpg.Connection, titulo: str = None, autor: str = None):
    """
    Busca títulos en lista_larga del año 2023 con filtros opcionales de título y autor
    Usa consultas paramétrizadas para seguridad
    """
    try:
        if titulo and autor:
            # Ambos filtros
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
            # Solo título
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                    AND LOWER(titulo) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{titulo}%")
        
        elif autor:
            # Solo autor
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                    AND LOWER(autor) LIKE LOWER($1)
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query, f"%{autor}%")
        
        else:
            # Sin filtros
            query = """
                SELECT titulo, autor
                FROM lista_larga
                WHERE anio = 2023
                ORDER BY titulo ASC;
            """
            filas = await db.fetch(query)

        return [dict(fila) for fila in filas]

    except Exception as e:
        logger.error(f"Error al consultar títulos: {e}")
        return []


# FUNCIÓN 4: Obtener todos los títulos
async def buscar_titulos(db: asyncpg.Connection):
    """Obtiene TODOS los títulos del año 2023"""
    try:
        # Query: traer todos los libros del 2023 ordenados
        query = """SELECT titulo, autor FROM lista_larga
                   WHERE anio = 2023 ORDER BY titulo ASC;"""
        filas = await db.fetch(query)  # Ejecutar query
        return [dict(fila) for fila in filas]  # Convertir a dicts
    except Exception as e:
        logger.error(f"Error al obtener títulos: {e}")
        return []