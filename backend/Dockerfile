# Backend Dockerfile
FROM python:3.9

WORKDIR /app

# Kopiert die requirements-Datei aus dem Hauptverzeichnis
COPY requirements.txt .

# Installiert die Abhängigkeiten
RUN pip install --default-timeout=1000 -r requirements.txt

# Kopiert den Rest des Backend-Codes aus dem aktuellen Verzeichnis
COPY backend/ .

# Öffnet den Port für Uvicorn
EXPOSE 8000

# Startet die FastAPI-Anwendung
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
