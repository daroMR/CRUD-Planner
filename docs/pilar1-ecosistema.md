# 🏛️ Pilar 1 — Ecosistema Híbrido

> **Descripción:** Vista general de la arquitectura del proyecto. Dos tracks independientes que convergen en Microsoft Planner como fuente de verdad.

---

## Resumen Ejecutivo

**CRUD-Planner** es un repositorio que alberga **dos productos independientes** unidos por la misma fuente de verdad: **Microsoft Planner** vía Graph API.

| Track | Stack | Propósito | Interfaz |
|:---:|:---|:---|:---|
| **Track Excel (V2)** | Python + xlwings + VBA (`v2/`) | Sync Planner ↔ Excel: Pull, Compare y Push bidireccional con semáforo visual. | Excel Desktop (.xlsm) |
| **Track Web** | FastAPI + Strawberry + SQLAlchemy (`backend/` + `frontend/`) | CRUD web con fallback local. API REST + GraphQL. Despliegue portable. | Browser SPA |

> ⚠️ Los dos tracks **no se comunican entre sí**. Comparten credenciales Azure (`.env`) y la fuente de datos (Planner/Graph), pero tienen autenticación, lógica y ciclo de vida **completamente separados**.

---

## 🗺️ Mapa de Componentes

```
c:\CRUD-Planner\
│
├── v2/                           ★ TRACK EXCEL (ACTIVO)
│   ├── planner_sync.py           # Motor: Auth → Fetch → Parse → Write → Push
│   ├── requirements.txt          # msal, requests, xlwings, python-dotenv
│   └── vba/                      # Módulos VBA definitivos
│       ├── SyncModule.bas        # CEREBRO: Orquestador V2/V1 híbrido
│       ├── ModConfig.bas         # Constantes, tokens, HasPython()
│       ├── ModAuth.bas           # Device Flow, Refresh, Clipboard helper
│       ├── ModGraphAPI.bas       # GET/PATCH con If-Match y retry 401
│       └── JsonConverter.bas     # Parser JSON para el Auth VBA
│
├── backend/                      ★ TRACK WEB (ACTIVO)
│   ├── main.py                   # FastAPI: REST + GraphQL, fallback a SQLite
│   ├── auth.py                   # MSAL PublicClient + Device Flow
│   ├── graphql_schema.py         # Strawberry: Query plans{buckets{tasks}}
│   ├── models.py                 # SQLAlchemy: Plan, Bucket, Task
│   ├── schemas.py                # Pydantic: BaseModel para validación
│   ├── database.py               # Engine + get_db dependency
│   └── requirements.txt          # fastapi, uvicorn, strawberry, sqlalchemy
│
├── frontend/                     ★ TRACK WEB (ACTIVO)
│   ├── index.html
│   ├── app.js
│   └── style.css
│
├── info/                         ★ DOCUMENTACIÓN (Pilares 5)
│   ├── blueprint.d2              # Golden Thread Map (código fuente)
│   └── onboarding.md             # Guía estratégica de acceso
│
├── docs/                         ★ DOCUMENTACIÓN TÉCNICA (Pilares 1-4)
│
├── .env                          # Credenciales Azure (compartidas, NO versionar)
├── README.md                     # Portal de entrada y guía rápida
├── requirements.txt              # Dependencias raíz (para Render/Deploy)
├── Procfile                      # Comandos de ejecución para Render
└── render.yaml                   # Configuración de automatización Render
```

---

## 🔐 Modelo de Autenticación por Track

| Aspecto | Track Excel (V2) | Track Web |
|:---|:---|:---|
| **Módulo** | `ModAuth.bas` + `planner_sync.py` | `backend/auth.py` |
| **Flujo** | Device Code (usuario autentica manualmente en `microsoft.com/devicelogin`) | Device Code (usuario autentica vía `GET /auth/login`) |
| **Client** | `ConfidentialClientApplication` (script) / `PublicClient` (VBA) | `PublicClientApplication` |
| **Grant** | `client_credentials` (V2 Script) / `device_code` (VBA) | `device_code` |
| **Token Cache** | Hoja "Config" en `.xlsm` (VBA) | `token_cache.bin` (backend) |
| **Scope** | `Tasks.ReadWrite User.Read` | `Tasks.ReadWrite User.Read` |

---

## 🔧 Stack de Tecnologías

| Capa | Tecnología | Versión recomendada |
|:---|:---|:---|
| Python (V2 + Backend) | Python | 3.11+ |
| Excel Integration | xlwings | 0.28+ |
| HTTP Client | requests (V2), httpx (Backend) | Latest |
| Auth | MSAL (Python) | 1.24+ |
| Web Framework | FastAPI | 0.110+ |
| GraphQL | Strawberry | 0.220+ |
| ORM | SQLAlchemy | 2.0+ |
| DB Local | SQLite (dev) / PostgreSQL (prod) | — |
| VBA Runtime | VBA 7.1 | Excel 2016+ |
