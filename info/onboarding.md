# 🧭 Onboarding — CRUD-Planner

## 🎯 ¿Qué es esto en 30 segundos?

Un repositorio con **dos productos independientes** conectados a Microsoft Planner:

- **Track Excel (V2):** Motor Python + VBA → sincroniza Planner ↔ Excel con semáforo visual e historia de cambios.
- **Track Web:** FastAPI + SPA → CRUD desde el browser, portable, sin Docker.

---

## 🚀 Guía Rápida

### Track Excel (V2)

```bash
# 1. Instalar dependencias
cd v2
pip install -r requirements.txt

# 2. Configurar credenciales
cp .env.example .env   # editar CLIENT_ID, TENANT_ID, CLIENT_SECRET

# 3. Importar módulos VBA en tu .xlsm
# Importar los 4 archivos de v2/vba/ en el editor VBA (Alt+F11)
# Asignar los botones del panel a:
#   LoginPlanner / ActualizarPlanner / CompararPlanner / SubirCambiosPlanner
```

### Track Web

```bash
# 1. Instalar dependencias
cd backend
pip install -r requirements.txt

# 2. Lanzar el backend
uvicorn main:app --reload

# 3. Abrir el frontend
# Abrir frontend/index.html en el browser (o servir con Live Server)

# 4. Para compartir externamente (sin servidor)
ngrok http 8000   # Genera URL pública temporal
```

---

## 📂 Mapa de Documentación

```
/docs/
├── pilar1-ecosistema.md      ← Arquitectura general y componentes
├── pilar2-flujo-datos.md     ← Diagramas de secuencia (Full/Compare/Push)
├── pilar3-api-contratos.md   ← Graph API, ##Tags, REST, GraphQL
└── pilar4-adr.md             ← 7 Decisiones de arquitectura

/info/
├── blueprint.d2              ← Golden Thread Map (código fuente D2)
├── golden-thread.svg         ← Diagrama vectorial (zoom infinito)
├── golden-thread.png         ← Diagrama para presentaciones
└── onboarding.md             ← ESTÁS AQUÍ
```

---

## 🎨 Renderizar el Golden Thread Map

```bash
# SVG (para browser / 4K)
d2 --layout elk --theme 200 info/blueprint.d2 info/golden-thread.svg

# PNG (para docs / presentaciones)
d2 --layout elk --theme 200 info/blueprint.d2 info/golden-thread.png

# Watch mode (hot reload al editar .d2)
d2 --watch --layout elk --theme 200 info/blueprint.d2
```

> Los archivos `.svg` y `.png` están en `.gitignore` — son generados, no versionados.

---

## 🔐 Variables de Entorno requeridas (`.env`)

```env
MS_GRAPH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
MS_GRAPH_TENANT_ID=common
MS_GRAPH_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_URL=sqlite:///./planner.db
```
