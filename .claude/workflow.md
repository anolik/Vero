# Workflow — Reference Document

> **SOURCE OF TRUTH:** `.claude/feature-list.json`
> Ce fichier décrit les phases planifiées et les regroupements de tâches.
> Pour le statut actuel, utiliser `feature-list.json` et le skill `project-coding`.
> Ce fichier N'EST PAS mis à jour pendant l'implémentation.

## Phase 1: Foundation (Jours 1-3)

### Task 1.1: Structure projet FastAPI
**Agent:** backend-developer (sonnet)
**Feature IDs:** F001
**Checkpoint:** `uvicorn main:app --reload` démarre sans erreur

### Task 1.2: Schéma de base de données
**Agent:** backend-developer (sonnet)
**Feature IDs:** F002
**Checkpoint:** Tables créées, seed data insérée

### Task 1.3: Système de tokens UUID
**Agent:** backend-developer (sonnet) + security-engineer (sonnet)
**Feature IDs:** F003
**Checkpoint:** Token valide → accès, invalide → 404, expiré → 410

### Task 1.4: Textes pré-rédigés
**Agent:** prompt-engineer (opus)
**Feature IDs:** F013
**Checkpoint:** 15 textes en DB (5 catégories × 3 variantes)

---

## Phase 2: Admin (Jours 3-5)

### Task 2.1: Dashboard admin
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F004
**Checkpoint:** `/admin` avec HTTP Basic Auth, tableau de sessions

### Task 2.2: Création de session
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F005
**Checkpoint:** Formulaire crée session + affiche lien unique

---

## Phase 3: Formulaire représentant (Jours 5-9)

### Task 3.1: Consentement Loi 25
**Agent:** fullstack-developer (sonnet) + security-engineer (sonnet)
**Feature IDs:** F006
**Checkpoint:** Consentement enregistré, redirect vers étape 1

### Task 3.2: Étape 1 — Sélection des textes
**Agent:** fullstack-developer (opus)
**Feature IDs:** F007
**Checkpoint:** 5 catégories × 3 cartes, sélection + personnalisation

### Task 3.3: Étape 2 — Informations personnelles
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F008
**Checkpoint:** Nom, prénom, email validés et sauvegardés

### Task 3.4: Étape 3 — Branding
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F009
**Checkpoint:** Logo uploadé, couleurs sélectionnées

### Task 3.5: Étape 4 — Domaine
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F010
**Checkpoint:** Domaine existant ou souhaité sauvegardé

### Task 3.6: Confirmation et récapitulatif
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F011
**Checkpoint:** Récap complet, statut → completed

### Task 3.7: UX du wizard
**Agent:** frontend-developer (sonnet)
**Feature IDs:** F014, F015, F016
**Checkpoint:** Stepper, reprise session, messages d'erreur

---

## Phase 4: Export et finition (Jours 9-11)

### Task 4.1: Export JSON
**Agent:** backend-developer (sonnet)
**Feature IDs:** F012, F019
**Checkpoint:** JSON valide avec toutes les sections, téléchargement fichier

### Task 4.2: Détails session admin
**Agent:** fullstack-developer (sonnet)
**Feature IDs:** F017
**Checkpoint:** Page détail avec toutes les données + logo

### Task 4.3: Landing page et responsive
**Agent:** frontend-developer (sonnet)
**Feature IDs:** F018, F020
**Checkpoint:** Page accueil, formulaire utilisable sur mobile
