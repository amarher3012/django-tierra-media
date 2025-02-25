

# Usa una imagen base ligera de Python
FROM python:3.13-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar paquetes como psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crea un usuario para evitar correr la app como root
RUN groupadd -g 1000 django && useradd -m -u 1000 -g django django

# Copia el archivo de dependencias antes de copiar el código (mejora la caché de Docker)
COPY requirements.txt .

# Instala las dependencias de Python globalmente sin usar `--user`
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY . .

# Da permisos al usuario para evitar problemas con volúmenes
RUN chown -R django:django /app

# Cambia al usuario no root
USER django
