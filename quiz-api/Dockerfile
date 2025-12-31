# ---- Image Python ----
FROM python:3.10-alpine

# Répertoire interne
WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Créer dossier instance (pour la bdd sqlite)
RUN mkdir -p /app/instance

# Copier la base de données existante dans l'image
COPY instance/database.db /app/instance/database.db

# Variables d'environnement
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV FLASK_APP=app.py
ENV DATABASE_PATH=/app/instance/database.db

# Copier le code source
COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 5000

# Informations sur l'image
LABEL maintainer="assia" version="1.1"

# Démarrer via le script d'entrée
CMD ["./entrypoint.sh"]
