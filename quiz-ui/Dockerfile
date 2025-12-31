# Étape 1 : Construction (build) du projet avec Node.js
FROM node:lts-alpine as build

# Installation de Vue CLI (pour build le projet)
RUN npm install -g @vue/cli

# Répertoire de travail dans le container
WORKDIR /app

# Copie des fichiers de dépendances
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du reste du code source
COPY . .

# Variable d'environnement : adresse de ton API Flask
# (en local, ton API tourne sur http://localhost:5000)
ENV VITE_API_URL=http://backend-service:3000


# Build de l'application Vue.js (sortie = /app/dist)
RUN npm run build

# Étape 2 : Création de l'image finale avec Nginx
FROM nginx

# Copie des fichiers buildés dans le dossier Nginx
COPY --from=build /app/dist /usr/share/nginx/html
