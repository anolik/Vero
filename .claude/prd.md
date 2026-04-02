# Product Requirements Document (PRD)

## Project Overview

- **Project Name:** Vero — Collecteur de sites web pour représentants
- **Description:** Application web permettant de collecter les informations nécessaires à la création de sites web pour les représentants en services financiers (fonds communs et assurance de personnes), puis de générer un JSON structuré pour import WordPress via WPEngine.
- **Problem Statement:** La création de sites web pour les représentants est un processus manuel, lent et sujet aux erreurs. Ce système automatise la collecte d'information et la préparation du contenu pour WordPress.
- **Target Users:** Équipe interne (admin) et représentants en services financiers
- **Project Tier:** 📦 Standard

## Related Documents

| Document | File | Status |
|----------|------|--------|
| BRD | `.claude/requirements/brd.md` | N/A |
| MRD | `.claude/requirements/mrd.md` | N/A |
| CRD | `.claude/requirements/crd.md` | N/A |
| FRD | `.claude/requirements/frd.md` | N/A |
| UIRD | `.claude/requirements/uird.md` | N/A |
| TRD | `.claude/requirements/trd.md` | N/A |
| QRD | `.claude/requirements/qrd.md` | N/A |
| SRS | `.claude/requirements/srs.md` | N/A |

---

## Brainstorm Summary

### Consensus
- **Token UUID4** dans l'URL comme unique mécanisme d'accès représentant (HIGH confidence)
- **Wizard/stepper 4 étapes** avec sauvegarde serveur par étape (POST/redirect)
- **Jinja2 SSR + Bootstrap 5 CDN** — pas de framework JS lourd
- **3 variantes de texte par catégorie** (tons: professionnel / chaleureux / concis)
- **JSON structuré** comme format d'export pour l'agent AI WordPress
- **HTTP Basic Auth** pour l'admin (suffisant pour démo)
- **Loi 25** : consentement explicite avec timestamp avant accès au formulaire

### Recommended Approach
Architecture simple FastAPI + Jinja2 + SQLite3, orientée démo mais extensible. UUID token pour l'accès représentant, wizard multi-étapes avec sauvegarde côté serveur, export JSON structuré pour agent AI.

### Alternatives Considered
- **HMAC signed tokens** : Plus sécurisé mais complexité excessive pour une démo (upgrade path pour production)
- **SPA React/Vue** : UX plus riche mais ajouterait un build step et de la complexité inutile
- **Pico.css** : Plus léger que Bootstrap mais manque de composants pour le dashboard admin
- **Auto-save JS** : Plus fluide mais complexité AJAX non justifiée pour le scope démo

## Goals & Objectives

### Primary Goals
1. Permettre à l'équipe interne de créer des sessions et générer des liens uniques pour les représentants
2. Collecter les informations du représentant via un formulaire guidé (textes, identité, branding, domaine)
3. Consolider les données en JSON structuré prêt pour un agent AI WordPress

### Success Metrics
- Un représentant peut compléter le formulaire en moins de 15 minutes
- Le JSON exporté contient toutes les informations nécessaires pour créer un site WordPress
- L'admin peut créer une session et obtenir un lien en moins de 30 secondes

### Scope Boundaries
- **In Scope:** Interface admin, formulaire représentant, export JSON, textes pré-rédigés pour le secteur financier
- **Out of Scope:** Envoi de courriels, agent AI WordPress, déploiement WPEngine, authentification avancée

### Non-Goals
- **Pas d'envoi de courriel** — pour la démo, on génère l'URL uniquement
- **Pas d'agent AI intégré** — le JSON est exporté, l'agent AI est un système externe
- **Pas de multi-tenancy** — un seul environnement admin
- **Pas de gestion de rôles/permissions** — HTTP Basic Auth suffit
- **Pas d'internationalisation** — français uniquement
- **Pas de tests automatisés complets** — tests manuels pour la démo
- **Pas de CI/CD** — déploiement local pour la démo

