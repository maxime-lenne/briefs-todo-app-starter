# Brief Métier : Dockeriser une app To-Do

### Contexte Professionnel

TechSolve, une entreprise reconnue dans le développement de solutions digitales pour la gestion de projets, 
est en pleine transformation numérique afin de répondre aux exigences croissantes de ses clients. 
Actuellement, l’application To-Do, utilisée quotidiennement par plus de 200 collaborateurs pour la gestion de tâches internes, 
repose sur une architecture monolithique composée d’une API FastAPI connectée à une base SQLite, 
et d’une interface utilisateur développée avec Svelte.

Face aux défis de scalabilité, de sécurité et de maintenance, TechSolve a décidé de moderniser son infrastructure en passant à une solution conteneurisée. 
L’objectif est de migrer la base de données vers PostgreSQL pour une gestion plus robuste des données en production et de dockeriser à la fois l’API et l’application Svelte. 
Cette démarche permettra non seulement d’améliorer la réactivité des déploiements et de faciliter la gestion des environnements, 
mais également de garantir une meilleure isolation des services et une orchestration sécurisée via Docker Compose.

## Partie 1 : Créer et orchestrer une application multi-conteneurs

### Besoins à Réaliser

1. **Mise en place de la base de données PostgreSQL dans Docker :**
    - Télécharger et configurer une image officielle PostgreSQL.
    - Créer une base de données fonctionnelle adaptée à l’application.
    - Gérer la persistance des données (volumes Docker).
2. **Dockerisation de l’API FastAPI :**
    - Adapter le code existant pour connecter l’API à PostgreSQL.
    - Créer un Dockerfile pour construire l’image Docker de l’API.
    - Optimiser l’image en respectant les bonnes pratiques (gestion des dépendances, exécution via Uvicorn, etc.).
    - Push l’image sur Docker Hub pour une utilisation future
3. **Dockerisation de l’Application Svelte :**
    - Créer un Dockerfile pour construire l’image Docker de l’application Svelte.
    - S’assurer que l’interface communique correctement avec l’API.
    - Push l’image sur Docker Hub pour une utilisation future
4. **Orchestration avec Docker Compose :**
    - Créer un fichier `docker-compose.yml` pour lier les trois conteneurs (PostgreSQL, API FastAPI, et Application Svelte).
    - Configurer les réseaux internes, les variables d’environnement et les dépendances de démarrage.

### Détails Techniques et Considérations Importantes

- **Migration de la Base de Données :**
    - Adapter le code existant (notamment dans `database.py`) pour qu’il se connecte à PostgreSQL.
- **Dockerfile pour l’API :**
    - Utiliser une image de base Python officielle.
    - Installer les dépendances (FastAPI, SQLAlchemy, etc.).
    - Configurer l’exécution avec Uvicorn.
    - Exposer le port approprié pour la communication.
- **Dockerfile pour Svelte :**
    - Utiliser une image Python adaptée.
    - Installer Svelte et les autres bibliothèques nécessaires.
    - Configurer le point d’entrée pour lancer l’application.
- **Réseaux :**
    - Dans le fichier Docker Compose, définir un réseau interne pour que les conteneurs communiquent entre eux.
    - Assurer une gestion des volumes pour la persistance des données PostgreSQL.
- **Déploiement et Tests :**
    - Tester chaque conteneur individuellement à l’aide de leurs Dockerfiles respectifs.
    - Une fois les conteneurs validés, tester l’orchestration complète via Docker Compose pour s’assurer que l’API et l’interface Svelte interagissent correctement avec la base de données PostgreSQL.

---

## Partie 2 : Sécuriser les conteneurs et optimiser la gestion des ressources

### 1. Sécurisation des Conteneurs et des Données

- **PostgreSQL :**
    - Définir un utilisateur dédié avec les permissions minimales requises pour l'application.
    - Utiliser des variables d'environnement sécurisées pour le stockage des mots de passe et des configurations sensibles.
    - Restreindre les accès réseau en configurant PostgreSQL pour accepter uniquement les connexions provenant du réseau Docker interne.
