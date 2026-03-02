# 🔌 Pilar 3 — API & Contratos Supreme

> **Descripción:** El Hilo Dorado de la información. Especificación de contratos REST, GraphQL y el esquema de metadatos `##Tags`.

---

## 🌐 Microsoft Graph API (Contract)

El sistema se integra con los enpoints de Planner v1.0 utilizando una estrategia de **Lazy ETag Management**.

| Entidad | Endpoint | Verbo | Concurrencia |
|:---|:---|:---|:---|
| **Plan** | `/planner/plans/{id}` | `GET, PATCH, DELETE` | If-Match (ETag) |
| **Bucket** | `/planner/buckets/{id}` | `GET, PATCH, DELETE` | If-Match (ETag) |
| **Task** | `/planner/tasks/{id}` | `GET, PATCH, DELETE` | If-Match (ETag) |

> [!IMPORTANT]
> El borrado de planes es definitivo. El sistema implementa un pre-fetch de metadatos para asegurar que el `If-Match` sea válido en el momento de la ejecución.

---

## 🕸️ GraphQL Engine (Hierarchy)

Para evitar el *over-fetching* y soportar una UI por slides, el sistema expone un esquema jerárquico.

```graphql
query PlannerSummary {
  plans {
    id
    name
    buckets {
      id
      name
      tasks {
        id
        title
        percentComplete
      }
    }
  }
}
```

- **Motor**: Strawberry GraphQL (FastAPI).
- **Resolver**: Conectado a un contexto híbrido que detecta la fuente de datos óptima (Graph o DB Local).

---

## 🏷️ Esquema de Metadatos: The Golden Thread

El "Hilo Dorado" se teje en el campo `description` de las tareas mediante una sintaxis de etiquetas enriquecidas.

| Etiqueta | Tipo | Uso en Excel | Uso en Middleware |
|:---|:---|:---|:---|
| `##D-` | Dinero (`float`) | Columna Financiera | Badge de Costo |
| `##F-` | Fecha (`date`) | Columna de Pago | Calendario |
| `##B-` | Booleano (`bool`) | Checkbox | Toggle Switch |
| `## [Key]` | Dinámico | Campo Programático | Columna Bento-Grid |

---

## 🔐 Contratos Local vs Cloud

El sistema detecta automáticamente el destino mediante la naturaleza del ID:
- **ID Numérico (1, 2, 105...)**: Persistencia en base de datos local (SQLAlchemy).
- **ID UUID (String largo)**: Operación directa sobre Microsoft Graph.

Esta dualidad garantiza que el proyecto sea **portable y resiliente** ante cualquier entorno.
