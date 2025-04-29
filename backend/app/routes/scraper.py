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
            # Cambia al directorio donde se encuentra el spider
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
            else:
                logger.info("Spider ejecutado correctamente")
                
        except Exception as e:
            logger.exception(f"Error inesperado al ejecutar el spider: {str(e)}")

    background_tasks.add_task(execute_spider)
    return {"message": "Spider iniciado en segundo plano"}
