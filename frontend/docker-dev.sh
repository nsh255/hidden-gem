#!/bin/bash
# Este script inicia el frontend en modo de desarrollo dentro de un contenedor

# Construir la imagen de desarrollo
docker build -t hidden-gem-frontend-dev -f Dockerfile.dev .

# Ejecutar el contenedor en modo de desarrollo
docker run --rm -it \
  -v $(pwd):/app \
  -v /app/node_modules \
  -p 4200:4200 \
  --network hidden-gem-network \
  hidden-gem-frontend-dev
