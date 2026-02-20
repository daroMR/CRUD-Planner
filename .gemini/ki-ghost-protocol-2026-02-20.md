# Knowledge Item: Ghost Protocol — CRUD-Planner Supreme Edition (v2)
# Fecha: 2026-02-20T01:27:00-06:00
# Hito: Auditoría completa + Fix de bugs + Actualización de 5 Pilares

## Arquitectura Dual (CRÍTICO)
- **Track Excel (V2):** `v2/planner_sync.py` + `v2/vba/SyncModule.bas` — Standalone, sin servidor.
- **Track Web:** `backend/main.py` + `frontend/` — FastAPI + SPA, requiere Docker.
- **V1 Legacy:** `vba/` (raíz) — VBA puro, obsoleto pero funcional.
- Los tracks NO se comunican entre sí. Comparten .env y Graph API.

## Bugs Corregidos (2026-02-20)
1. ✅ `planner_sync.py:145` — `xw.Book.caller()` ahora usa try/except.
2. ✅ `planner_sync.py:198-216` — Semáforo completo implementado (Conflict/Planner/Excel/Default).
3. ✅ `.gitignore` — Agregados token_cache.bin, planner.db, server_log.txt, outputs D2.

## Bugs Pendientes (NO corregidos aún)
- `backend/main.py` — PATCH a Graph sin If-Match header (412 error).
- `backend/graphql_schema.py:298` — delete_task compara string ID con integer PK.
- `planner_sync.py:101` — GET /planner/plans con client_credentials trae TODO el tenant.

## Documentación Actualizada
1. `/docs/pilar1-ecosistema.md` — ✅ Refleja arquitectura dual.
2. `/docs/pilar2-flujo-datos.md` — ✅ Semáforo de 4 estados en diagrama compare.
3. `/docs/pilar3-api-contratos.md` — ✅ Nota de auditoría If-Match.
4. `/docs/pilar4-adr.md` — ✅ Nuevo ADR-008 (Dual Track).
5. `/info/blueprint.d2` — ✅ Golden Thread con dos swim lanes.
6. `/info/onboarding.md` — ✅ Resumen actualizado.

## Archivos Obsoletos Identificados
- `vba/` (raíz) — V1 legacy, considerar renombrar a `v1-legacy/`.
- `docu/api_guide.md` — Redundante con `docs/pilar3-api-contratos.md`.
- `db/` — Carpeta vacía (solo .gitignore).
- `backend/server_log.txt` — No debería estar versionado.
- `backend/token_cache.bin` — Contiene refresh tokens reales.
