# 📊 Pilar 2 — Flujo de Datos 360°

> **Descripción:** Los tres ciclos de sincronización del sistema. Diagramas de secuencia para cada modo de operación.

---

## Modo 1: SYNC / PULL (Full)

Descarga **todos** los datos de Planner y reescribe Excel desde cero. Aplica estilo premium.

```
Usuario Excel        SyncModule.bas        planner_sync.py        MS Graph API
     │                     │                      │                      │
     │─── Click [🔄 Sync] ─▶│                      │                      │
     │                     │─── RunPython('full') ▶│                      │
     │                     │                      │── GET /me/planner/plans ──▶│
     │                     │                      │◀────────── [{id, title}] ──│
     │                     │                      │                      │
     │                     │                      │─ GET /plans/{id}/tasks ───▶│
     │                     │                      │◀──── [{title, desc, etag}] │
     │                     │                      │                      │
     │                     │         ┌────────────────────────────┐      │
     │                     │         │  parse_description(desc)   │      │
     │                     │         │  → ##Dinero → float        │      │
     │                     │         │  → ##Fecha  → datetime     │      │
     │                     │         │  → ##Check  → bool         │      │
     │                     │         └────────────────────────────┘      │
     │                     │                      │                      │
     │◀────── Escribe data + ETag en celdas ──────│                      │
     │◀────── apply_premium_styling() ────────────│                      │
```

---

## Modo 2: COMPARE (Semáforo 4-Estados)

Lee ETags de Excel, los compara con Planner **y** detecta ediciones locales. Pinta filas sin sobrescribir datos.

```
Usuario Excel        SyncModule.bas        planner_sync.py        MS Graph API
     │                     │                      │                      │
     │─── Click [🔍 Comp] ─▶│                      │                      │
     │                     │─── RunPython('comp') ▶│                      │
     │                     │                      │── GET /plans/{id}/tasks ──▶│
     │                     │                      │◀────── [{id, etag_P}] ────│
     │                     │                      │                      │
     │                     │         ┌──────────────────────────────────────┐
     │                     │         │ POR CADA TAREA:                      │
     │                     │         │                                      │
     │                     │         │  planner_changed = etag_P ≠ etag_E  │
     │                     │         │  excel_changed   = title/status ≠   │
     │                     │         │                                      │
     │                     │         │  IF ambos:  → 🟥 COLOR_CONFLICT     │
     │                     │         │  ELIF Planner: → 🟧 PLANNER_NEW     │
     │                     │         │  ELIF Excel:   → 🟦 EXCEL_NEW       │
     │                     │         │  ELSE:         → ⬜ DEFAULT          │
     │                     │         └──────────────────────────────────────┘
     │                     │                      │
     │◀────────── Aplica color en filas (sin borrar datos) ──────────────│
```

---

## Modo 3: PUSH 🆕 (Excel → Planner)

Lee ediciones de Excel y las sube a Planner usando `PATCH` con `If-Match` (ETag) para evitar sobrescribir trabajo ajeno.

```
Usuario Excel        SyncModule.bas        planner_sync.py        MS Graph API
     │                     │                      │                      │
     │─── Click [⬆️ Push] ─▶│                      │                      │
     │                     │─── RunPython('push') ▶│                      │
     │                     │                      │                      │
     │                     │         ┌─────────────────────────────────┐  │
     │                     │         │ POR CADA FILA DE EXCEL:         │  │
     │                     │         │  lee: task_id, etag, title, %  │  │
     │                     │         └─────────────────────────────────┘  │
     │                     │                      │                      │
     │                     │                      │── PATCH /planner/tasks/{id} ──▶│
     │                     │                      │── Header: If-Match: {etag} ───▶│
     │                     │                      │                      │
     │                     │         ┌─────────────────────────────────┐  │
     │                     │         │ HTTP 200: OK                   │  │
     │                     │         │   → Actualiza ETag en Excel    │  │
     │                     │         │ HTTP 412: Conflicto            │  │
     │                     │         │   → Pinta fila 🟥 CONFLICT     │  │
     │                     │         └─────────────────────────────────┘  │
```

---

## Modelo de Datos: Planner JSON → Excel Tabular

| Columna Excel | Campo Graph API | Transformación |
|:---|:---|:---|
| `Task ID` | `task.id` | Directo (string UUID) |
| `Bucket ID` | `task.bucketId` | Directo |
| `Task Title` | `task.title` | Directo |
| `Status` | `task.percentComplete` | 0→"Sin Iniciar", 50→"Iniciada", 100→"Completada" |
| `Start Date` | `task.startDateTime` | ISO 8601 → fecha Excel |
| `Due Date` | `task.dueDateTime` | ISO 8601 → fecha Excel |
| `Dinero` | `##Dinero` en `details.description` | Regex → float |
| `Fecha Pago` | `##Fecha` en `details.description` | Regex → datetime |
| `Pagado` | `##B-Pagado` en `details.description` | Regex → bool |
| `ETag` | `task['@odata.etag']` | Almacenado para Compare/Push |

---

## Fallback VBA (V1 Modo)

Cuando `HasPython() = False`, `SyncModule.bas` ejecuta `FetchAll_VBA()`:
- Solo descarga `title`, `bucketId`, `percentComplete`, `@odata.etag`.
- Sin parsing de `##Tags`. Sin Premium Styling.
- Disponible como red de seguridad sin dependencias externas.
