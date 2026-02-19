Attribute VB_Name = "SyncModule"
Option Explicit

''' <summary>
''' Subrutina principal: Ejecuta la sincronización completa.
''' Descarga todos los datos de Microsoft Planner y actualiza la hoja activa,
''' aplicando el formato premium y sobrescribiendo los datos locales.
''' </summary>
Public Sub ActualizarPlanner()
    On Error GoTo ErrorHandler
    
    ' Mostrar progreso en la barra de estado de Excel
    Application.StatusBar = "Iniciando sincronización completa con Planner (V2)..."
    
    ' Llamada a Python usando el puente de xlwings
    ' El modo 'full' reconstruye la tabla y aplica estilos.
    RunPython ("import planner_sync; planner_sync.sync('full')")
    
    ' Limpiar la barra de estado al finalizar
    Application.StatusBar = False
    Exit Sub

ErrorHandler:
    ' Asegurar que la barra de estado se limpie incluso si hay error
    Application.StatusBar = False
    MsgBox "Ocurrió un error durante la sincronización: " & vbCrLf & Err.Description, vbCritical, "Crud-Planner V2"
End Sub

''' <summary>
''' Subrutina de Comparación: Busca diferencias sin modificar datos.
''' Compara los ETags de Planner con los de Excel y resalta en naranja
''' las filas que han sido actualizadas en la nube.
''' </summary>
Public Sub CompararPlanner()
    On Error GoTo ErrorHandler
    
    ' Notificar al usuario que la comparación está en curso
    Application.StatusBar = "Analizando diferencias entre Excel y Planner... por favor espere."
    
    ' Ejecuta el script en modo 'compare' para activar el resaltado visual
    RunPython ("import planner_sync; planner_sync.sync('compare')")
    
    ' Informar el resultado en la barra de estado
    Application.StatusBar = "Comparación finalizada. Las filas resaltadas en NARANJA tienen cambios en Planner."
    Exit Sub

ErrorHandler:
    Application.StatusBar = False
    MsgBox "Ocurrió un error al comparar los datos: " & vbCrLf & Err.Description, vbCritical, "Crud-Planner V2"
End Sub
