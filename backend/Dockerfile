# Backend Dockerfile
FROM python:3.9

RUN apt-get update && apt-get upgrade -y

WORKDIR /app/backend

# Kopiert die requirements-Datei aus dem Hauptverzeichnis
COPY ./backend/requirements.txt .

# Installiert die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiert den Rest des Backend-Codes aus dem aktuellen Verzeichnis
COPY ./backend .

# Öffnet den Port für Uvicorn
EXPOSE 8080

# Startet die FastAPI-Anwendung
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