- **API FastAPI :**
    - Gérer les secrets d'accès à la base de données avec des variables d'environnement.
    - Appliquer les bonnes pratiques de sécurité Docker (éviter de lancer en tant que root, limiter les privilèges).
- **Application Svelte :**
    - S'assurer que Svelte ne soit accessible que via le reverse proxy Docker (éviter l'exposition directe).
    - Mettre en place des configurations adaptées pour éviter les fuites d'informations sensibles.

### 2. Gestion des Ressources et Optimisation

- **PostgreSQL :**
    - Définir explicitement les ressources CPU et mémoire dans Docker Compose pour éviter les saturations.
    - Utiliser des volumes Docker dédiés avec gestion explicite pour garantir la persistance et faciliter les sauvegardes.
- **API FastAPI :**
    - Configurer les limites des ressources disponibles (CPU, mémoire) via Docker Compose.
    - Optimiser l'image Docker pour réduire sa taille (utiliser des images officielles légères comme Python Alpine, nettoyer les caches après l'installation des dépendances).
- **Application Svelte :**
    - Définir clairement les besoins en ressources CPU et mémoire.
    - Mettre en place un système de gestion des logs pour faciliter la maintenance et le suivi des performances (facultatif).

### 3. Orchestration Sécurisée avec Docker Compose

- **Sécurisation du réseau Docker :**
    - Créer un réseau interne isolé (bridge interne) empêchant tout accès externe non autorisé.
    - Vérifier que seuls les conteneurs nécessaires puissent communiquer entre eux (isolation stricte des services).
    - Utiliser des variables d’environnement pour gérer les informations sensibles (mot de passe de la BDD, configuration de l’API, etc.).
- **Gestion et Politique de Redémarrage :**
    - Configurer une politique de redémarrage automatique en cas de panne pour garantir la disponibilité des services.
    - Mettre en place un monitoring basique (logs centralisés ou métriques simples) pour surveiller l’état des conteneurs et anticiper les problèmes de performance ou de sécurité (facultatif).

### 4. Tests et Validation Sécurisée

- Réaliser des tests de sécurité basiques (scan d’image Docker avec un outil comme Trivy pour détecter les vulnérabilités).
- Vérifier la robustesse de l'isolation réseau avec des tests pratiques simples (tentative de connexion externe non autorisée, etc.).

---

### Livrables Attendus

- **Code Source et Dockerfiles :**
    - Dockerfile pour l’API FastAPI.
    - Dockerfile pour l’application Svelte.
    - Fichier `docker-compose.yml` orchestrant les trois conteneurs.
    - Éventuelles modifications du code.
- **Documentation :**
    - Un README.md détaillant :
        - Les étapes d’installation et d’exécution des conteneurs.
        - La configuration nécessaire (variables d’environnement, volumes, ports, etc.).
        - Les choix techniques et les éventuelles limitations rencontrées.

### Critères de Performance et Bonnes Pratiques

- **Fonctionnalités Obligatoires :**
    - Base de données PostgreSQL opérationnelle dans Docker.
    - API FastAPI dockerisée capable de gérer les opérations CRUD avec PostgreSQL.
    - Application Svelte dockerisée interagissant avec l’API.
    - Docker Compose assurant une orchestration sécurisée et fluide entre les conteneurs.
- **Qualité du Code et Sécurité :**
    - Code propre et bien structuré avec des commentaires explicatifs.
    - Respect des standards de programmation et des bonnes pratiques Docker.
    - Sécurisation de la communication entre conteneurs et gestion appropriée des accès à la base de données.
- **Documentation :**
    - Documentation complète permettant à toute personne de reproduire et comprendre le déploiement.

### Ressources Supplémentaires

