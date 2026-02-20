# ⚖️ Pilar 4 — Decisiones Arquitectónicas (ADR) Supreme

> **Descripción:** El registro de por qué tomamos las decisiones que tomamos. Consistencia y transparencia estratégica.

---

## ADR 007: Navegación de Alto Impacto por Slides
- **Contexto**: El dashboard anterior sufría de fatiga por scroll infinito, dificultando la navegación rápida.
- **Decisión**: Implementar un sistema de navegación horizontal basado en **Slides** y un **Sidebar Fijo**.
- **Impacto**: Mejora significativa en la densidad de información y la usabilidad móvil (Full Responsive).

---

## ADR 008: Soporte Real de Borrado de Planes en Graph
- **Contexto**: Se creía erróneamente que Graph API no permitía el borrado directo de planes, forzando un fallback local.
- **Decisión**: Implementar el soporte oficial `DELETE /planner/plans/{id}` mediante la gestión reactiva de ETags (If-Match).
- **Impacto**: El sistema ahora es 100% fiel a las capacidades reales de Microsoft, eliminando advertencias obsoletas de la UI.

---

## ADR 009: Centro de Documentación Integrado
- **Contexto**: La documentación técnica y estratégica estaba dispersa en el repositorio, oculta para el usuario final.
- **Decisión**: Crear un "Slide de Documentación" que sirve archivos estáticos (`/info` y `/docs`) directamente desde el servidor Ghost (FastAPI).
- **Impacto**: Centralización masiva del conocimiento. El usuario puede auditar la arquitectura sin salir de la App.

---

## ADR 010: Arquitectura Defensiva en Frontend
- **Contexto**: La evolución rápida del HTML causó errores de referencia nula (`null`) en JavaScript.
- **Decisión**: Implementar un protocolo de **Programación Defensiva** con null-checks obligatorios y validaciones de formulario enriquecidas.
- **Impacto**: Estabilidad total en la sección de Gestión. Errores de consola reducidos a cero.

---

> [!NOTE]
> Para consultar ADRs antiguos (001-006), revisar el historial de commits o los logs del Protocolo Ghost inicial.
