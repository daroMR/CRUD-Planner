# CRUD-Planner

Sistema de sincronización con Microsoft Planner. Dos productos independientes en un mismo repo.

---

## 🗺️ ¿Qué hay aquí?

| Track | Carpeta | Stack | ¿Para qué? |
|:---|:---|:---|:---|
| **Excel (V2)** | `v2/` | Python + xlwings + VBA | Sync inteligente Planner ↔ Excel con semáforo visual |
| **Web** | `backend/` + `frontend/` | FastAPI + SQLAlchemy + SPA | Dashboard CRUD en el browser |

> Los dos tracks **no se comunican entre sí**. Comparten credenciales Azure (`.env`) y la fuente de datos (Microsoft Planner vía Graph API).

---

## ⚡ Inicio Rápido

### Track Excel (V2)
```bash
cd v2
pip install -r requirements.txt
# Importar los módulos de v2/vba/ en tu .xlsm (Alt+F11)
# Botones: LoginPlanner / ActualizarPlanner / CompararPlanner / SubirCambiosPlanner
```

### Track Web
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Abrir frontend/index.html en el browser
# Para compartir externamente: ngrok http 8000
```

---

## 🔐 Configuración

Copia `.env` y rellena tus credenciales de Azure:
```
MS_GRAPH_CLIENT_ID=...
MS_GRAPH_TENANT_ID=common
MS_GRAPH_CLIENT_SECRET=...
DATABASE_URL=sqlite:///./planner.db
```

---

## 📚 Documentación

| Pilar | Contenido |
|:---|:---|
| [Ecosistema](docs/pilar1-ecosistema.md) | Arquitectura general, mapa de componentes |
| [Flujo de Datos](docs/pilar2-flujo-datos.md) | Diagramas Full / Compare / Push |
| [API & Tags](docs/pilar3-api-contratos.md) | Contratos Graph, `##Tags`, REST, GraphQL |
| [Decisiones](docs/pilar4-adr.md) | 7 ADRs de arquitectura |
| [Golden Thread](info/onboarding.md) | Onboarding + comandos D2 |
