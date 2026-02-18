# MS Planner Excel VBA Integration

Este directorio contiene los módulos de VBA necesarios para integrar Excel con Microsoft Planner.

## Requisitos
1. **Microsoft Excel** (versión reciente con soporte para VBA).
2. **VBA-JSON**: Se requiere la librería `VBA-JSON` (JsonConverter.bas) para procesar las respuestas de la API.
   - Descargar desde: [VBA-JSON GitHub](https://github.com/VBA-tools/VBA-JSON)
3. **Microsoft Scripting Runtime**: Habilitar en `Herramientas -> Referencias` dentro del editor de VBA.
4. **Microsoft WinHTTP Services version 5.1**: Habilitar en `Herramientas -> Referencias`.

## Cómo Importar
1. Abre tu archivo Excel (`.xlsm`).
2. Presiona `Alt + F11` para abrir el Editor de VBA.
3. Haz clic derecho en el proyecto -> `Import File...` y selecciona los archivos `.bas` de esta carpeta.
4. Asegúrate de configurar las referencias mencionadas arriba.

## Módulos
- **ModConfig.bas**: Configuración de Client ID y Endpoints.
- **ModAuth.bas**: Lógica de autenticación (Device Code Flow).
- **ModGraphAPI**: Funciones genéricas para llamar a MS Graph.
- **ModSync**: Funciones de sincronización (Fetch, Pull, Push).
