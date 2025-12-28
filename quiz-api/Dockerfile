# ---- Image Python ----
FROM python:3.10-alpine

# Répertoire interne
WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Créer dossier instance (pour la bdd sqlite)
RUN mkdir -p /app/instance

# Variables d'env
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV FLASK_APP=app.py
ENV DATABASE_PATH=/app/instance/database.db

# Copier le code
COPY . .

EXPOSE 5000

# Informations sur l'image
LABEL maintainer="assia" version="1.1"

# Démarrer gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers=3", "app:app"]