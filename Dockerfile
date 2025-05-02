FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY backend/app ./app

COPY backend/scrapy.cfg /app/scrapy.cfg

# Variable para indicar entorno
ENV ENVIRONMENT=production

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar las migraciones y luego la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
