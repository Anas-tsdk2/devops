# quiz-app


![CI](https://github.com/InesR91/projet-devops/actions/workflows/ci.yml/badge.svg)

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


# Phase 3 – Livraison continue (CD)

**Objectif :** Déployer automatiquement l’application sur Kubernetes après validation du code, pour que les dernières modifications soient directement disponibles.

## 1 Déploiement sur Kubernetes

Des manifestes Kubernetes ont été créés pour chaque composant de l’application :

- **Backend (API)** : Deployment + Service.
- **Frontend (UI)** : Deployment + Service.
- **Base de données** : Deployment + PersistentVolumeClaim pour la persistance des données.

Un **Helm Chart** simple a été mis en place pour faciliter le déploiement et les mises à jour. Les variables d’environnement et les secrets sont configurés pour garantir la connectivité entre les composants et la sécurité des informations sensibles.

## 2 Pipeline de livraison continue

Le pipeline CI existant a été étendu pour inclure la livraison continue. Chaque merge sur la branche principale déclenche automatiquement :

1. L’exécution des tests unitaires et d’intégration.  
2. Le déploiement sur le cluster Kubernetes via `kubectl apply` ou `helm upgrade`.

Seules les modifications validées par les tests sont déployées, assurant la stabilité du cluster.

## 3 Vérifications

Après le déploiement, les points suivants ont été vérifiés :

- Le backend communique correctement avec la base de données.  
- Le frontend accède au backend sans problème.  
- Les mises à jour se propagent correctement lors d’un push sur la branche principale.

## 5 Résultat

La livraison continue est opérationnelle et entièrement automatisée. L’application peut être déployée automatiquement à chaque mise à jour du code, avec un backend connecté à la base de données et un frontend fonctionnel. Les manifestes et le Helm Chart assurent un déploiement reproductible et modulable pour différents environnements.
