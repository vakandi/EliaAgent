# BIYOU Project - Complete Documentation

**Project Key**: `BIYOU`
**Project URL**: https://bsbagency.atlassian.net/browse/BIYOU
**Sprint Period**: April 22 - June 15, 2026 (8 weeks)
**Client**: [New client name]

---

## Project Overview

**BIYOU** is a client platform with:
- **Directus CMS** for all public/private APIs, permissions, flows, and security
- **React + TypeScript** frontend for homepage and other pages
- **Directus Admin Dashboard** for admin management
- **Payment Integration API** (Stripe) - the real work since Directus doesn't handle payments

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                         BIYOU ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────┐ │
│  │   USER     │     │   ADMIN    │     │    EXTERNAL           │ │
│  │  BROWSER  │     │   BROWSER  │     │    SERVICES         │ │
│  └─────┬──────┘     └─────┬──────┘     └────────┬─────────────┘ │
│        │                  │                    │              │
│        │                  │                    │              │
│        ▼                  ▼                    │              │
│  ┌─────────────────────────────────────┐      │              │
│  │       APACHE (HTTPD 2.4)              │      │              │
│  │  Reverse Proxy + SSL Termination     │◄─────┘              │
│  └────────────┬────────────────────────┘                       │
│               │                                                │
│        ┌──────┴──────┐                                        │
│        │             │                                         │
│        ▼             ▼                                         │
│  ┌───────────┐ ┌───────────┐ ┌───────────────────────────────┐   │
│  │  FRONTEND │ │  DIRECTUS │ │  PAYMENT API (Custom)          │   │
│  │  React   │ │   CMS    │ │  (Stripe Integration)        │   │
│  │  :8000   │ │   :8050  │ │                             │   │
│  └───────────┘ └─────┬────┘ └───────────────────────────────┘   │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────┐            │
│  │           POSTGRESQL DATABASE                  │            │
│  │   - Users, Profiles                         │            │
│  │   - Content, Media                        │            │
│  │   - Orders, Payments                      │            │
│  │   - Activity Logs                         │            │
│  └───────────────────────────────────────────┘            │
│                                                              │
│  ┌──────────────────────────────────────────────────┐         │
│  │           REDIS (CACHE)                          │         │
│  └──────────────────────────────────────────────────┘         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Sprint Breakdown

### Sprint 1: Infrastructure Setup (April 22-28, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-1 | [INFRA-01] Docker Compose Setup | HIGH |
| BIYOU-2 | [INFRA-02] Apache Configuration | HIGH |
| BIYOU-3 | [INFRA-03] Directus Deployment | HIGH |
| BIYOU-4 | [INFRA-04] Database Schema Design | MEDIUM |

**Goal**: Complete Docker infrastructure and Directus deployment

### Sprint 2: Directus Core Setup (April 29 - May 5, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-5 | [CORE-01] Collections Setup | HIGH |
| BIYOU-6 | [CORE-02] Permission Roles | HIGH |
| BIYOU-7 | [CORE-03] Flows Automation | MEDIUM |
| BIYOU-8 | [CORE-04] Extensions Setup | MEDIUM |

**Goal**: Configure Directus collections, permissions, and flows

### Sprint 3: Backend & API (May 6-12, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-9 | [API-01] Custom API Endpoints | HIGH |
| BIYOU-10 | [API-02] Authentication System | HIGH |
| BIYOU-11 | [API-03] Directus SDK Setup | MEDIUM |
| BIYOU-12 | [API-04] Webhooks | MEDIUM |

**Goal**: Build custom API endpoints and authentication

### Sprint 4: Payment Integration (May 13-19, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-13 | [PAY-01] Stripe Integration | HIGH |
| BIYOU-14 | [PAY-02] Payment Endpoints | HIGH |
| BIYOU-15 | [PAY-03] Webhook Handlers | HIGH |
| BIYOU-16 | [PAY-04] Payment Flows | MEDIUM |

**Goal**: Implement Stripe payment integration

### Sprint 5: Frontend Setup (May 20-26, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-17 | [FE-01] React Project Setup | HIGH |
| BIYOU-18 | [FE-02] Directus SDK | MEDIUM |
| BIYOU-19 | [FE-03] Authentication UI | HIGH |
| BIYOU-20 | [FE-04] Core Pages Setup | MEDIUM |

**Goal**: Set up React frontend with Directus SDK

