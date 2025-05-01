## Instrucciones para ejecutar el proyecto

### Requisitos
- Python 3.9+
- PostgreSQL
- Docker (opcional)

### Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/hidden-gem.git
   cd hidden-gem
   ```

2. Configura el entorno virutal:
    ```bash
    python -m venv venv
    source venv\Scripts\activate
    pip install -r backend\requirements.txt
    ```

3. Configura la base de datos:
    ```bash
    psql -U postgres -c "CREATE DATABASE hiddengem;"
    ```