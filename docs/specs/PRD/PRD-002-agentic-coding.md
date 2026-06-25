# PRD-002: Développement Agentic Coding

## 📌 Métadonnées
- **ID**: PRD-002
- **Type**: Méthodologie
- **Auteurs**: Fatima
- **Date**: 2026-06-25
- **Statut**: Draft
- **Version**: 1.0.0
- **Relations**: Lié à `PRD-001` (infrastructure)

## 🎯 Objectif
Mettre en place un workflow de développement **piloté par des agents** (Vibe CLI) pour :
- Automatiser les tâches répétitives
- Standardiser les processus
- Accélérer le développement

---

## 📋 Fonctionnalités

### F1: Commandes Agent Todo
**Description** : Permettre aux utilisateurs d'interagir avec les todos via des commandes naturelles.

#### Scénarios
| ID    | Description                                      | Priorité | Statut  | Code lié |
|-------|--------------------------------------------------|----------|---------|----------|
| F1.1  | `/todo add {titre}` pour ajouter un todo          | P0       | ✅      | `.vibe/commands/todo.json` |
| F1.2  | `/todo list` pour lister les todos               | P0       | ✅      | `.vibe/commands/todo.json` |
| F1.3  | `/todo delete {id}` pour supprimer un todo        | P0       | ✅      | `.vibe/commands/todo.json` |

---

### F2: Workflows Agent
**Description** : Automatiser les workflows courants.

#### Scénarios
| ID    | Description                                      | Priorité | Statut  | Code lié |
|-------|--------------------------------------------------|----------|---------|----------|
| F2.1  | Lint + test automatique après modification      | P0       | ✅      | `.husky/pre-commit` |
| F2.2  | Génération de documentation auto                | P1       | ❌      | À implémenter |
| F2.3  | Détection des erreurs de syntaxe JSON          | P1       | ✅      | `.prettierrc` |

---

## ✅ Critères d'Acceptance
- [x] Les commandes `/todo` fonctionnent sans erreur
- [x] Le pre-commit exécute `lint:all`
- [ ] Un agent peut générer de la documentation à partir du code
- [ ] Un agent peut décomposer une tâche en sous-tâches

---

## 🔗 Liens vers le Code
- **Vibe Commands** : `.vibe/commands/todo.json`
- **Git Hooks** : `.husky/pre-commit`
- **Lint Config** : `.prettierrc`, `.eslintrc.cjs`

---

## 🤖 Rôle de l'Agent
- **Todo Management** : Gérer les todos via des commandes naturelles
- **Code Review** : Vérifier la qualité du code avant commit
- **Documentation** : Générer/maintenir la documentation
