from fastapi import APIRouter, BackgroundTasks, HTTPException
import subprocess
from pathlib import Path
import os
import logging
import sys

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run-spider", status_code=202)
async def run_spider(background_tasks: BackgroundTasks):
    """
    Ejecuta el spider de Steam en segundo plano
    """
    def execute_spider():
        try:
            # Obtiene el directorio raíz del proyecto
            project_dir = Path(__file__).parent.parent.parent
            os.chdir(project_dir)
            
            logger.info(f"Ejecutando spider desde: {os.getcwd()}")
            
            # Ejecuta el spider usando crawl en lugar de runspider
            result = subprocess.run(
                [
                    sys.executable, 
                    "-m", 
                    "scrapy", 
                    "crawl", 
                    "games_spider",
                ],
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(project_dir)}
            )
            
            if result.returncode != 0:
                logger.error(f"Error al ejecutar el spider: {result.stderr}")
                return {"success": False, "message": "Error al ejecutar el spider", "error": result.stderr}
            else:
                logger.info("Spider ejecutado correctamente")
                
        except Exception as e:
            logger.exception(f"Error inesperado al ejecutar el spider: {str(e)}")
    
    background_tasks.add_task(execute_spider)
    return {"message": "Spider iniciado en segundo plano"}

@router.post("/run")
async def execute_spider_sync():
    try:
        # En Docker, el directorio de trabajo ya debería ser /app
        logger.info(f"Ejecutando spider desde: {os.getcwd()}")
        
        # Ejecuta el spider directamente desde el entorno Docker
        result = subprocess.run(
            [
                "python", 
                "-m", 
                "scrapy", 
                "crawl", 
                "games_spider",
            ],
            capture_output=True,
            text=True,
            env={**os.environ}
        )
        
        # Mostrar detalles completos para depuración
        logger.info(f"Salida del comando: {result.stdout}")
        logger.info(f"Error del comando: {result.stderr}")
        
        if result.returncode != 0:
            logger.error(f"Error al ejecutar el spider: {result.stderr}")
            return {
                "success": False,
                "message": "Error al ejecutar el spider",
                "error": result.stderr,
                "output": result.stdout,
                "cwd": os.getcwd()
            }
        else:
            logger.info("Spider ejecutado correctamente")
            return {
                "success": True,
                "message": "Spider ejecutado correctamente",
                "output": result.stdout
            }
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Error inesperado al ejecutar el spider: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar el spider: {error_msg}"
        )