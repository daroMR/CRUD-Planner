# 📊 Pilar 2 — Flujo de Datos 360° Supreme

> **Descripción:** Ciclos de sincronización de alta fidelidad. Gestión de estados, ETags y persistencia híbrida.

---

## 🔄 Modo 1: SYNC / PULL (Full)

Sincronización total de la jerarquía Planner → UX. 

- **Backend**: Realiza llamadas recursivas a Graph API (Plans -> Buckets -> Tasks).
- **Procesamiento**: El motor `parse_description` decodifica los metadatos `##Dinero`, `##Fecha` y `##B-`.
- **Frontend**: Renderizado jerárquico dinámico con `renderResumenArbol` y actualización del `Maestro de Datos`.

---

## 🔍 Modo 2: INTELLIGENT COMPARE

Comparación reactiva basada en ETags para prevenir sobrescritura de datos.

1. **Lectura local**: El sistema carga los ETags almacenados en el estado actual.
2. **Consulta remota**: Obtiene los headers `@odata.etag` más recientes de Microsoft Planner.
3. **Validación**:
    - `planner_changed`: `@odata.etag` remoto ≠ local.
    - `excel_changed`: Datos en el grid ≠ datos originales.
4. **Semáforo**: Visualización de conflictos 🟥, cambios en Planner 🟧 y cambios locales 🟦.

---

## ⬆️ Modo 3: PUSH SUPREME (Create / Update / Delete)

Gestión total de ciclo de vida con integridad garantizada mediante `If-Match`.

### Actualización (PATCH)
- Envía el ETag más reciente en el header `If-Match`.
- Si el servidor devuelve `412 Precondition Failed`, se activa el protocolo de resolución de conflictos.

### Creación (POST)
- **Bucket/Task**: Requiere el UUID del contenedor superior.
- **Plan**: Soporte para creación de `plannerPlan` con asignación automática de ID.

### Borrado (DELETE) 🆕
- **Real Graph Delete**: Soporte nativo para `DELETE /planner/plans/{id}`.
- **Lazy ETag Fetch**: Si no se dispone del ETag, el sistema realiza una petición `GET` previa para obtenerlo y asegurar el borrado atómico.

---

## 🏛️ Persistencia Híbrida (Fallback)

Ante fallos de red o falta de tokens:
1. **SQLite Local**: La arquitectura detecta si el ID es un entero (local) o UUID (Graph).
2. **Sincronización Silenciosa**: El sistema intenta persistir en ambas capas cuando es posible, garantizando que el usuario nunca pierda su trabajo.
