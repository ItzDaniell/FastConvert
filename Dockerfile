# Usa una imagen base ligera de Python
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /src

# Instala las dependencias del sistema necesarias para Django
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala las dependencias del sistema necesarias para yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod a+rx /usr/local/bin/yt-dlp

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo el proyecto al contenedor
COPY . .

# Evita que Python genere archivos .pyc (bytecode) en el contenedor
ENV PYTHONDONTWRITEBYTECODE 1

# Evita que Python bufferice la salida (stdout y stderr) para que los logs se muestren en tiempo real
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

# Comando de inicio: ejecuta migraciones, collectstatic y luego levanta el servidor
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]