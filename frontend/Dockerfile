# Frontend Dockerfile
FROM node:14

WORKDIR /app/frontend

# Kopiert die package.json und installiert die Abhängigkeiten
COPY ./frontend/ .
RUN npm install

# Öffnet den Port für das React-Frontend
EXPOSE 3000

# Startet die React-Anwendung
CMD ["npm", "start"]
