# 📡 Pilar 3 — Contratos API & Especificación de Tags

> **Descripción:** Referencia técnica de los contratos de API consumidos (Graph), expuestos (FastAPI/GraphQL) y el lenguaje de etiquetas propietario `##Tag`.

> ⚠️ **Nota de auditoría:** El backend web (`main.py`) no envía el header `If-Match` en PATCH a Planner → Error `412 Precondition Failed`. El motor Python V2 **sí lo implementa** correctamente en `graph_patch()`.

---

## ☁️ Microsoft Graph API — Endpoints Consumidos

### Track Excel (V2: `planner_sync.py`)

| Endpoint | Método | Descripción | Auth |
|:---|:---:|:---|:---|
| `/me/planner/plans` | GET | Lista todos los planes del usuario | Client Credentials |
| `/planner/plans/{id}/tasks` | GET | Tareas de un plan | Client Credentials |
| `/planner/tasks/{id}` | PATCH | Actualiza título/status | Client Credentials + `If-Match` ✅ |

### Track Web (`backend/auth.py`, `backend/main.py`)

| Endpoint | Método | Descripción | Auth |
|:---|:---:|:---|:---|
| `/me/planner/plans` | GET | Lista planes del usuario autenticado | Device Flow |
| `/planner/plans/{id}/buckets` | GET | Buckets del plan | Device Flow |
| `/planner/buckets/{id}/tasks` | GET | Tareas del bucket | Device Flow |
| `/planner/tasks/{id}` | PATCH | Actualiza tarea | Device Flow (sin `If-Match` ⚠️) |
| `/planner/tasks/{id}` | DELETE | Elimina tarea | Device Flow |

---

## 🏷️ Especificación del Lenguaje `##Tag`

Las etiquetas se embeben en el campo `description` de cada tarea de Planner. Son parseadas por `parse_description()` en `planner_sync.py` usando regex.

### Sintaxis General
```
##NombreTag: valor
```

### Etiquetas Soportadas

| Tag | Aliases | Tipo Resultante | Ejemplo |
|:---|:---|:---:|:---|
| `##Dinero` | `##$`, `##Monto` | `float` | `##Dinero: 1500.00` |
| `##Fecha` | `##FechaPago`, `##Date` | `datetime` | `##Fecha: 2025-03-15` |
| `##B-Pagado` | `##Pagado`, `##Paid` | `bool` | `##B-Pagado: ON` |
| `##Prioridad` | `##P`, `##Priority` | `str` | `##Prioridad: Alta` |
| `##Notas` | `##Notes`, `##Obs` | `str` | `##Notas: Verificar con cliente` |

### Ejemplo de `description` completo
```
Reunión de seguimiento con proveedor
##Dinero: 2500.00
##Fecha: 2025-04-10
##B-Pagado: OFF
##Prioridad: Alta
##Notas: Pendiente firma de contrato
```

---

## ⚡ FastAPI Backend — Endpoints Expuestos

Base URL: `http://localhost:8000`

### Autenticación
| Endpoint | Método | Descripción |
|:---|:---:|:---|
| `/auth/login` | GET | Inicia Device Flow → devuelve `user_code` + `verification_uri` |
| `/auth/complete` | POST | Completa el flujo, obtiene token |
| `/auth/status` | GET | Verifica si hay sesión activa |

### REST CRUD
| Endpoint | Método | Graph? | DB Fallback? |
|:---|:---:|:---:|:---:|
| `/plans` | GET | ✅ | ✅ |
| `/plans` | POST | ❌ | ✅ Solo local |
| `/buckets?plan_id=` | GET | ✅ | ✅ |
| `/buckets` | POST | ❌ | ✅ Solo local |
| `/tasks?bucket_id=` | GET | ✅ | ✅ |
| `/tasks` | POST | ❌ | ✅ Solo local |
| `/tasks/{id}` | PUT | ✅ (sin `If-Match` ⚠️) | ✅ |
| `/tasks/{id}` | DELETE | ✅ | ✅ |

### GraphQL
Disponible en `http://localhost:8000/graphql` (Strawberry)

```graphql
query {
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

---

## 🗄️ Modelo Local (SQLAlchemy)

```python
Plan:    id(PK, str), name(str)
Bucket:  id(PK, str), name(str), plan_id(FK→Plan)
Task:    id(PK, str), title(str), percent_complete(int), bucket_id(FK→Bucket)
```
