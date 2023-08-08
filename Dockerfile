# Utilizamos una imagen base de Python que incluya el sistema operativo y Python instalado
FROM python:3.9

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos necesarios para la aplicación
COPY requirements.txt /app/
COPY app.py /app/

# Instalamos las dependencias de la aplicación
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto que usará la aplicación
EXPOSE 5000

# Ejecutamos la aplicación Flask cuando se inicie el contenedor
CMD ["python", "app.py"]