### Assumptions & Constraints
> Toutes les hypothèses sont dans `.claude/assumptions.md`

**Key Assumptions:**
- SQLite3 suffit pour le volume de la démo (<50 sessions simultanées)
- Les représentants accèdent via un navigateur moderne (Chrome, Firefox, Edge, Safari récent)
- 3 variantes de texte par catégorie couvrent les besoins de la majorité des représentants
- Le format JSON proposé sera compatible avec l'agent AI WordPress à développer ultérieurement

**Key Constraints:**
- Timeline : 1-2 semaines (démo interne)
- Stack imposé : Python, FastAPI, SQLite3
- Pas de budget infrastructure — exécution locale
- Domaine financier : fonds communs et assurance de personnes (Québec)

---

## User Journeys

### Journey 1: Admin — Créer une session
**Persona:** Membre de l'équipe interne
**Goal:** Créer une session pour un représentant et obtenir le lien unique

| Step | User Action | System Response | Notes |
|------|-------------|-----------------|-------|
| 1 | Accède à `/admin` | Affiche le dashboard avec liste des sessions | HTTP Basic Auth |
| 2 | Clique "Nouvelle session" | Affiche formulaire (nom cabinet, contact, email) | |
| 3 | Remplit et soumet | Crée la session, génère UUID token | |
| 4 | Voit le lien unique | Affiche l'URL `/form/{token}` avec bouton copier | L'URL est le livrable principal |

### Journey 2: Représentant — Compléter le formulaire
**Persona:** Représentant en services financiers
**Goal:** Fournir toutes les informations pour la création de son site web

| Step | User Action | System Response | Notes |
|------|-------------|-----------------|-------|
| 1 | Clique sur le lien unique | Affiche page de consentement Loi 25 | Token validé, expiration vérifiée |
| 2 | Accepte le consentement | Redirige vers étape 1 du wizard | Timestamp enregistré |
| 3 | **Étape 1 — Textes** : Choisit parmi 3 variantes par catégorie, personnalise si désiré | Affiche cartes de sélection + textarea éditable | 5 catégories × 3 variantes |
| 4 | **Étape 2 — Identité** : Remplit nom, prénom, email (Loi 25) | Formulaire avec validation | |
| 5 | **Étape 3 — Branding** : Upload logo, choisi couleurs | Color picker natif + preview logo | |
| 6 | **Étape 4 — Domaine** : Spécifie domaine existant ou souhaité | Champ conditionnel (oui/non → input) | |
| 7 | Soumet le formulaire | Confirmation + récapitulatif | Statut passe à "completed" |

### Journey 3: Admin — Exporter les données
**Persona:** Membre de l'équipe interne
**Goal:** Récupérer le JSON structuré pour l'agent AI WordPress

| Step | User Action | System Response | Notes |
|------|-------------|-----------------|-------|
| 1 | Voit session "completed" dans le dashboard | Badge vert "Complété" | |
| 2 | Clique "Exporter JSON" | Télécharge le fichier JSON structuré | Format documenté ci-dessous |

---

## Features

### Priority Definitions
- **P0:** Must have for MVP / démo
- **P1:** Important pour la démo
- **P2:** Nice to have
- **P3:** Hors scope démo

---

### P0 Features (Critical)

#### F001: Initialisation du projet et structure
**Category:** setup
**Source:** PRD
**Description:** Mettre en place la structure du projet FastAPI avec SQLite3, Jinja2, et Bootstrap 5 CDN.

**Acceptance Criteria:**
- [ ] Projet FastAPI fonctionnel avec structure de dossiers standard
- [ ] SQLite3 initialisé avec le schéma de base de données
- [ ] Templates Jinja2 avec layout de base Bootstrap 5
- [ ] Configuration via variables d'environnement (.env)

