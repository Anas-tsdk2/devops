# quiz-app

![CI](https://github.com/InesR91/projet-devops/actions/workflows/ci.yml/badge.svg)

# Phase 1 –  Initialisation et déploiement de l’application

##  Installer et configurer Minikube en local
J'ai suivi la [documentation](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download) présente sur le site de minikube.

##  Créer un simple backend (API REST, par exemple) et un frontend minimal.
L'application de quiz composée d’un frontend Vue.js, d’un backend Flask et d’une base de données SQLite, entièrement dockerisée.

#### __L'architecture du projet__ :
```quiz-app/
├── quiz-api/    # Backend Flask
├── quiz-ui/     # Frontend Vue.js
└── docker-compose.yml
```

## Conteneuriser ces deux composants (Dockerfiles) :

#### __Dockerisation__ :
__Backend__ :
* Image basée sur python:3.10-alpine
* Serveur Flask lancé avec Gunicorn
* Base de données SQLite stockée dans un volume Docker afin d’assurer la persistance des données
* Utilisation de variables d’environnement pour configurer le chemin de la base de données

__Frontend__ :

* Build du projet Vue.js avec Node.js
* Application servie en production via Nginx
* Communication avec l’API Flask via le réseau Docker

## Déployer la base de données (conteneur local ou service managé).

_À la racine du projet :_
```
docker-compose build
docker-compose up
```

_Accès à l’application :_

Frontend : http://localhost:8080
Backend API : http://localhost:5000

_Sécurité :_

* Authentification via JWT
* Certaines routes sont protégées par un token d’authentification
* Mot de passe admin configurable via variable d’environnement

# Phase 2 – CI/CD et tests automatisés

Pour la phase 2 du projet **Quiz API / Quiz UI**, j’ai réalisé les étapes suivantes :

## 1 Écriture des tests unitaires et d’intégration

- Création de tests pour toutes les routes de l’API (`/`, `/login`, `/questions`, `/participations`, `/quiz-info`, etc.) avec **pytest**.
- Utilisation de fixtures pour :
  - Le client Flask (`client`) pour simuler les requêtes HTTP.
  - L’authentification (`auth_header`) en mockant le token.
- Utilisation de **pytest-mock** pour mocker les appels à la base de données (`question_dao`) afin de tester les routes indépendamment de la base réelle.
- Vérification des cas :
  - Succès et échec du login.
  - Accès autorisé et non autorisé aux endpoints protégés.
  - Création, récupération, modification et suppression des questions.
  - Soumission et suppression des participations.

## 3 Dockerisation

- Création d’un `Dockerfile` pour l’API :
  - Image `python:3.10-alpine`.
  - Installation des dépendances via `requirements.txt`.
  - Configuration des variables d’environnement (`FLASK_ENV`, `FLASK_APP`, `DATABASE_PATH`).
  - Lancement de l’API avec **Gunicorn**.
- Création du dossier `instance` pour la base SQLite.

## 4 Mise en place de l’intégration continue (GitHub Actions)

- Ajout d’un workflow `.github/workflows/ci.yml` à la racine du projet pour la CI.
- Workflow configuré pour :
  - Cloner le dépôt (`actions/checkout`).
  - Installer Python et les dépendances.
  - Lancer les tests pour **quiz-api**.
- Correction des chemins pour que GitHub Actions trouve correctement le `requirements.txt` (`working-directory: quiz-api`).
- Vérification que le workflow est vert après chaque push sur la branche `main`.

## 5 Résultat

- Tous les tests unitaires et d’intégration passent localement.
- CI GitHub Actions fonctionne correctement avec installation des dépendances et exécution des tests.
- L’API est maintenant dockerisée et prête pour déploiement, avec tests automatisés garantissant la stabilité à chaque modification.
