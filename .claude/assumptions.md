# Assumptions Log

> Auto-maintained by Claude Code. Each phase gate requires logging assumptions before proceeding.
> Search: `grep "Status | active" .claude/assumptions.md` or `grep "Impact | HIGH" .claude/assumptions.md`

## Quick Reference

| ID | Phase | Category | Confidence | Impact | Status |
|----|-------|----------|------------|--------|--------|
| ASS-001 | brainstorm | technical | HIGH | HIGH | active |
| ASS-002 | brainstorm | technical | HIGH | MED | active |
| ASS-003 | brainstorm | user | MED | MED | active |
| ASS-004 | brainstorm | security | HIGH | HIGH | active |
| ASS-005 | planning | technical | MED | HIGH | active |
| ASS-006 | planning | integration | MED | HIGH | active |
| ASS-007 | planning | user | HIGH | MED | active |
| ASS-008 | planning | security | HIGH | HIGH | active |

---

## Entries

### ASS-001 — SQLite3 suffisant pour le volume de la démo

| Field | Value |
|-------|-------|
| Phase | brainstorm |
| Category | technical |
| Confidence | HIGH |
| Impact | HIGH |
| Status | active |
| Linked | ADR-003 |
| Revised-to | — |
| Date | 2026-04-01 |

SQLite3 gère sans problème moins de 50 sessions simultanées. Le verrouillage en écriture n'est pas un enjeu pour une démo interne avec peu d'utilisateurs. Si le projet évolue vers la production, migration vers PostgreSQL nécessaire.

---

### ASS-002 — UUID4 offre une entropie suffisante pour la démo

| Field | Value |
|-------|-------|
| Phase | brainstorm |
| Category | technical |
| Confidence | HIGH |
| Impact | MED |
| Status | active |
| Linked | ADR-001 |
| Revised-to | — |
| Date | 2026-04-01 |

UUID4 fournit ~122 bits d'entropie, rendant le brute-force impraticable. Pour la démo locale (pas d'exposition internet), le risque est négligeable. En production, ajouter HTTPS + rate limiting.

---

### ASS-003 — 3 variantes de texte couvrent les besoins

| Field | Value |
|-------|-------|
| Phase | brainstorm |
| Category | user |
| Confidence | MED |
| Impact | MED |
| Status | active |
| Linked | PRD-F007, PRD-F013 |
| Revised-to | — |
| Date | 2026-04-01 |

Les 3 tons (professionnel, chaleureux, concis) couvrent la majorité des préférences de communication des représentants financiers. Le mécanisme de personnalisation (textarea éditable) compense si aucun ne convient parfaitement.

---

### ASS-004 — Loi 25 respectée avec consentement + timestamp

| Field | Value |
|-------|-------|
| Phase | brainstorm |
| Category | security |
| Confidence | HIGH |
| Impact | HIGH |
| Status | active |
| Linked | PRD-F006 |
| Revised-to | — |
| Date | 2026-04-01 |

Le consentement explicite avec checkbox, timestamp et hash IP satisfait les exigences minimales de la Loi 25 pour la collecte de données à des fins de création de site web. Validation par un conseiller juridique recommandée avant production.

---

### ASS-005 — Le schéma JSON proposé sera compatible avec l'agent AI WordPress

| Field | Value |
|-------|-------|
| Phase | planning |
| Category | technical |
| Confidence | MED |
| Impact | HIGH |
| Status | active |
| Linked | PRD-F012 |
| Revised-to | — |
| Date | 2026-04-01 |

Le schéma JSON versionné (schema_version: 1.0) contient toutes les sections nécessaires pour un site WordPress (identité, contenu, branding, domaine). L'agent AI n'est pas encore développé — le schéma devra peut-être évoluer.

---

### ASS-006 — Bootstrap 5 CDN disponible et stable

| Field | Value |
|-------|-------|
| Phase | planning |
| Category | integration |
| Confidence | MED |
| Impact | HIGH |
| Status | active |
| Linked | ADR-004 |
| Revised-to | — |
| Date | 2026-04-01 |

La démo dépend du CDN Bootstrap. Si la démo se fait en environnement sans internet, il faudra servir Bootstrap localement. Alternative : télécharger les fichiers Bootstrap dans /static/.

---

### ASS-007 — Les représentants utilisent un navigateur moderne

| Field | Value |
|-------|-------|
| Phase | planning |
| Category | user |
| Confidence | HIGH |
| Impact | MED |
| Status | active |
| Linked | PRD-F009 |
| Revised-to | — |
| Date | 2026-04-01 |

Les fonctionnalités utilisées (`<input type="color">`, `<input type="file">` avec preview, CSS grid) nécessitent un navigateur moderne. Chrome/Firefox/Edge/Safari récents sont supportés. IE11 n'est pas supporté.

---

### ASS-008 — HTTP Basic Auth suffisant pour l'admin en démo

| Field | Value |
|-------|-------|
| Phase | planning |
| Category | security |
| Confidence | HIGH |
| Impact | HIGH |
| Status | active |
| Linked | ADR-001, PRD-F004 |
| Revised-to | — |
| Date | 2026-04-01 |

Pour une démo interne, HTTP Basic Auth via variable d'environnement est acceptable. En production, il faudra un système d'authentification plus robuste (OAuth2, SSO d'entreprise).

---
