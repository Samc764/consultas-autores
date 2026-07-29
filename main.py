# ============================================================================
# MAIN.PY - Archivo principal de FastAPI (Corregido y Optimizado)
# ============================================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import asyncpg
from loguru import logger  # Logging de eventos y errores

# Importar gestión de conexiones
from database import init_db_pool, close_db_pool, get_db
# Importar funciones de consultas
from consultas import autores, buscar_titulo, buscar_titulos, buscar_titulos_con_filtros


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestor del ciclo de vida de FastAPI para el Pool de conexiones."""
    await init_db_pool()  # Inicializar pool
    yield  # Ejecutar app
    await close_db_pool()  # Cerrar pool


# Crear app FastAPI con gestor de ciclo de vida
app = FastAPI(lifespan=lifespan)

# Configurar carpeta de plantillas Jinja2
templates = Jinja2Templates(directory="templates")


# ============================================================================
# RUTA RAÍZ: GET / - Redirige a /usuarios para evitar 404 en Vercel
# ============================================================================
@app.get("/")
async def root():
    return RedirectResponse(url="/usuarios")


# ============================================================================
# RUTA 1: GET /usuarios - Listar autores
# ============================================================================
@app.get("/usuarios")
async def listar_usuarios(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Obtiene lista de autores y retorna HTML via Jinja2"""
    registros = await autores(db)

    return templates.TemplateResponse(
        request=request,
        name="usuarios.html",
        context={"usuarios": registros}
    )


# ============================================================================
# RUTA 2: GET /traer_titulo - Listar títulos de libros (Muestra)
# ============================================================================
@app.get("/traer_titulo")
async def traer_titulo_endpoint(
    request: Request,
    conn: asyncpg.Connection = Depends(get_db)
):
    """Obtiene títulos de libros de muestra y retorna HTML via Jinja2"""
    titulos = await buscar_titulo(conn)

    return templates.TemplateResponse(
        request=request,
        name="titulos.html",
        context={"titulos": titulos}
    )


# ============================================================================
# RUTA 3: GET /buscar - Búsqueda avanzada de libros (AÑO 2023)
# ============================================================================
@app.get("/buscar", response_class=HTMLResponse)
async def buscar_libros(
    request: Request,
    titulo: str = "",
    autor: str = "",
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Búsqueda principal utilizando el controlador de consultas.py.
    Retorna HTML a través de la plantilla buscar.html.
    """
    try:
        titulos = await buscar_titulos_con_filtros(db, titulo=titulo, autor=autor)
        return templates.TemplateResponse(
            "buscar.html",
            {
                "request": request,
                "titulos": titulos,
                "busqueda_titulo": titulo,
                "busqueda_autor": autor,
            },
        )
    except Exception as e:
        logger.error(f"Error en endpoint buscar: {e}", exc_info=True)
        return HTMLResponse(
            f"""
            <!DOCTYPE html>
            <html>
            <head><title>Error</title></head>
            <body style="background: #1a1a2e; color: #ff5555; padding: 20px; font-family: Arial;">
                <h1>⚠️ Ocurrió un error en el servidor</h1>
                <p>{str(e)}</p>
            </body>
            </html>
            """,
            status_code=500,
        )


# ============================================================================
# RUTA 4: GET /titulos - Listar todos los títulos sin filtros
# ============================================================================
@app.get("/titulos")
async def mostrar_titulos(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)
):
    """Obtiene TODOS los títulos del 2023 sin filtros y los renderiza"""
    titulos = await buscar_titulos(db)

    return templates.TemplateResponse(
        "titulos.html",
        {
            "request": request,
            "titulos": titulos,
            "busqueda_titulo": "",
            "busqueda_autor": "",
        },
    )


# ============================================================================
# RUTA 5: GET /traer_titulos - Buscar títulos con filtros y mostrar resultados
# ============================================================================
@app.get("/traer_titulos")
async def traer_titulos(
    request: Request,
    titulo: str = "",
    autor: str = "",
    db: asyncpg.Connection = Depends(get_db)
):
    """Búsqueda de títulos usando la plantilla tituloss.html"""
    titulos = await buscar_titulos_con_filtros(db, titulo=titulo, autor=autor)
    return templates.TemplateResponse(
        "tituloss.html",
        {
            "request": request,
            "titulos": titulos,
            "busqueda_titulo": titulo,
            "busqueda_autor": autor,
        },
    )


# ============================================================================
# RUTA API: GET /api/titulos-2023 - JSON puro
# ============================================================================
@app.get("/api/titulos-2023")
async def get_titulos_2023(db: asyncpg.Connection = Depends(get_db)):
    """Retorna JSON nativo con títulos de la lista_larga del año 2023"""
    return await buscar_titulos(db)
