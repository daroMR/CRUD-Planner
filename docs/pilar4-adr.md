# 📋 Pilar 4 — Decisiones de Arquitectura (ADRs)

> **Formato:** Tarjetas de decisión modernas. Cada ADR documenta el contexto, la decisión tomada y sus consecuencias.

---

## ADR-001 · Arquitectura Híbrida (VBA + Python)

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada |
| **Decisión** | VBA actúa como **orquestador y capa UX** (botones, mensajes, auth). Python actúa como **motor de datos** (sync, parse, push, styling). |
| **Alternativas descartadas** | Solo VBA (limitado, sin parsing de tags), Solo Python (requiere terminal, no amigable para usuarios finales). |
| **Consecuencias** | ✅ UX familiar (Excel). ✅ Potencia de Python. ✅ Fallback nativo VBA. ❌ Dos lenguajes que mantener. |

---

## ADR-002 · xlwings como Bridge VBA → Python

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada |
| **Decisión** | `xlwings` es el conector entre VBA (`RunPython()`) y el script `.py`. Permite leer/escribir Excel desde Python en tiempo real. |
| **Alternativas** | `openpyxl` (no puede acceder al libro abierto activo), `win32com` (más bajo nivel, más frágil). |
| **Consecuencias** | ✅ Acceso al libro abierto sin cerrarlo. ✅ xlwings activo con `xw.Book.caller()`. ❌ Requiere `xlwings.addin` instalado y xlwings en el entorno Python. |

---

## ADR-003 · ETags para Concurrencia Optimista

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada |
| **Decisión** | Usar `@odata.etag` de Planner para detectar cambios sin comparar campo a campo. Almacenar el ETag en Excel y enviarlo como `If-Match` en las peticiones PATCH. |
| **Limitación conocida** | Cambios en `description` (donde viven los `##Tags`) pueden **no actualizar** el ETag del task principal. El ETag de `/tasks/{id}` y `/tasks/{id}/details` son distintos. |
| **Consecuencias** | ✅ Detección eficiente. ✅ Previene sobrescritura accidental. ❌ Los cambios de solo `##Tags` podrían no ser detectados por Compare. |

---

## ADR-004 · Push Bidireccional con Manejo de Conflictos 412

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada (V2 definitiva) |
| **Decisión** | El modo `push` en `planner_sync.py` envía `PATCH` a Graph con el `If-Match` ETag guardado en Excel. Si otro usuario modificó la tarea, Graph devuelve `412 Precondition Failed`. El sistema captura el error y pinta la fila 🟥 (CONFLICT) sin perder datos locales. |
| **Consecuencias** | ✅ Bidireccionalidad real: Excel → Planner. ✅ Seguridad: ningún cambio se pierde silenciosamente. ✅ Al hacer Push exitoso, se actualiza el ETag en Excel automáticamente. |

---

## ADR-005 · ##Tags en `description` (Campo Libre)

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada |
| **Decisión** | Planner no tiene campos personalizados nativos. Se usa el campo `description` para embeber metadata estructurada con el prefijo `##Clave: Valor`. |
| **Alternativas** | Usar checklist items de Planner (limitado a texto), API de Graph Extensions (compleja y requiere schema registrado en Azure). |
| **Consecuencias** | ✅ Cero configuración Azure adicional. ✅ Legible por humanos en Planner. ❌ Descripción "contaminada" con metadata técnica. ❌ Parsing frágil si el usuario edita la descripción manualmente. |

---

## ADR-006 · Despliegue Web Portable (Sin Docker)

| Campo | Detalle |
|:---|:---|
| **Estado** | 🔄 Evaluando |
| **Contexto** | El `docker-compose.yml` existente consume recursos significativos en laptops. Se busca una alternativa para compartir el Track Web sin overhead de contenedores. |
| **Opciones evaluadas** | Ver tabla abajo. |
| **Recomendación** | Tres niveles según el contexto. |
| **Consecuencias** | ✅ Sin Docker. ✅ Token Graph sigue funcionando desde cualquier IP. ⚠️ En Render Free el token_cache.bin se pierde al reiniciar — el usuario debe re-autenticarse. |

**Tabla de Opciones de Deploy:**

| Opción | Costo | Uso ideal |
|:---|:---:|:---|
| `python main.py` (local) | $0 | Desarrollo diario |
| `ngrok http 8000` (local + URL pública) | $0 | Compartir demo sin deploy |
| Render.com Free | $0 | Demo externa (duerme 15 min sin uso) |
| Render.com Starter | $7/mes | Producción ligera, siempre activo |

---

## ADR-007 · Dos Tracks en un Solo Repo

| Campo | Detalle |
|:---|:---|
| **Estado** | ✅ Adoptada (de facto) |
| **Decisión** | Track Excel (`v2/`) y Track Web (`backend/`, `frontend/`) coexisten en el mismo repositorio porque comparten `.env` y la misma fuente de verdad (Planner). |
| **Consecuencias** | ✅ Un solo `git clone`. ✅ Una sola fuente de credenciales. ❌ Ambigüedad para nuevos colaboradores. ❌ Sin README raíz claro. |
| **Deuda técnica** | Crear un `README.md` completo en la raíz que explique los dos tracks. |
