# ADR-002: Utiliser SvelteKit pour le Frontend

## 📌 Statut
✅ **Accepté**

## 📅 Date
2026-06-25

## 👥 Auteurs
Fatima

## 🎯 Contexte
Nous avions besoin d'un framework frontend moderne pour notre application Todo.
Options considérées :
- **React** : Populaire mais complexe (JSX, hooks)
- **Vue** : Simple mais moins performant
- **SvelteKit** : Léger, pas de virtual DOM, routage intégré

## ⚖️ Décision
**Utiliser SvelteKit** pour le frontend.

## ✅ Conséquences
### Positives
- **Pas de virtual DOM** → Meilleure performance
- **Routage intégré** (fichiers = routes)
- **SSG/SSR/CSR** supporté nativement
- **Intégration facile** avec Tailwind CSS

### Négatives
- Communauté plus petite que React
- Moins de libraries tierces

## 🔗 Liens
- **Code** : `web/src/routes/`
- **Documentation** : [SvelteKit Docs](https://kit.svelte.dev/)
