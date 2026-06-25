# PRD-001: Infrastructure Docker

## 📌 Métadonnées
- **ID**: PRD-001
- **Type**: Infrastructure
- **Auteurs**: Fatima
- **Date**: 2026-06-25
- **Statut**: Draft
- **Version**: 1.0.0

## 🎯 Objectif
Fournir une infrastructure Docker pour :
- Développer localement avec un environnement isolé
- Déployer l'application en production
- Garantir la cohérence entre les environnements

---

## 📋 Fonctionnalités

### F1: Environnement de Développement
**Description** : Permettre aux développeurs de lancer l'application localement avec Docker.

#### Scénarios
| ID    | Description                                      | Priorité | Statut  | Code lié               |
|-------|--------------------------------------------------|----------|---------|------------------------|
| F1.1  | Lancer les services avec `docker compose up`      | P0       | ✅      | `docker-compose.yml`   |
| F1.2  | Accéder à l'API sur `http://localhost:8000`      | P0       | ✅      | `api/Dockerfile`      |
| F1.3  | Accéder au frontend sur `http://localhost:5173`   | P0       | ✅      | `web/Dockerfile`      |

---

### F2: Build de Production
**Description** : Générer des images Docker optimisées pour la production.

#### Scénarios
| ID    | Description                                      | Priorité | Statut  | Code lié               |
|-------|--------------------------------------------------|----------|---------|------------------------|
| F2.1  | Images multi-stage pour réduire la taille       | P0       | ✅      | `api/Dockerfile`      |
| F2.2  | Utilisateur non-root pour la sécurité           | P0       | ✅      | `api/Dockerfile`      |

---

## ✅ Critères d'Acceptance
- [ ] `docker compose up` lance tous les services sans erreur
- [ ] L'API répond à `GET /todos` (test: `curl http://localhost:8000/todos`)
- [ ] Le frontend est accessible et interagit avec l'API

---

## 🔗 Liens vers le Code
- **Backend** : `api/Dockerfile`, `docker-compose.yml`
- **Frontend** : `web/Dockerfile`
