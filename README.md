# SKAD GROUP Corporate Backend Platform

High-performance, content-governed, Headless CMS and REST API platform built with **Python 3.11**, **Django 5.1**, and **Django REST Framework (DRF)**.

Engineered strictly per the **SKAD GROUP Corporate Website: Python + Django Specification (v1.0)** and the master architectural brief.

---

## Key Features

1. **Editorial Django Admin CMS (`/admin/`)**:
   - Role-based permissions (`Approver`, `Editor`, `HR`, `Media`, `Enquiry handler`).
   - Audit trail on all content changes via `django-simple-history`.
   - Strict content governance: blocks promotional buzzwords (`world-class`, `leading`, `best`) and unfinished drafts (`TODO`, `TBD`, `placeholder`).
2. **Interactive OpenAPI / Swagger Documentation (`/api/docs/` & `/api/redoc/`)**:
   - Complete interactive API playground generated dynamically by `drf-spectacular`.
   - Test, inspect, and trigger every endpoint in your browser without needing any frontend!
3. **Approved Corporate Ecosystem Architecture**:
   - **Companies**: `SKAD JEWELS INDIA PRIVATE LIMITED`, `LUXORA GLOW ESSENTIALS PRIVATE LIMITED`, `DETARA LTD`, `SKAD DIATECH EXPORTS`.
   - **Brands**: `DETARA`, `LUXORA GLOW`, `BENAVI` (*India-only* silver jewellery), `RUPAARI`, `CASE SUNO`, `ZEMO`.
   - **Platforms**: `SKAD COMMERCEOS` (*BUILD • LAUNCH • GROW*), `SKAD COMMERCE LAB` (*AI + HUMAN EXECUTION*).
   - **Ventures & Foundation**: `FUTURE VENTURES`, `KALLA RUDRA FOUNDATION`.
4. **11-Channel Departmental Inquiry Routing**:
   - `general`, `business_partnership`, `investment` (inactive by default), `supplier`, `manufacturing`, `diamond_trading`, `international_trade`, `technology`, `media`, `careers`, `foundation`.
   - Anti-bot honeypot detection, SHA-256 IP hashing, unique reference tracking (`SKD-YYMM-XXXX`).
5. **Interactive Ecosystem Graph & Fallback**:
   - `/api/v1/ecosystem/` returns node & edge graph data plus an accessible tabular fallback.
6. **SEO & Discoverability Engine**:
   - Dynamic `/api/v1/seo/sitemap/` endpoint feeding Next.js crawlers.
   - Automatic 301 `/api/v1/seo/redirects/` tracking on slug mutations.

---

## Quick Start Guide

### 1. Prerequisites & Environment
Ensure the virtual environment is activated:
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Seed Canonical Data
Load initial group hierarchy, companies, brands, platforms, 17 capabilities, 10 industries, and 11 enquiry routes (all initialized in draft/unverified state per content governance rules):
```bash
python manage.py seed_skad
```

### 4. Start Local Development Server
```bash
python manage.py runserver
```

---

## Essential URLs

| Service / Interface | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Django Admin CMS** | `http://127.0.0.1:8000/admin/` | **Username**: `admin`<br>**Password**: `skadadmin2026` |
| **Interactive Swagger UI** | `http://127.0.0.1:8000/api/docs/` | Visual API browser & test console |
| **ReDoc Documentation** | `http://127.0.0.1:8000/api/redoc/` | Clean technical documentation |
| **OpenAPI Schema (YAML)** | `http://127.0.0.1:8000/api/schema/` | Raw OpenAPI 3.0 schema |
| **Service Health Check** | `http://127.0.0.1:8000/api/v1/health/` | JSON status response |

---

## Core API Endpoints (`/api/v1/`)

### Entities & Corporate Graph
- `GET /api/v1/companies/` & `GET /api/v1/companies/{slug}/`
- `GET /api/v1/brands/` & `GET /api/v1/brands/{slug}/` (includes verified parent company)
- `GET /api/v1/platforms/` & `GET /api/v1/platforms/{slug}/`
- `GET /api/v1/ventures/`
- `GET /api/v1/foundation/initiatives/`
- `GET /api/v1/ecosystem/` (visual node graph + flat accessible list)

### Dynamic CMS & Page Composition
- `GET /api/v1/pages/home/` (ordered sections with JSON blocks)
- `GET /api/v1/pages/{slug}/`
- `GET /api/v1/navigation/` (primary nav tree + mega menu + footer columns)
- `GET /api/v1/site-settings/`
- `GET /api/v1/theme/` (approved design palette & brand themes)
- `GET /api/v1/ui-strings/` (frontend microcopy key-value dictionary)

### Taxonomy & Markets
- `GET /api/v1/capabilities/` (17 strategic capabilities)
- `GET /api/v1/industries/` (10 verified sectors)
- `GET /api/v1/markets/` (grouped into active, served, target, future)

### Insights, Press & Team
- `GET /api/v1/articles/` & `GET /api/v1/articles/{slug}/`
- `GET /api/v1/news/` & `GET /api/v1/news/{slug}/`
- `GET /api/v1/people/` (consented bios only)
- `GET /api/v1/careers/` (open roles)
- `GET /api/v1/partners/`

### Inquiries & Controlled Form Ingestion
- `GET /api/v1/enquiries/routes/` (list active channels)
- `POST /api/v1/enquiries/` (submits enquiry with routing & honeypot defense)
- `POST /api/v1/opportunities/` (founder/strategic proposals)
- `POST /api/v1/applications/` (multipart resume upload)
- `POST /api/v1/subscriptions/` (newsletter double opt-in)

### Documents & SEO
- `GET /api/v1/documents/` & `GET /api/v1/documents/{id}/download/` (tracked download logging)
- `GET /api/v1/search/?q={query}` (unified cross-entity search)
- `GET /api/v1/seo/sitemap/`
- `GET /api/v1/seo/redirects/`

---

## Running Automated Tests

Run the full automated test suite covering governance checks, honeypot defenses, and API endpoints:
```bash
python manage.py test tests
```
