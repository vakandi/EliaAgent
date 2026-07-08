# BIYOU Sprint 1 Prep - 22 Avril 2026

## 📅 Sprint Period
**22 Avril - 28 Avril 2026** (1 semaine)

---

## 🎯 Sprint 1 Goal
Infrastructure Setup complet:
- Docker Compose
- Apache Configuration
- Directus Deployment
- Database Schema

---

## 📋 Tickets Jira (BIYOU)

### Ticket BIYOU-1: [INFRA-01] Docker Compose Setup
- **Status**: À faire
- **Priority**: HIGH
- **Description**: Create Docker Compose file with:
  - Apache (reverse proxy + SSL)
  - Frontend (React)
  - Directus CMS
  - PostgreSQL
  - Redis

### Ticket BIYOU-2: [INFRA-02] Apache Configuration
- **Status**: À faire
- **Priority**: HIGH
- **Description**: Configure Apache as reverse proxy with SSL termination

### Ticket BIYOU-3: [INFRA-03] Directus Deployment
- **Status**: À faire
- **Priority**: HIGH
- **Description**: Deploy Directus CMS with initial configuration

### Ticket BIYOU-4: [INFRA-04] Database Schema Design
- **Status**: À faire
- **Priority**: MEDIUM
- **Description**: Design and create database schema

---

## 🔧 Technical Resources

### Reference Projects
| Project | Path | Purpose |
|---------|------|---------|
| AccForgeDev | /Users/vakandi/Documents/AccForgeDev/ | Docker + Apache patterns |
| Directus Docs | https://docs.directus.io | Directus setup |

### Docker Compose Template (from AccForgeDev)
```yaml
version: '3.8'
services:
  apache:
    build: ./apache
    ports: [80, 443]
    depends_on: [frontend, directus]

  frontend:
    build: ./frontend
    ports: [8000]

  directus:
    image: directus/directus:latest
    ports: [8050]
    env_file: .env

  db:
    image: postgres:17
    volumes: [db_data:/var/lib/postgresql/data]

  redis:
    image: redis:latest

volumes:
  db_data:
```

### Required Environment Variables
```bash
# Database
DB_PASSWORD=your_secure_password

# Directus
ADMIN_EMAIL=admin@biyou.agency
ADMIN_PASSWORD=your_secure_password
KEY=your_directus_key
SECRET=your_directus_secret

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# App
APP_URL=https://biyou.agency
CORS_ORIGIN=https://biyou.agency
```

---

## ✅ Acceptance Criteria

- [ ] Docker Compose crée sans erreurs
- [ ] Apache proxy vers frontend et Directus
- [ ] SSL certificates provisionnés
- [ ] Directus accessible
- [ ] Database migrations passent

---

## 📝 Notes

1. **Client**: Nouveau client (nom à confirmer)
2. **Architecture**: Directus CMS + React Frontend + Custom Payment API
3. **Paiement**: Stripe integration (custom API requise car Directus ne gère pas les paiements)

---

*Préparé: 21 Avril 2026*
*Elia - Sprint 1 starts tomorrow*