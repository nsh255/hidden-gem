from fastapi import APIRouter, BackgroundTasks, HTTPException
import subprocess
from pathlib import Path
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/run-spider", status_code=202)
async def run_spider(background_tasks: BackgroundTasks):
    """
    Ejecuta el spider de Steam en segundo plano
    """
    def execute_spider():
        try:
            # Cambia al directorio donde se encuentra el archivo scrapy.cfg
            project_dir = Path(__file__).parent.parent.parent
            os.chdir(project_dir)
            
            # Ejecuta el spider usando subprocess
            result = subprocess.run(
                ["scrapy", "crawl", "games_spider", "-o", "games.json"],
                capture_output=True,
                text=True
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
    """
    Ejecuta el spider de Steam de forma síncrona y devuelve el resultado
    """
    try:
        # Cambia al directorio donde se encuentra el archivo scrapy.cfg
        project_dir = Path(__file__).parent.parent.parent
        os.chdir(project_dir)
        
        logger.info(f"Ejecutando spider desde: {os.getcwd()}")
        
        # Ejecuta el spider usando subprocess
        result = subprocess.run(
            ["scrapy", "crawl", "games_spider", "-o", "games.json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error al ejecutar el spider: {result.stderr}")
            return {
                "success": False,
                "message": "Error al ejecutar el spider",
                "error": result.stderr,
                "output": result.stdout
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
