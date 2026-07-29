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
    titulo: str = "",      
    autor: str = "",       
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Búsqueda principal utilizando el controlador de consultas.py.
    Retorna HTML estructurado dinámicamente.
    """
    try:
        # OPTIMIZACIÓN: Delegamos la query segura y los filtros a consultas.py
        result = await buscar_titulos_con_filtros(db, titulo=titulo, autor=autor)
        
        # Construir interfaz HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Buscar Libros</title>
            <style>
                body {{ font-family: Arial; background: #1a1a2e; color: #e0e0e0; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; background: #16213e; padding: 20px; }}
                h1 {{ color: #00d4ff; }}
                form {{ margin-bottom: 20px; }}
                input {{ padding: 5px; width: 200px; margin-right: 10px; background: #0f3460; color: white; border: 1px solid #00d4ff; }}
                button {{ padding: 5px 15px; background: #00d4ff; color: #1a1a2e; font-weight: bold; border: none; cursor: pointer; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #0f3460; padding: 10px; text-align: left; }}
                th {{ background: #0f3460; color: #00d4ff; }}
                tr:hover {{ background: #0f3460; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📚 Búsqueda de Libros 2023</h1>
                
                <form method="get">
                    <input type="text" name="titulo" placeholder="Título..." value="{titulo}">
                    <input type="text" name="autor" placeholder="Autor..." value="{autor}">
                    <button type="submit">🔍 Buscar</button>
                </form>

                <p>Se encontraron <strong>{len(result)}</strong> resultado(s)</p>
        """
        
        if result:
            html += """
                <table>
                    <tr>
                        <th>Título</th>
                        <th>Autor</th>
                    </tr>
            """
            for row in result:
                html += f"""
                    <tr>
                        <td>{row['titulo']}</td>
                        <td>{row['autor']}</td>
                    </tr>
                """
            html += """
                </table>
            """
        else:
            html += "<p style='color: #999;'>Sin resultados que coincidan.</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        return html
        
    except Exception as e:
        logger.error(f"Error en endpoint buscar: {e}", exc_info=True)
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="background: #1a1a2e; color: #ff5555; padding: 20px; font-family: Arial;">
            <h1>⚠️ Ocurrió un error en el servidor</h1>
            <p>{str(e)}</p>
        </body>
        </html>
        """


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

    # CORRECCIÓN: Se añadieron los nombres explícitos de los parámetros de Jinja2
    return templates.TemplateResponse(
        request=request,
        name="titulos.html",
        context={"titulos": titulos}
    )


# ============================================================================
# RUTA API: GET /api/titulos-2023 - JSON puro
# ============================================================================
@app.get("/api/titulos-2023")
async def get_titulos_2023(db: asyncpg.Connection = Depends(get_db)):
    """Retorna JSON nativo con títulos de la lista_larga del año 2023"""
    # Reutiliza la función del core de consultas para evitar SQL duplicado
    return await buscar_titulos(db)
