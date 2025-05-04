#!/bin/bash
set -e

# Script de inicialización para PostgreSQL
# Crea la base de datos 'hidden_gem' si no existe

# Conectarse como usuario postgres
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE hidden_gem'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'hidden_gem');
EOSQL

echo "✅ Verificación de base de datos completada"