**Verification Steps:**
1. `uvicorn main:app --reload` démarre sans erreur
2. La page d'accueil s'affiche avec le layout Bootstrap

**Dependencies:** None
**Complexity:** M

---

#### F002: Modèle de données SQLite3
**Category:** data
**Source:** PRD
**Description:** Créer le schéma de base de données avec les tables sessions, form_data, uploads, consent_logs et text_templates.

**Acceptance Criteria:**
- [ ] Table `sessions` : id, token (UUID unique), firm_name, contact_name, contact_email, status (pending/in_progress/completed), expires_at, created_at
- [ ] Table `form_data` : id, session_id (FK), step, field_key, field_value, updated_at
- [ ] Table `uploads` : id, session_id (FK), file_type, filename, storage_path, uploaded_at
- [ ] Table `consent_logs` : id, session_id (FK), consent_given, consent_timestamp, consent_ip_hash
- [ ] Table `text_templates` : id, category, variant (1-3), title, content
- [ ] Index sur sessions.token pour recherche rapide
- [ ] Données de seed pour les 15 textes pré-rédigés (5 catégories × 3 variantes)

**Verification Steps:**
1. Le schéma se crée sans erreur au démarrage
2. Les 15 templates de texte sont pré-insérés
3. Les contraintes FK fonctionnent

**Dependencies:** F001
**Complexity:** M

---

#### F003: Système de token UUID
**Category:** auth
**Source:** PRD
**Description:** Générer des tokens UUID4 uniques lors de la création de session. Vérifier la validité et l'expiration à chaque accès.