- **Docker et Docker Compose :**
    - [Documentation Docker](https://docs.docker.com/)
    - [Documentation Docker Compose](https://docs.docker.com/compose/)
- **FastAPI et Svelte :**
    - [FastAPI Official Documentation](https://fastapi.tiangolo.com/)
    - [Svelte Documentation](https://docs.Svelte.io/)

---

## Partie 3 : Mettre en place une pipeline CI/CD avec GitHub Actions

### Objectif

Automatiser la validation et la livraison des images Docker via GitHub Actions afin de garantir
que chaque modification du code passe par les mêmes contrôles qualité avant d’être publiée, et
que les images publiées soient versionnées et stockées dans le registre Docker GitHub
(`ghcr.io`).

### Étapes à Réaliser

1. **Stage `validate`** (déclenché sur chaque push et chaque pull request)
    - **API FastAPI :**
        - Exécuter au minimum un outil de lint (par exemple `ruff` ou `flake8`).
        - Exécuter les tests unitaires (par exemple `pytest`).
    - **Application Svelte :**
        - Exécuter au minimum un outil de lint (`svelte-check`, `eslint`, etc.).
        - Exécuter les tests unitaires (`vitest` ou équivalent).
    - L’étape échoue si l’une des vérifications ne passe pas. Aucune image ne doit être
      construite tant que `validate` n’est pas vert.
2. **Stage `build`** (déclenché après un `validate` réussi sur la branche par défaut ou sur un
    tag de release)
    - Construire les images Docker de l’API et du Web.
    - Tagger chaque image avec :
        - le SHA court du commit (`sha-<short>`),
        - la version sémantique en cas de tag git (`vX.Y.Z`),
        - `latest` sur la branche principale.
    - Pousser les images vers le **GitHub Container Registry** (`ghcr.io/<owner>/<repo>-api` et
      `ghcr.io/<owner>/<repo>-web`) en utilisant le `GITHUB_TOKEN` fourni par GitHub Actions.

### Bonnes Pratiques

- Utiliser le cache des dépendances (npm, pip) pour accélérer les jobs.
- Utiliser `docker/build-push-action` avec le cache de layers pour les builds.
- Restreindre les permissions du workflow au minimum nécessaire (`packages: write` pour le push
  ghcr, `contents: read` pour le checkout).
- Documenter dans le README la liste des images publiées et la manière de les consommer.

### Livrables supplémentaires attendus

- Un (ou plusieurs) workflow YAML dans `.github/workflows/`.
- Tests unitaires côté API et côté Web exécutables localement (`pytest`, `npm test`).
- Section CI/CD dans le `README.md` décrivant les stages et les images publiées.

---

## Partie 4 (Facultative) : Déployer une application multi-conteneur sur un système Cloud

### Objectif

Proposer une solution de déploiement cloud simple et gratuite pour héberger l'application multi-conteneurs (API FastAPI, Svelte et PostgreSQL) en utilisant **Railway**, une plateforme cloud facile d’accès.

### Étapes à Réaliser

1. **Création d’un projet sur Railway**
    - Créer un compte sur [https://railway.app](https://railway.app/).
    - Créer un nouveau projet.
2. **Déploiement de la base de données PostgreSQL**
    - Ajouter un **plugin PostgreSQL** depuis l'interface Railway.
    - Récupérer les **informations de connexion** (host, port, user, password, database).
    - Les intégrer dans les variables d’environnement du service FastAPI.
3. **Déploiement de l’API FastAPI**
    - Créer un service Railway en déployant l’image Docker de l’API.
    - Ajouter les **variables d’environnement** nécessaires à la connexion à PostgreSQL.
4. **Déploiement de l’application Svelte**
    - Créer un autre service pour Svelte en déployant l’image Docker de Svelte.
    - Ajouter une variable d’environnement pour pointer vers l’URL de l’API FastAPI déployée.
5. **Tests et Validation**
    - Vérifier que l’API FastAPI est accessible publiquement.
    - Vérifier que l’application Svelte interagit correctement avec l’API.
    - Tester les fonctionnalités CRUD via l’interface.

---

### Bonnes Pratiques et Limitations

- Bien vérifier que chaque service dispose de ses propres variables d’environnement (ne pas partager les secrets inutiles).
- Railway attribue un sous-domaine public à chaque service, à utiliser pour les connexions inter-services.
- Il est recommandé d’ajouter un fichier `.env.example` dans le projet pour documenter les variables utilisées.

---

### Livrables supplémentaires attendus (facultatif)

- Une section “Déploiement Cloud” dans le `README.md` expliquant comment déployer sur Railway.
- Capture(s) d’écran montrant l’API et l’interface Svelte en ligne.
- Lien public vers l’application déployée.
