# ADR-001: Utiliser FastAPI pour le Backend

## 📌 Statut
✅ **Accepté**

## 📅 Date
2026-06-25

## 👥 Auteurs
Fatima

## 🎯 Contexte
Nous avions besoin d'un framework backend pour notre application Todo.
Les options considérées :
- **Django** : Trop lourd pour une API simple
- **Flask** : Moins structuré, pas de validation native
- **FastAPI** : Moderne, performant, validation native, OpenAPI intégré

## ⚖️ Décision
**Utiliser FastAPI** pour le backend.

## ✅ Conséquences
### Positives
- **Validation automatique** des requêtes/réponses (Pydantic)
- **Documentation OpenAPI** générée automatiquement (`/openapi.json`, `/docs`)
- **Performances** élevées (basé sur Starlette)
- **Typage fort** avec Python

### Négatives
- Courbe d'apprentissage pour les débutants
- Moins mature que Django (mais largement adopté)

## 🔗 Liens
- **Code** : `api/app/main.py`
- **Documentation** : [FastAPI Docs](https://fastapi.tiangolo.com/)
- **PRD lié** : PRD-001 (Infrastructure Docker)