**Acceptance Criteria:**
- [ ] Génération UUID4 à la création de session
- [ ] Vérification du token à chaque requête sur `/form/{token}`
- [ ] Retour 404 si token invalide (ne pas révéler l'existence)
- [ ] Retour 410 Gone si token expiré
- [ ] Expiration configurable (défaut : 30 jours)

**Verification Steps:**
1. Un token valide affiche le formulaire
2. Un token invalide retourne 404
3. Un token expiré retourne 410 avec message approprié

**Dependencies:** F002
**Complexity:** S

---

#### F004: Interface admin — Dashboard
**Category:** ui
**Source:** PRD
**Description:** Dashboard admin protégé par HTTP Basic Auth listant toutes les sessions avec leur statut.

**Acceptance Criteria:**
- [ ] Route `/admin` protégée par HTTP Basic Auth (credentials via .env)
- [ ] Tableau listant : nom cabinet, contact, email, statut, date création, lien unique
- [ ] Badges de statut colorés (pending=jaune, in_progress=bleu, completed=vert)
- [ ] Bouton "Copier le lien" pour chaque session

**Verification Steps:**
1. Accès à `/admin` demande les credentials
2. Credentials invalides = rejet
3. Le tableau affiche les sessions existantes avec bon statut

**Dependencies:** F001, F002
**Complexity:** M

---

#### F005: Interface admin — Créer une session
**Category:** ui
**Source:** PRD
**Description:** Formulaire admin pour créer une nouvelle session (nom cabinet, nom contact, email contact).

**Acceptance Criteria:**
- [ ] Formulaire avec champs : nom du cabinet, nom du contact, email du contact
- [ ] Validation des champs (email valide, champs requis)
- [ ] Après soumission : session créée, token généré, lien unique affiché
- [ ] Redirection vers le dashboard avec la nouvelle session visible

**Verification Steps:**
1. Remplir et soumettre le formulaire crée une session en DB
2. Le lien unique est affiché et fonctionnel
3. La validation rejette un email invalide

**Dependencies:** F003, F004
**Complexity:** S

---

#### F006: Page de consentement Loi 25
**Category:** core
**Source:** PRD
**Description:** Page de consentement obligatoire avant l'accès au formulaire. Le représentant doit accepter les conditions d'utilisation de ses données personnelles.

**Acceptance Criteria:**
- [ ] Affichée à la première visite sur `/form/{token}`
- [ ] Texte clair sur l'utilisation des données (création de site web)
- [ ] Checkbox "J'accepte" obligatoire
- [ ] Enregistrement du consentement (timestamp + hash IP) dans consent_logs
- [ ] Redirection vers étape 1 du formulaire après acceptation
- [ ] Si déjà consenti, redirection directe vers la dernière étape non complétée

**Verification Steps:**
1. Premier accès affiche la page de consentement
2. Impossible de continuer sans cocher la case
3. Le consent_logs contient l'enregistrement après acceptation
4. Un retour sur le lien ne re-demande pas le consentement

**Dependencies:** F003
**Complexity:** S

---

#### F007: Formulaire — Étape 1 : Sélection des textes
**Category:** core
**Source:** PRD
**Description:** Interface de sélection des textes pré-rédigés pour les 5 catégories. Chaque catégorie propose 3 variantes. L'utilisateur peut personnaliser le texte sélectionné.

**Catégories :**
1. Biographie / À propos
2. Services offerts
3. Approche client
4. Titres et accréditations
5. Mentions légales et divulgations

**Acceptance Criteria:**
- [ ] 5 sections, une par catégorie
- [ ] 3 cartes par section (variantes : professionnel / chaleureux / concis)
- [ ] Sélection par clic sur la carte (radio button visuel)
- [ ] Bouton "Personnaliser" qui ouvre un textarea pré-rempli avec le texte sélectionné
- [ ] Sauvegarde du template sélectionné ET du texte final (modifié ou non)
- [ ] POST vers le serveur → sauvegarde en DB → redirection étape 2

**Verification Steps:**
1. Les 5 catégories s'affichent avec 3 variantes chacune
2. La sélection d'une carte met à jour le visuel (carte active)
3. Le textarea s'ouvre avec le texte pré-rempli
4. La modification du texte est sauvegardée correctement
5. Les données sont en DB après soumission de l'étape

**Dependencies:** F002, F006
**Complexity:** L

---

#### F008: Formulaire — Étape 2 : Informations personnelles
**Category:** core
**Source:** PRD
**Description:** Collecte du nom, prénom et email du représentant pour la conformité Loi 25 et le contenu du site.

**Acceptance Criteria:**
- [ ] Champs : prénom, nom, email
- [ ] Validation côté serveur (champs requis, format email)
- [ ] Validation côté client (HTML5 validation)
- [ ] POST → sauvegarde en DB → redirection étape 3

**Verification Steps:**
1. Les champs s'affichent avec les labels appropriés
2. La soumission sans email valide est rejetée
3. Les données sont en DB après soumission

**Dependencies:** F006
**Complexity:** S

---

#### F009: Formulaire — Étape 3 : Branding (logo + couleurs)
**Category:** core
**Source:** PRD
**Description:** Upload du logo et sélection des couleurs primaire et secondaire du représentant.

**Acceptance Criteria:**
- [ ] Upload de logo (PNG, JPG, SVG) avec preview après sélection
- [ ] Validation taille max (5 MB) et types autorisés
- [ ] Stockage dans `/uploads/{token}/`
- [ ] Deux color pickers natifs (`<input type="color">`) : couleur primaire et secondaire
- [ ] Preview live des couleurs sélectionnées
- [ ] Logo et couleurs optionnels (le représentant peut passer cette étape)
- [ ] POST → sauvegarde fichier + données en DB → redirection étape 4

**Verification Steps:**
1. L'upload d'un PNG affiche la preview
2. Un fichier > 5MB est rejeté avec message d'erreur
3. Les color pickers fonctionnent et la preview se met à jour
4. Le fichier est bien enregistré dans le bon dossier

**Dependencies:** F006
**Complexity:** M

---

#### F010: Formulaire — Étape 4 : Nom de domaine
**Category:** core
**Source:** PRD
**Description:** Le représentant indique s'il a déjà un nom de domaine ou s'il en souhaite un nouveau.

**Acceptance Criteria:**
- [ ] Radio button : "J'ai déjà un domaine" / "Je souhaite un nouveau domaine"
- [ ] Si existant : champ pour saisir le domaine actuel
- [ ] Si nouveau : champ pour saisir le domaine souhaité
- [ ] Validation basique du format de domaine
- [ ] POST → sauvegarde en DB → page de confirmation

**Verification Steps:**
1. Le choix radio affiche le bon champ conditionnel
2. La validation rejette un format invalide
3. Les données sont en DB après soumission

**Dependencies:** F006
**Complexity:** S

---

#### F011: Page de confirmation et récapitulatif
**Category:** core
**Source:** PRD
**Description:** Après soumission de la dernière étape, afficher un récapitulatif de toutes les informations saisies.

**Acceptance Criteria:**
- [ ] Récapitulatif complet : textes choisis, identité, branding, domaine
- [ ] Bouton "Modifier" par section (retour à l'étape concernée)
- [ ] Bouton "Confirmer et soumettre" final
- [ ] Le statut de la session passe à "completed" après confirmation
- [ ] Message de remerciement post-confirmation

**Verification Steps:**
1. Le récapitulatif affiche toutes les données saisies correctement
2. Le bouton "Modifier" renvoie à la bonne étape
3. Le statut en DB passe à "completed"

**Dependencies:** F007, F008, F009, F010
**Complexity:** M

---

#### F012: Export JSON structuré
**Category:** api
**Source:** PRD
**Description:** Endpoint admin qui génère et retourne le JSON structuré contenant toutes les informations collectées, prêt pour l'agent AI WordPress.

**Acceptance Criteria:**
- [ ] Route `GET /admin/sessions/{id}/export` retourne le JSON
- [ ] Schéma JSON respecté (meta, identity, domain, branding, content, privacy)
- [ ] Chaque section content inclut selected_template et final_text
- [ ] Le logo_path est un chemin relatif valide
- [ ] Disponible uniquement pour les sessions "completed"
- [ ] Bouton "Exporter JSON" dans le dashboard admin

**Verification Steps:**
1. L'export d'une session complétée retourne un JSON valide
2. Le JSON contient toutes les sections attendues
3. L'export d'une session non complétée retourne une erreur 400

**Dependencies:** F004, F011
**Complexity:** M

---

#### F013: Textes pré-rédigés pour le secteur financier
**Category:** data
**Source:** PRD
**Description:** Rédiger les 15 textes pré-rédigés (5 catégories × 3 variantes) adaptés au secteur des services financiers (fonds communs et assurance de personnes).

**Acceptance Criteria:**
- [ ] 3 variantes par catégorie : professionnel, chaleureux, concis
- [ ] Textes en français, adaptés au marché québécois
- [ ] Catégorie 1 (Biographie) : parcours, expérience, formation
- [ ] Catégorie 2 (Services) : fonds communs, assurance de personnes, planification financière
- [ ] Catégorie 3 (Approche client) : philosophie, valeurs, engagement
- [ ] Catégorie 4 (Accréditations) : titres professionnels, certifications, affiliations
- [ ] Catégorie 5 (Mentions légales) : disclaimers réglementaires, conformité AMF
- [ ] Textes réalistes et utilisables en production

**Verification Steps:**
1. 15 textes présents dans la table text_templates
2. Chaque texte est cohérent avec sa catégorie et son ton
3. Les textes mentionnent les bons produits (fonds communs, assurance de personnes)

**Dependencies:** F002
**Complexity:** L

---

### P1 Features (High)

#### F014: Indicateur de progression du wizard
**Category:** ui
**Source:** PRD
**Description:** Barre de progression visuelle indiquant l'étape courante dans le formulaire (1/4, 2/4, etc.).

**Acceptance Criteria:**
- [ ] Stepper visuel en haut du formulaire avec 4 étapes nommées
- [ ] Étape courante mise en évidence
- [ ] Étapes complétées marquées visuellement
- [ ] Navigation arrière possible via le stepper

**Verification Steps:**
1. Le stepper reflète l'étape courante
2. Cliquer sur une étape précédente y retourne

**Dependencies:** F006
**Complexity:** S

---

#### F015: Reprise de session
**Category:** core
**Source:** PRD
**Description:** Si le représentant revient sur son lien unique, il reprend à la dernière étape non complétée.

**Acceptance Criteria:**
- [ ] Détection de la dernière étape complétée via les données en DB
- [ ] Redirection automatique vers la prochaine étape non complétée
- [ ] Les données déjà saisies sont pré-remplies dans les étapes précédentes

**Verification Steps:**
1. Compléter les étapes 1 et 2, fermer le navigateur, rouvrir le lien → redirigé à l'étape 3
2. Les données des étapes 1 et 2 sont toujours en DB

**Dependencies:** F006, F007
**Complexity:** M

---

#### F016: Validation et feedback utilisateur
**Category:** ui
**Source:** PRD
**Description:** Messages d'erreur et de succès clairs pour toutes les interactions du formulaire.

**Acceptance Criteria:**
- [ ] Messages d'erreur sous les champs invalides
- [ ] Toast/alert de succès après chaque étape sauvegardée
- [ ] Messages en français, clairs et non techniques

**Verification Steps:**
1. Soumettre un formulaire invalide affiche les erreurs sous les champs
2. Une soumission réussie affiche un message de confirmation

**Dependencies:** F007, F008
**Complexity:** S

---

#### F017: Administration — Voir les détails d'une session
**Category:** ui
**Source:** PRD
**Description:** Page de détail admin permettant de voir toutes les réponses d'une session sans exporter le JSON.

**Acceptance Criteria:**
- [ ] Route `/admin/sessions/{id}` affiche toutes les données collectées
- [ ] Affichage lisible des textes sélectionnés, identité, branding, domaine
- [ ] Preview du logo uploadé
- [ ] Statut de consentement Loi 25

**Verification Steps:**
1. La page de détail affiche correctement toutes les données
2. Le logo est visible
3. L'info de consentement est présente

**Dependencies:** F004
**Complexity:** M

---

### P2 Features (Medium)

#### F018: Page d'accueil / Landing
**Category:** ui
**Source:** PRD
**Description:** Page d'accueil simple présentant le projet et redirigeant vers l'admin.

**Acceptance Criteria:**
- [ ] Page `/` avec branding Vero
- [ ] Lien vers `/admin`
- [ ] Description courte du processus

**Verification Steps:**
1. La page d'accueil s'affiche correctement

**Dependencies:** F001
**Complexity:** S

---

#### F019: Export JSON — Téléchargement fichier
**Category:** api
**Source:** PRD
**Description:** Option de télécharger le JSON comme fichier .json au lieu de l'afficher dans le navigateur.

**Acceptance Criteria:**
- [ ] Header `Content-Disposition: attachment` pour téléchargement
- [ ] Nom de fichier : `{firm_name}_{contact_name}_{date}.json`

**Verification Steps:**
1. Le clic sur "Télécharger JSON" déclenche un téléchargement avec le bon nom

**Dependencies:** F012
**Complexity:** S

---

#### F020: Responsive mobile
**Category:** ui
**Source:** PRD
**Description:** Le formulaire du représentant doit être utilisable sur mobile et tablette.

**Acceptance Criteria:**
- [ ] Layout responsive via Bootstrap 5 grid
- [ ] Cards de texte empilées sur mobile
- [ ] Color picker et upload fonctionnels sur mobile

**Verification Steps:**
1. Le formulaire est lisible et utilisable sur un écran 375px de large

**Dependencies:** F007
**Complexity:** M

---

## Technical Requirements

### Technology Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Base de données:** SQLite3 (via aiosqlite ou sqlite3 standard)
- **Templates:** Jinja2 (intégré à FastAPI)
- **CSS:** Bootstrap 5 (CDN)
- **JS:** Vanilla JavaScript (minimal)
- **Serveur:** Uvicorn
- **Gestion de paquets:** uv (ou pip)

### Structure du projet

```
vero/
├── main.py                    # Point d'entrée FastAPI
├── database.py                # Initialisation SQLite + schéma
├── models.py                  # Pydantic models
├── routers/
│   ├── admin.py               # Routes admin
│   └── form.py                # Routes formulaire représentant
├── templates/
│   ├── base.html              # Layout Bootstrap 5
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── create_session.html
│   │   └── session_detail.html
│   └── form/
│       ├── consent.html
│       ├── step1_texts.html
│       ├── step2_identity.html
│       ├── step3_branding.html
│       ├── step4_domain.html
│       └── confirmation.html
├── static/
│   └── css/
│       └── custom.css
├── uploads/                   # Logos uploadés
├── seed_data.py               # Textes pré-rédigés
├── .env                       # Configuration
├── requirements.txt
└── README.md
```

### Schéma JSON d'export

```json
{
  "meta": {
    "schema_version": "1.0",
    "session_id": "uuid",
    "firm_name": "Cabinet XYZ",
    "exported_at": "2026-04-15T10:30:00Z",
    "status": "completed"
  },
  "identity": {
    "first_name": "Marie",
    "last_name": "Tremblay",
    "email": "marie@cabinet.ca",
    "firm_name": "Cabinet Horizon"
  },
  "domain": {
    "has_existing": false,
    "existing_domain": null,
    "requested_domain": "marie-tremblay-conseillere.ca"
  },
  "branding": {
    "logo_path": "uploads/{token}/logo.png",
    "primary_color": "#1A3C5E",
    "secondary_color": "#C8A84B"
  },
  "content": {
    "biography": {
      "category": "Biographie / À propos",
      "selected_template": 2,
      "variant_name": "chaleureux",
      "final_text": "Texte final après personnalisation..."
    },
    "services": {
      "category": "Services offerts",
      "selected_template": 1,
      "variant_name": "professionnel",
      "final_text": "..."
    },
    "client_approach": {
      "category": "Approche client",
      "selected_template": 3,
      "variant_name": "concis",
      "final_text": "..."
    },
    "credentials": {
      "category": "Titres et accréditations",
      "selected_template": 1,
      "variant_name": "professionnel",
      "final_text": "..."
    },
    "legal_disclosures": {
      "category": "Mentions légales et divulgations",
      "selected_template": 2,
      "variant_name": "chaleureux",
      "final_text": "..."
    }
  },
  "privacy": {
    "consent_given": true,
    "consent_timestamp": "2026-04-10T14:22:00Z",
    "data_purpose": "website_creation",
    "retention_policy": "2_years"
  }
}
```

---

## Architecture Decision Records

### ADR-001: UUID4 comme mécanisme d'authentification représentant
**Status:** Accepted
**Context:** Le représentant doit accéder au formulaire via un lien unique sans créer de compte.
**Decision:** UUID4 dans l'URL (`/form/{uuid}`) avec vérification côté serveur et expiration.
**Alternatives Considered:**
- HMAC signed tokens — Plus sécurisé mais complexité inutile pour démo. Upgrade path conservé.
- Short codes (8 chars) + IP binding — Plus facile à communiquer verbalement mais fragile (VPN, mobile).
**Consequences:** Nécessite HTTPS en production pour éviter que le token soit loggé en clair. Pour la démo locale, acceptable.

### ADR-002: Jinja2 SSR au lieu de SPA
**Status:** Accepted
**Context:** Le formulaire multi-étapes peut être implémenté en SPA (React/Vue) ou en SSR (Jinja2).
**Decision:** Jinja2 server-side rendering avec POST/redirect pour chaque étape.
**Alternatives Considered:**
- React SPA — Meilleur UX pour les transitions mais nécessite un build step, une API REST séparée, et double la complexité.
- HTMX + Jinja2 — Bon compromis mais ajoute une dépendance pour peu de bénéfice avec 4 étapes simples.
**Consequences:** Transitions moins fluides entre étapes (full page reload). Acceptable pour la démo. JS vanilla suffisant pour les interactions (preview logo, color picker, toggle textarea).

### ADR-003: SQLite3 comme base de données
**Status:** Accepted
**Context:** Stack imposé par le client. SQLite3 est suffisant pour le scope démo.
**Decision:** SQLite3 avec schéma relationnel complet.
**Alternatives Considered:**
- PostgreSQL — Plus robuste pour la concurrence mais overhead d'installation. Migration possible ultérieurement.
**Consequences:** Pas de support concurrence élevée (ok pour démo, <50 sessions). Fichier unique facilite les backups et la portabilité.

### ADR-004: Bootstrap 5 CDN comme framework CSS
**Status:** Accepted
**Context:** Le frontend nécessite un framework CSS pour le dashboard admin et le formulaire.
**Decision:** Bootstrap 5 via CDN, pas de build step CSS.
**Alternatives Considered:**
- Pico.css — Plus léger (10kb vs 30kb) mais manque de composants pour le tableau admin, les badges, les modals.
- Tailwind CDN — CDN sans JIT = 3MB, inacceptable.
**Consequences:** Dépendance au CDN (ok pour démo locale). Design Bootstrap reconnaissable mais fonctionnel.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Token UUID devinable/brute-forcé | Low | High | 122 bits d'entropie UUID4 + rate limiting en production |
| SQLite verrouillage concurrent | Low | Medium | Scope démo = peu d'utilisateurs simultanés |
| Textes pré-rédigés inadaptés | Medium | Medium | L'utilisateur peut personnaliser chaque texte |
| Format JSON incompatible avec agent AI | Medium | High | Schéma documenté et versionné, validation JSON Schema possible |
| Upload de fichiers malveillants | Low | High | Validation type MIME + taille max + pas d'exécution serveur |
| Perte de données formulaire | Medium | Medium | Sauvegarde par étape côté serveur, reprise de session |

---

## Agent Assignments

| Phase | Agent | Deliverable |
|-------|-------|-------------|
| Requirements | requirements-analyst | `.claude/prd.md` |
| Architecture | backend-architect | Structure FastAPI + schéma DB |
| Frontend | frontend-developer | Templates Jinja2 + Bootstrap |
| Textes | prompt-engineer | 15 textes pré-rédigés secteur financier |
| Data | python-pro | Models, routes, export JSON |
| QA | quality-engineer | Tests manuels + validation |

---

## Milestones

### Phase 1: Foundation (Jours 1-3)
**Features:** F001, F002, F003, F013
**Target:** Structure projet, DB, tokens, textes pré-rédigés

### Phase 2: Admin (Jours 3-5)
**Features:** F004, F005
**Target:** Dashboard admin fonctionnel

### Phase 3: Formulaire représentant (Jours 5-9)
**Features:** F006, F007, F008, F009, F010, F011, F014, F015, F016
**Target:** Wizard complet avec toutes les étapes

### Phase 4: Export et finition (Jours 9-11)
**Features:** F012, F017, F018, F019, F020
**Target:** Export JSON, détails admin, polish

---

## Approval

- [x] Brainstorm completed and direction approved
- [x] All features have acceptance criteria
- [x] All features have verification steps
- [x] Non-goals documented
- [x] Risks assessed with mitigations
- [x] Architecture decisions recorded
- [x] `.claude/assumptions.md` — à créer
- [x] `.claude/lessons.md` — à créer
- [x] Past lessons reviewed — aucune leçon globale existante
- [ ] Ready for project-init
