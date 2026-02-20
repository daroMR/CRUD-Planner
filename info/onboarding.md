# 🧭 Onboarding — CRUD-Planner Supreme

## 🎯 ¿Qué es esto en 30 segundos?

Un ecosistema avanzado de gestión de proyectos que conecta **Excel y Web** con Microsoft Planner mediante una sincronización inteligente y una interfaz de usuario de alto impacto.

- **Track Excel (V2):** Sincronización bidireccional Planner ↔ Excel con semáforo inteligente y gestión de ETags.
- **Track Web (Premium UX):** SPA moderna con navegación por slides, diseño responsivo y CRUD total (incluyendo borrado de planes) sincronizado en tiempo real.

---

## 🚀 Guía Rápida

### Track Web (The Ghost Experience)

```bash
# 1. Backend FastAPI
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 2. Frontend Ultra-Moderno
# Accede a http://localhost:8000/app/index.html
# Disfruta de la navegación fluida por slides y el sidebar inteligente.
```

---

## 📂 Mapa de Documentación Estratégica

Ahora accesible directamente desde el **Centro de Documentación** interno en la App.

```
/docs/ (Arquitectura)
├── pilar1-ecosistema.md      ← Ecosistema Híbrido & Componentes
├── pilar2-flujo-datos.md     ← Sincronización Inteligente & ETags
├── pilar3-api-contratos.md   ← Graph API & GraphQL (The Golden Thread)
└── pilar4-adr.md             ← Registro de Decisiones Arquitectónicas

/info/ (Estrategia Master)
├── blueprint.d2              ← Golden Thread Map (D2 Visual Source)
├── onboarding.md             ← ESTÁS AQUÍ (Manual de Vuelo)
└── golden-thread.png         ← Mapa Estratégico (Visualización 4K)
```

---

## 🎨 Renderizar el Golden Thread Map (Protocolo Supreme)

Para actualizar el mapa visual, usa el motor `tala` (obligatorio para evitar cruces):

```bash
# Generación en alta resolución
d2 --layout tala --theme 200 info/blueprint.d2 info/golden-thread.svg
d2 --layout tala --theme 200 info/blueprint.d2 info/golden-thread.png

# Modo Desarrollo (Hot Reload)
d2 --watch --layout tala --theme 200 info/blueprint.d2
```

---

## 🔐 Infraestructura & Seguridad

El sistema opera con **Cero Configuración** en la nube para el usuario final, delegando la persistencia en Graph API o SQLite local.

```env
MS_GRAPH_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DATABASE_URL=sqlite:///./planner.db
```
