import asyncio
import asyncpg

DATABASE_URL = 'postgresql://estudiantes:npg_FtxeYOVU8yD7@ep-withered-wind-apq7hmfj-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require'

async def get_titulos():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        filas = await conn.fetch('SELECT titulo, autor FROM lista_larga WHERE anio = 2023 LIMIT 20')
        print("\n📚 LIBROS DISPONIBLES PARA BUSCAR (Año 2023):\n")
        for i, fila in enumerate(filas, 1):
            print(f"{i}. {fila['titulo']}")
            print(f"   Autor: {fila['autor']}\n")
    finally:
        await conn.close()

asyncio.run(get_titulos())