### Sprint 6: Frontend Pages (May 27 - June 2, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-21 | [FE-05] Homepage | HIGH |
| BIYOU-22 | [FE-06] Content Pages | MEDIUM |
| BIYOU-23 | [FE-07] User Dashboard | HIGH |
| BIYOU-24 | [FE-08] Admin Dashboard | MEDIUM |

**Goal**: Build all frontend pages

### Sprint 7: Testing & Integration (June 3-9, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-25 | [QA-01] E2E Testing | HIGH |
| BIYOU-26 | [QA-02] Security Audit | HIGH |
| BIYOU-27 | [QA-03] Performance | MEDIUM |
| BIYOU-28 | [QA-04] Bug Fixes | HIGH |

**Goal**: Test, secure, and optimize

### Sprint 8: Deployment & Launch (June 10-15, 2026)

| Ticket | Summary | Priority |
|--------|---------|---------|
| BIYOU-29 | [DEPLOY-01] Production | HIGH |
| BIYOU-30 | [DEPLOY-02] Monitoring | MEDIUM |
| BIYOU-31 | [DEPLOY-03] Documentation | MEDIUM |
| BIYOU-32 | [DEPLOY-04] Launch | HIGH |

**Goal**: Deploy to production and launch

---

## Directus Collections Schema

```
┌─────────────────────────────────────────────────────────────┐
│                 DIRECTUS COLLECTIONS                 │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐                                    │
│  │ directus_  │ (built-in)                         │
│  │  users    │                                    │
│  └─────┬─────┘                                    │
│        │ 1:1                                     │
│        ▼                                         │
│  ┌─────────────┐     ┌─────────────┐             │
│  │ profiles  │←────│  users    │             │
│  └─────┬─────┘     └─────────────┘             │
│        │                                         │
│  ┌─────────────┐                              │
│  │  content  │ (pages, articles)             │
│  └─────────────┘                              │
│                                                   │
│  ┌─────────────┐                              │
│  │  orders    │ (payment records)             │
│  └─────────────┘                              │
│                                                   │
│  ┌─────────────┐                              │
│  │  activity │ (audit trail)                │
│  │   _logs   │                              │
│  └─────────────┘                              │
│                                                   │
│  ┌─────────────┐                              │
│  │ directus_  │ (built-in)                         │
│  │  files    │ (media library)                  │
│  └─────────────┘                              │
│                                                   │
└─────────────────────────────────────────────────────┘
```

---

## Directus Permissions Roles

| Role | Access Level |
|------|------------|
| **Admin** | Full access to all collections |
| **Editor** | Create/edit content, manage media |
| **User** | View content, manage own profile |
| **Guest** | View public content only |

---

## Payment Integration (Stripe)

```
┌─────────────────────────────────────────────────────────────┐
│                 STRIPE PAYMENT FLOW                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User → Checkout → Stripe → Webhook → Update             │
│    │         │       │        │        │             │
│    │         │       │        │        ▼             │
│    │         │       │        │   Update Order         │
│    │         │       │        │   Send Email         │
│    │         │       │        │   Trigger Flow      │
│    │         │       │        ▼                 │
│    │         │       │   Directus Flow         │
│    │         │       ▼                        │
│    │         │   Checkout Session            │
│    │         ▼                                │
│    │   Create Session                      │
│    ▼                                        │
│  Payment Intent                             │
│                                                     │
└─────────────────────────────────────────────────┘
```

### Stripe Webhook Events

| Event | Action |
|--------|--------|
| `checkout.session.completed` | Mark order as paid |
| `payment_intent.succeeded` | Update status |
| `payment_intent.payment_failed` | Mark as failed |
| `charge.refunded` | Process refund |

---

## Docker Setup (AccForgeDev Pattern)

### docker-compose.yaml

```yaml
version: '3.8'
services:
  apache:
    build:
      context: .
      dockerfile: Dockerfile.apache
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./apache-config:/usr/local/apache2/conf/sites-available
      - ./letsencrypt-certs:/etc/letsencrypt
    depends_on:
      - frontend
      - directus
      - db

  directus:
    image: directus/directus:latest
    ports:
      - "8050:8050"
    environment:
      DB_CLIENT: postgres
      DB_HOST: db
      DB_PORT: 5432
      DB_DATABASE: biyou
      DB_USER: biyou_user
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "8000:8000"

  db:
    image: postgres:17.2
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U biyou_user"]
      interval: 10s
      timeout: 5s

  redis:
    image: redis:latest
    command: redis-server --maxmemory 200mb

volumes:
  db_data:

networks:
  default:
    name: biyou_network
```

