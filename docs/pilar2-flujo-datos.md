# Pilar 2: Flujo de Datos (Middleware VBA Sync)

Este diagrama detalla el "Hilo Dorado" de la información desde el sistema local (VBA) hasta el núcleo de Microsoft Planner, pasando por nuestro Middleware de "Cose" (Stitch).

## Diagrama de Secuencia: Sync de Columnas Personalizadas

```mermaid
sequenceDiagram
    autonumber
    participant VBA as Excel/VBA Client
    participant MW as Stitch Middleware (FastAPI/Python)
    participant Graph as Microsoft Graph API
    participant Planner as Microsoft Planner (Data Store)

    Note over VBA, Planner: Inicio de Sincronización de Campo Personalizado

    VBA->>MW: POST /api/sync (Action: Update "Costo")
    MW->>MW: Parser Markdown (JSON -> ## Costo\nValue)
    
    MW->>Graph: GET /tasks/{id} (Fetch Details & ETag)
    Graph-->>MW: 200 OK (Current DescriptionContent)
    
    MW->>MW: Merge Content (Preserve Human Text + Update Keys)
    
    MW->>Graph: PATCH /tasks/{id}/details (Update Description)
    Note right of MW: Header: If-Match {ETag}
    
    Graph->>Planner: Persistencia de Datos
    Planner-->>Graph: Acknowledgement
    Graph-->>MW: 204 No Content (Success)
    
    MW-->>VBA: 200 OK (Sync Complete)
    
    Note over VBA, Planner: El Dashboard Web refleja el cambio instantáneamente vía Stitch UI
```

> [!TIP]
> El uso de **ETags** es crítico para evitar colisiones cuando múltiples usuarios (o el script VBA y un humano) editan la misma tarea simultáneamente.

## Estados de Sincronización UI
- **Azul Pulsante**: Sincronización en curso.
- **Verde Sólido**: Datos persistidos y validados.
- **Rojo Alerta**: Conflicto de ETag (requiere intervención manual).
