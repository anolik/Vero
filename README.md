<!-- Source: .claude/prd.md — Do not copy PRD prose. Summarize outcomes, not requirements. -->

# Vero

Collecteur d'informations pour la création de sites web de représentants en services financiers.

## Quickstart

```bash
# 1. Cloner et configurer
git clone <repo-url> && cd vero
bash .claude/scripts/init.sh

# 2. Lancer le serveur
uvicorn main:app --reload

# 3. Accéder
# Admin: http://localhost:8000/admin
# Credentials: voir .env
```

## Prerequisites

| Outil | Version | Notes |
|-------|---------|-------|
| Python | 3.11+ | Requis |
| uv | latest | Gestion de paquets (ou pip) |

## Installation

```bash
# Créer l'environnement virtuel
uv venv && source .venv/bin/activate

# Installer les dépendances
uv pip install -r requirements.txt

# Configurer l'environnement
cp .env.example .env
# Modifier les valeurs par défaut dans .env
```

## Configuration

| Variable | Description | Défaut |
|----------|-------------|--------|
| `ADMIN_USERNAME` | Nom d'utilisateur admin | `admin` |
| `ADMIN_PASSWORD` | Mot de passe admin | `changeme` |
| `TOKEN_EXPIRY_DAYS` | Durée de validité des liens | `30` |
| `DATABASE_URL` | Chemin SQLite | `sqlite:///vero.db` |
| `SECRET_KEY` | Clé secrète pour les sessions | — |

## Usage

### 1. Créer une session (Admin)

Accéder à `/admin`, créer une nouvelle session en fournissant :
- Nom du cabinet
- Nom du contact
- Email du contact

Un lien unique est généré pour le représentant.

### 2. Compléter le formulaire (Représentant)

Le représentant accède via son lien unique et complète 4 étapes :
1. **Textes** — Choix parmi 3 variantes pour 5 catégories de contenu
2. **Identité** — Nom, prénom, email
3. **Branding** — Logo et couleurs
4. **Domaine** — Nom de domaine existant ou souhaité

### 3. Exporter les données (Admin)

Une fois le formulaire complété, exporter le JSON structuré depuis le dashboard admin pour l'agent AI WordPress.

<!-- TODO: Ajouter exemple de JSON exporté après implémentation -->

## Tech Stack

- **Backend:** Python 3.11+ / FastAPI / Uvicorn
- **Base de données:** SQLite3
- **Frontend:** Jinja2 + Bootstrap 5 CDN
- **Gestion de paquets:** uv

## License

Apache 2.0
