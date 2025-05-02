from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
import subprocess
from pathlib import Path
import os
import logging
import sys
import time

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run-spider", status_code=202)
async def run_spider(background_tasks: BackgroundTasks, 
                    max_pages: int = Query(20, description="Número máximo de páginas a scrapear por categoría")):
    """
    Ejecuta el spider de Steam en segundo plano
    """
    def execute_spider():
        try:
            # Obtiene el directorio raíz del proyecto
            project_dir = Path(__file__).parent.parent.parent
            os.chdir(project_dir)
            
            logger.info(f"Ejecutando spider desde: {os.getcwd()}")
            logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'No definido')}")
            
            # Ejecuta el spider usando crawl en lugar de runspider
            cmd = [
                sys.executable, 
                "-m", 
                "scrapy", 
                "crawl", 
                "games_spider",
                "-s", f"CLOSESPIDER_PAGECOUNT={max_pages}",
                "-a", "max_games=2000",  # Aumentado a 2000
                "--logfile=spider_log.txt",
                "-s", "LOG_LEVEL=DEBUG"
            ]
            
            logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(project_dir)}
            )
            
            if result.returncode != 0:
                logger.error(f"Error al ejecutar el spider: {result.stderr}")
                # Guardar salida para depuración
                with open("spider_error.log", "w") as f:
                    f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
                logger.info("Error guardado en spider_error.log")
                return {"success": False, "message": "Error al ejecutar el spider", "error": result.stderr}
            else:
                logger.info("Spider ejecutado correctamente")
                # Guardar salida para referencia
                with open("spider_output.log", "w") as f:
                    f.write(result.stdout)
                logger.info("Salida guardada en spider_output.log")
                
        except Exception as e:
            logger.exception(f"Error inesperado al ejecutar el spider: {str(e)}")
    
    background_tasks.add_task(execute_spider)
    return {"message": "Spider iniciado en segundo plano"}

@router.post("/run")
async def execute_spider_sync(max_pages: int = Query(100, description="Número máximo de páginas a scrapear"),  # Aumentado a 100
                              max_games: int = Query(2000, description="Número máximo de juegos a extraer")):  # Aumentado a 2000
    try:
        start_time = time.time()
        logger.info(f"Ejecutando spider desde: {os.getcwd()}")
        
        # Ejecuta el spider directamente desde el entorno Docker
        cmd = [
            "python", 
            "-m", 
            "scrapy", 
            "crawl", 
            "games_spider",
            "-s", f"CLOSESPIDER_PAGECOUNT={max_pages}",
            "-a", f"max_games={max_games}",  # Añadimos el argumento de max_games
            "-s", "LOG_LEVEL=DEBUG"
        ]
        
        logger.info(f"Ejecutando comando: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ}
        )
        
        # Mostrar detalles completos para depuración
        logger.info(f"Tiempo de ejecución: {time.time() - start_time:.2f} segundos")
        
        # Guardar logs completos independientemente del resultado
        with open("spider_debug.log", "w") as f:
            f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
        
        if result.returncode != 0:
            logger.error(f"Error al ejecutar el spider: {result.stderr}")
            return {
                "success": False,
                "message": "Error al ejecutar el spider",
                "error": result.stderr,
                "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                "cwd": os.getcwd(),
                "execution_time": f"{time.time() - start_time:.2f} segundos"
            }
        else:
            logger.info("Spider ejecutado correctamente")
            return {
                "success": True,
                "message": "Spider ejecutado correctamente",
                "output": result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout,
                "execution_time": f"{time.time() - start_time:.2f} segundos"
            }
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Error inesperado al ejecutar el spider: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar el spider: {error_msg}"
        )