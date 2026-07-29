# ============================================================================
# MAIN.PY - Archivo principal de FastAPI
# ============================================================================
# Rutas (endpoints) principales de la aplicación web

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncpg
from loguru import logger  # Logging de eventos y errores

# Importar gestión de conexiones
from database import init_db_pool, close_db_pool, get_db
# Importar funciones de consultas
from consultas import autores, buscar_titulo, buscar_titulos, buscar_titulos_con_filtros


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor del ciclo de vida de FastAPI.
    Startup: Crear conexiones a BD
    Shutdown: Cerrar conexiones a BD
    """
    await init_db_pool()  # Inicializar pool
    yield  # Ejecutar app
    await close_db_pool()  # Cerrar pool


# Crear app FastAPI con gestor de ciclo de vida
app = FastAPI(lifespan=lifespan)

# Configurar carpeta de plantillas Jinja2
templates = Jinja2Templates(directory="templates")


# ============================================================================
# RUTA 1: GET /usuarios - Listar autores
# ============================================================================
@app.get("/usuarios")
async def listar_usuarios(
    request: Request,
    db: asyncpg.Connection = Depends(get_db)  # Inyecta conexion BD
):
    """Obtiene lista de autores y retorna HTML"""
    # Consultar autores
    registros = await autores(db)

    # Renderizar template con datos
    return templates.TemplateResponse(
        request=request,
        name="usuarios.html",
        context={"usuarios": registros}
    )


# ============================================================================
# RUTA 2: GET /traer_titulo - Listar títulos de libros
# ============================================================================
@app.get("/traer_titulo")
async def traer_titulo_endpoint(
    request: Request,
    conn=Depends(get_db)  # Inyecta conexion BD
):
    """Obtiene títulos de libros y retorna HTML"""
    # Consultar títulos
    titulos = await buscar_titulo(conn)

    # Renderizar template con datos
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
    titulo: str = "",      # Filtro opcional: título
    autor: str = "",       # Filtro opcional: autor
    db: asyncpg.Connection = Depends(get_db)  # Inyecta conexion BD
):
    """
    Búsqueda principal de libros.
    Parámetros: ?titulo=palabra&autor=palabra
    Retorna HTML puro (sin Jinja2 para evitar problemas)
    """
    try:
        # Construir query dinámica según parámetros
        query_parts = ["SELECT titulo, autor FROM lista_larga WHERE anio = 2023"]
        params = []  # Parámetros seguros (anti SQL injection)
        
        # Añadir filtro de título si se proporciona
        if titulo:
            params.append(f"%{titulo}%")
            query_parts.append(f"AND LOWER(titulo) LIKE LOWER(${len(params)})")
        
        # Añadir filtro de autor si se proporciona
        if autor:
            params.append(f"%{autor}%")
            query_parts.append(f"AND LOWER(autor) LIKE LOWER(${len(params)})")
        
        # Ordenar y limitar
        query_parts.append("ORDER BY titulo ASC LIMIT 100;")
        query = " ".join(query_parts)
        
        # Ejecutar query (con parámetros es seguro contra SQL injection)
        if params:
            result = await db.fetch(query, *params)
        else:
            result = await db.fetch(query)
        
        # Construir HTML
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
                input {{ padding: 5px; width: 200px; margin-right: 10px; }}
                button {{ padding: 5px 15px; }}
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
            html += "<p style='color: #999;'>Sin resultados</p>"
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="background: #1a1a2e; color: red; padding: 20px;">
            <h1>Error: {str(e)}</h1>
        </body>
        </html>
        """


# ============================================================================
# RUTA 4: GET /titulos - Listar todos los títulos sin filtros
# ============================================================================
@app.get("/titulos")
async def mostrar_titulos(
    request: Request,
    db=Depends(get_db)  # Inyecta conexion BD
):
    """Obtiene TODOS los títulos del 2023 sin filtros"""
    # Consultar todos los títulos
    titulos = await buscar_titulos(db)

    # Renderizar template
    return templates.TemplateResponse(
        "titulos.html",
        {
            "request": request,
            "titulos": titulos
        }
    )


@app.get("/api/titulos-2023")
async def get_titulos_2023(db: asyncpg.Connection = Depends(get_db)):
    """
    Retorna JSON con título y autor de lista_larga donde anio = 2023
    """
    try:
        query = """
            SELECT titulo, autor
            FROM lista_larga
            WHERE anio = 2023;
        """
        filas = await db.fetch(query)
        return [dict(fila) for fila in filas]
    except Exception as e:
        logger.error(f"Error al consultar títulos 2023: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al consultar títulos: {str(e)}"
        )