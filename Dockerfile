FROM python:3.12-slim

# Installing only what we need. En caso de problemas de SSL o red, se puede
# descomentar la instalación de ca-certificates o herramientas de debug.
# RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

# Nota: uvicorn recarga en desarrollo con "--reload", pero en contenedor
# lo dejamos simple. En local se puede usar "uvicorn app.api:app --reload".
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8080"]
