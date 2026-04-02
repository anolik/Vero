# Vero — Collecteur de sites web pour représentants financiers

Application web FastAPI collectant les informations des représentants (fonds communs, assurance de personnes) pour générer un JSON structuré importable dans WordPress/WPEngine.

## Tech Stack
- Python 3.11+ / FastAPI / Uvicorn
- SQLite3 (base de données)
- Jinja2 (templates server-side)
- Bootstrap 5 CDN (CSS)
- Vanilla JS (minimal)
- uv (gestion de paquets)

## MCP: Core Only
`context7` · `sequential-thinking` — disable all others.

## Startup
```bash
cat CLAUDE.md && cat .claude/workflow.md
cat .claude/feature-list.json && cat .claude/progress.txt
git log --oneline -5
grep -c '"passes": false' .claude/feature-list.json
grep -c "Status | active" .claude/assumptions.md 2>/dev/null
```

## Standards
- Routes admin sous `/admin`, formulaire sous `/form/{token}`
- HTTP Basic Auth pour admin (credentials via .env)
- UUID4 pour tokens d'accès représentant
- Sauvegarde par étape (POST/redirect), pas d'auto-save JS
- Consentement Loi 25 obligatoire avant accès formulaire
- Export JSON versionné (schema_version: 1.0)

## Constraints
- Démo interne, timeline 1-2 semaines
- Pas d'envoi de courriel — générer URL uniquement
- Pas d'agent AI intégré — JSON exporté pour système externe
- Français uniquement
- SQLite3 imposé (pas de PostgreSQL)

## Lessons
- Aucune leçon globale héritée (premier projet)
> Full log: `.claude/lessons.md`

## Skills
`project-planning` → `project-init` → `project-coding` → `project-testing` → `project-optimization`

## Project Structure
```
vero/
├── main.py              # FastAPI app
├── database.py          # SQLite3 init + schema
├── models.py            # Pydantic models
├── routers/admin.py     # Routes admin
├── routers/form.py      # Routes formulaire
├── templates/           # Jinja2 (base, admin/, form/)
├── static/css/          # Custom CSS
├── uploads/             # Logos uploadés
├── seed_data.py         # 15 textes pré-rédigés
├── .env                 # Config (ne pas committer)
└── requirements.txt
```
