# KI: STITCH INTEGRATION PROTOCOL (Ghost Edition)
**Hito:** Configuración de Google Stitch MCP & Skills
**Fecha:** 2026-03-02

## 📝 Resumen Ejecutivo
Se ha dotado al ecosistema de agentes con el "Ojo de Stitch". Esta integración permite una transición fluida entre el diseño visual y la implementación técnica, activando el loop de retroalimentación diseño-código de forma local.

## 🛠️ Detalles de Ingeniería
- **Motor MCP:** Servidor `stitch` configurado vvia `npx @google/stitch-mcp-server`.
- **API Auth:** Clave `STITCH_KEY` persistida en `mcp_config.json`.
- **Skills Directory:** `.agent/skills/` (Symlinked).
- **Tooling Activo:** `design-md`, `react-components`, `stitch-loop`.

## 🧠 Memoria Operativa
Para activar flujos de diseño, invocar al agente Stitch mediante el protocolo MCP. Las habilidades están registradas y listas para usar en tareas de refactorización UI y creación de componentes.

> [!IMPORTANT]
> Mantener el archivo `.env` sincronizado para futuras rotaciones de claves. No compartir `mcp_config.json` públicamente.
