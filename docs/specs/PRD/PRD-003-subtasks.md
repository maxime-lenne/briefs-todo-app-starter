# PRD-003: Sous-tâches et Dépendances

## 📌 Métadonnées
- **ID**: PRD-003
- **Type**: Fonctionnalité
- **Auteurs**: Fatima
- **Date**: 2026-06-25
- **Statut**: Draft
- **Version**: 1.0.0
- **Relations**: Dépend de PRD-001 (Docker), PRD-002 (Agentic)

## 🎯 Objectif
Permettre aux utilisateurs de :
1. **Décomposer** un todo en sous-tâches hiérarchiques
2. **Définir des dépendances** entre tâches (A bloque B)
3. **Visualiser** la progression globale

---

## 📋 Fonctionnalités

### F1: Gestion des Sous-tâches
**Description** : Structurer les todos en arborescence.

#### Scénarios
| ID    | Description | Priorité | Statut | Code lié |
|-------|-------------|----------|--------|----------|
| F1.1 | Champ `parent_id` dans le modèle `Todo` | P0 | ❌ | `api/app/models/todo.py` |
| F1.2 | Endpoint `GET /todos/{id}/subtasks` | P0 | ❌ | `api/app/routes/todos.py` |
| F1.3 | Affichage hiérarchique dans le frontend | P0 | ❌ | `web/src/lib/components/TodoItem.svelte` |
| F1.4 | Indentation visuelle (2 espaces par niveau) | P1 | ❌ | `web/src/lib/components/TodoList.svelte` |

---

### F2: Dépendances entre Tâches
**Description** : Gérer les relations "A bloque B".

#### Scénarios
| ID | Description | Priorité | Statut | Code lié |
|----|-------------|----------|--------|----------|
| F2.1 | Table `task_dependencies` (blocking_id, blocked_id) | P0 | ❌ | `api/app/models/dependency.py` |
| F2.2 | Empêcher la suppression d'une tâche bloquante | P0 | ❌ | `api/app/routes/todos.py` |
| F2.3 | Endpoint `GET /todos/{id}/dependencies` | P0 | ❌ | `api/app/routes/todos.py` |
| F2.4 | Visualisation des dépendances (graphe simple) | P2 | ❌ | `web/src/lib/components/DependencyGraph.svelte` |

---

### F3: Progression
**Description** : Calculer et afficher l'état d'avancement.

#### Scénarios
| ID | Description | Priorité | Statut | Code lié |
|----|-------------|----------|--------|----------|
| F3.1 | Calcul automatique du % de complétion | P1 | ❌ | `api/app/services/progress.py` |
| F3.2 | Afficher la progression dans le frontend | P1 | ❌ | `web/src/lib/components/ProgressBar.svelte` |
| F3.3 | Une tâche est complétée si toutes ses sous-tâches le sont | P1 | ❌ | `api/app/services/progress.py` |

---

## ✅ Critères d'Acceptance
- [ ] Une tâche peut avoir plusieurs sous-tâches (niveau illimité)
- [ ] Une sous-tâche ne peut pas être complétée si sa tâche parente ne l'est pas
- [ ] Une tâche bloquante ne peut pas être supprimée si une tâche bloquée existe
- [ ] L'interface affiche les sous-tâches avec une indentation visuelle
- [ ] L'interface affiche les dépendances (ex: "Bloqué par: Tâche X")

---

## 🔗 Liens vers le Code
- **Backend** : `api/app/models/todo.py`, `api/app/models/dependency.py`, `api/app/routes/todos.py`
- **Frontend** : `web/src/lib/components/TodoItem.svelte`, `web/src/lib/components/TodoList.svelte`

---

## 📊 Métriques
| Métrique | Valeur cible | Outil de mesure |
|----------|--------------|-----------------|
| Profondeur max des sous-tâches | 5 niveaux | Tests unitaires |
| Temps de calcul de la progression | < 100ms | Benchmark |

---

## 🏷️ Tags
`feature`, `todos`, `dependencies`, `subtasks`
