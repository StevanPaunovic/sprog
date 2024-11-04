# Frontend Dockerfile
FROM node:14

WORKDIR /app

# Kopiert die package.json und installiert die Abhängigkeiten
COPY package*.json ./
RUN npm install

# Kopiert den Rest des Frontend-Codes
COPY frontend/ .

# Öffnet den Port für das React-Frontend
EXPOSE 3000

# Startet die React-Anwendung
CMD ["npm", "start"]
