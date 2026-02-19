# Documentación de APIs - CRUD Planner

Esta carpeta contiene la guía rápida de uso para las APIs del sistema CRUD Planner, tanto para el desarrollo del Dashboard Web como para integraciones externas.

## 🚀 Cómo empezar

El backend está desarrollado con **FastAPI** y ofrece tres formas de interacción:

1.  **Dashboard Web**: Interfaz moderna en `http://localhost:3000`.
2.  **API REST**: Endpoints estándar para operaciones CRUD.
3.  **GraphQL**: Consultas flexibles para resúmenes de datos.

---

## 🔐 Autenticación (Microsoft Graph)

El sistema utiliza el flujo de **Device Code** para conectar con Microsoft Planner.

- `GET /auth/login`: Inicia el flujo y devuelve un `user_code` y un `verification_uri`.
- `POST /auth/complete`: Verifica si el usuario ha completado el login.
- `GET /auth/status`: Comprueba si hay una sesión activa.

---

## 📡 Endpoints REST (Modelos de Planner)

Todos los endpoints devuelven y aceptan JSON. Los IDs son **strings** (compatibles con MS Graph).

### 📁 Planes
- `GET /plans`: Lista todos los planes del usuario conectado.
- `POST /plans`: Crea un nuevo plan (local/fallback).

### 🗄️ Buckets
- `GET /buckets?plan_id={id}`: Lista los buckets de un plan específico.
- `POST /buckets`: Crea un nuevo bucket.

### 📝 Tareas
- `GET /tasks?bucket_id={id}`: Lista las tareas de un bucket.
- `POST /tasks`: Crea una nueva tarea.
- `PUT /tasks/{id}`: Actualiza una tarea (título, completado, etc.).
- `DELETE /tasks/{id}`: Eliminar una tarea de Planner.

---

## 📊 GraphQL

Disponible en `http://localhost:8000/graphql`. Permite obtener toda la jerarquía en una sola llamada.

### Consulta de Resumen (Query)
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

## 🛠️ Documentación Interactiva
FastAPI genera automáticamente documentación detallada:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
