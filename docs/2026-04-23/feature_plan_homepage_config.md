# Bene2Luxe Homepage Config Feature Plan

**Date:** 23 Avril 2026
**Status:** Plan/Draft
**Priority:** HIGH - Admin Enhancement

---

## Overview

Create a new "Homepage Config" section in /admin that allows configuring:
1. **Featured products** for "Nouveautés & Best-sellers" section
2. **Homepage hero text** (customizable tagline)
3. **Product count per page** (with mobile optimization)

---

## Feature Requirements

### 1. Homepage Config Admin Section (`/admin?section=homepage-config`)

#### Backend Requirements:
- [ ] Create `homepage_config` table with fields:
  - `config_key` (VARCHAR, PRIMARY KEY) - e.g., 'featured_products', 'hero_text', 'products_per_page'
  - `config_value` (JSONB) - flexible value storage
  - `updated_at` (TIMESTAMP)
- [ ] Create API endpoints:
  - `GET /admin/homepage-config` - Get all config
  - `PUT /admin/homepage-config/{key}` - Update specific config
  - `POST /admin/homepage-config/featured-products` - Bulk update featured products

#### Frontend Requirements:
- [ ] Create `HomepageConfigSection.tsx` component
- [ ] Product selector with search and multi-select
- [ ] Hero text editor
- [ ] Products per page slider (with mobile preview)
- [ ] Live preview of homepage section

### 2. Homepage "Nouveautés & Best-sellers" Section

#### Backend Requirements:
- [ ] Fetch featured products from `homepage_config`
- [ ] Support priority ordering
- [ ] Fallback to recent active products if no config

#### Frontend Requirements:
- [ ] Display featured products in "Nouveautés & Best-sellers"
- [ ] Respect `products_per_page` config
- [ ] Reduce display count by 50% on mobile
- [ ] Mobile config editable via admin

### 3. Hero Text Configuration

- [ ] Configurable tagline text (default: "Découvrez nos pièces les plus convoitées, sélectionnées pour leur excellence et leur style intemporel")
- [ ] French language support

---

## Implementation Steps

### Phase 1: Backend (Database + API)
1. Create migration for `homepage_config` table
2. Add CRUD endpoints in backend
3. Create migration script for existing config

### Phase 2: Frontend Admin
1. Create `HomepageConfigSection.tsx` component
2. Add section to admin navigation
3. Implement product search and selector
4. Add live preview feature

### Phase 3: Frontend Homepage
1. Update Homepage component to read from config
2. Implement mobile optimization
3. Add dynamic product count

---

## Technical Notes

### Database Schema (Suggested)
```sql
CREATE TABLE homepage_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Initial data
INSERT INTO homepage_config (config_key, config_value) VALUES
('featured_products', '{"product_ids": [], "priority_order": true}'),
('hero_text', '{"text_fr": "Découvrez nos pièces les plus convoitées..."}'),
('display_settings', '{"products_per_page_desktop": 8, "products_per_page_mobile": 4}');
```

### API Response Format
```json
{
  "featured_products": {
    "product_ids": [1, 2, 3, 4, 5, 6, 7, 8],
    "priority_order": true
  },
  "hero_text": {
    "text_fr": "Découvrez nos pièces les plus convoitées, sélectionnées pour leur excellence et leur style intemporel"
  },
  "display_settings": {
    "products_per_page_desktop": 8,
    "products_per_page_mobile": 4
  }
}
```

---

## Status: PENDING IMPLEMENTATION

**Assigned to:** Development (Gilfoyle)
**Estimated complexity:** Medium
**Dependencies:** None