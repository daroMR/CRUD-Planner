# 🏛️ Pilar 1 — Ecosistema Híbrido Supreme

> **Descripción:** Arquitectura de alta disponibilidad y UX Premium. Dos tracks independientes que convergen en Microsoft Planner como fuente de verdad única.

---

## Resumen Ejecutivo

**CRUD-Planner** evoluciona hacia una solución de gestión integral donde la robustez del motor Excel se une a la elegancia de una interfaz web por slides.

| Track | Stack | Propósito | Interfaz |
|:---:|:---|:---|:---|
| **Track Excel (V2)** | Python + xlwings + VBA | Sincronización analítica y control masivo de datos con semáforo visual. | Excel Desktop (.xlsm) |
| **Track Web (Premium)** | FastAPI + GraphQL + Vanilla CSS | Gestión ágil y móvil con navegación por slides, modo oscuro y CRUD completo. | SPA Responsiva |
| **Middleware (Stitch)** | Python (FastAPI) + React | Puente de datos de alta fidelidad entre VBA y Planner con columnas personalizadas. | Dashboard Bento-Grid |

---

## 🗺️ Mapa de Componentes (The Ghost Architecture)

```
c:\CRUD-Planner\
│
├── backend/                      ★ API MASTER (REST + GraphQL)
│   ├── main.py                   # Exposición de activos /info, /docs y /app
│   └── ...
│
├── middleware/                   ★ DATA STITCHER (FastAPI + React)
│   ├── main.py                   # Lógica de parsing Markdown (Sync Protocol)
│   ├── tests.py                  # Pruebas de integridad de datos
│   └── frontend/                 # UI Bento-Grid (Google Cloud Style)
│
├── frontend/                     ★ UX PREMIUM (Slides & Sidebar)
│   ├── index.html                # Estructura por slides: Dashboard, Gestión, Maestro e Info
│   ├── app.js                    # Lógica defensiva & Navegación fluida
│   └── style.css                 # Glassmorphism & Media Queries (Full Responsive)
│
├── info/                         ★ INTELIGENCIA (Golden Thread)
│   ├── blueprint.d2              # Mapa fuente (Layout: Tala)
│   ├── onboarding.md             # Guía táctica de despliegue
│   └── golden-thread.png         # Visualización estratégica 4K
│
├── docs/                         ★ ARQUITECTURA (Pilares 1-4)
│
├── requirements.txt              # Motor unificado para Render
└── render.yaml                   # Orquestación de infraestructura
```

---

## 🔐 Modelo de Autenticación Unificado

Ambos tracks utilizan flujos de Microsoft Identity pero con propósitos distintos:

- **Excel Track**: Utiliza flujos delegados y scripts de Python para comparaciones pesadas.
- **Web Track**: Implementa un flujo de dispositivo integrado en el UI que cachea el token en el servidor para una experiencia sin interrupciones.

---

## 🔧 Stack de Tecnologías (Supreme Edition)

- **Frontend**: Vanilla JS (Zero dependencies) para máxima velocidad y control. CSS dinámico con variables y transiciones de 0.4s.
- **Backend**: FastAPI (Python 3.11+) operando en modo asíncrono para concurrencia masiva.
- **Data**: Strawberry GraphQL para consultas de árbol y SQLAlchemy para el fallback de base de datos local.
- **DevOps**: Git-flow automatizado con despliegue continuo en Render.com.