### Dockerfile.apache

```dockerfile
FROM httpd:2.4

RUN apt-get update && apt-get install -y \
    curl openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Enable modules
RUN sed -i \
    -e 's/#LoadModule proxy_module/LoadModule proxy_module/' \
    -e 's/#LoadModule proxy_http_module/LoadModule proxy_http_module/' \
    -e 's/#LoadModule ssl_module/LoadModule ssl_module/' \
    /usr/local/apache2/conf/httpd.conf

# ... rest of config from AccForgeDev
```

### Apache Virtual Host

```apache
<VirtualHost *:443>
    ServerName biyou.agency
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/biyou.agency/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/biyou.agency/privkey.pem

    # Proxy to Directus
    ProxyPass /api http://directus:8050/api
    ProxyPassReverse /api http://directus:8050/api

    # Proxy to Frontend
    ProxyPass / http://frontend:8000/
    ProxyPassReverse / http://frontend:8000/
</VirtualHost>
```

---

## Environment Variables

### Required

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
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Redis
REDIS_PASSWORD=your_redis_password

# App
APP_URL=https://biyou.agency
CORS_ORIGIN=https://biyou.agency
```

---

## File Structure

```
/biyou/
├── docker-compose.yaml
├── Dockerfile.apache
├── Dockerfile.frontend
├── .env
│
├── apache-config/
│   ├── biyou.agency-ssl.conf
│   └── docker-entrypoint.sh
│
├── letsencrypt-certs/
│   └── live/biyou.agency/
│
├── directus/
│   └── (extensions, hooks, endpoints)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── stores/
│   ├── package.json
│   └── vite.config.ts
│
└── docs/
    └── documentation.md
```

---

## API Reference

### Directus Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/items/content` | Get content |
| GET | `/items/content/:id` | Get single content |
| POST | `/items/content` | Create content |
| PATCH | `/items/content/:id` | Update content |
| DELETE | `/items/content/:id` | Delete content |
| POST | `/auth/login` | Login |
| POST | `/auth/refresh` | Refresh token |

### Custom Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|------------|
| POST | `/payments/create-session` | Create Stripe session |
| GET | `/payments/:id` | Get payment status |
| POST | `/payments/webhook` | Stripe webhook |
| POST | `/payments/:id/refund` | Refund payment |

---

## Acceptance Criteria Checklist

### Sprint 1
- [ ] Docker Compose working
- [ ] Apache proxy working
- [ ] Directus deployed
- [ ] Database schema created

### Sprint 2
- [ ] All collections created
- [ ] Permissions configured
- [ ] Flows working
- [ ] Extensions installed

### Sprint 3
- [ ] Custom endpoints working
- [ ] Authentication working
- [ ] SDK integrated
- [ ] Webhooks configured

### Sprint 4
- [ ] Stripe integration working
- [ ] Payments processing
- [ ] Webhooks handling
- [ ] Flows automated

### Sprint 5
- [ ] React project running
- [ ] SDK integrated
- [ ] Auth UI working
- [ ] Core layout done

### Sprint 6
- [ ] Homepage done
- [ ] Content pages done
- [ ] User dashboard done
- [ ] Admin dashboard done

### Sprint 7
- [ ] E2E tests passing
- [ ] Security audit passed
- [ ] Performance optimized
- [ ] Bugs fixed

### Sprint 8
- [ ] Production deployed
- [ ] Monitoring active
- [ ] Documentation complete
- [ ] Launch confirmed

---

## Reference Files

| File | Path |
|------|------|
| AccForgeDev docker-compose | `/Users/vakandi/Documents/AccForgeDev/docker-compose.yaml` |
| AccForgeDev Dockerfile.apache | `/Users/vakandi/Documents/AccForgeDev/Dockerfile.apache` |
| AccForgeDev Apache configs | `/Users/vakandi/Documents/AccForgeDev/apache-config/` |
| Directus Docs | `https://docs.directus.io` |
| Stripe Docs | `https://stripe.com/docs` |

---

**Document Version**: 1.0
**Created**: April 21, 2026
**Project Manager**: Wael Bousfira