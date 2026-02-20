Attribute VB_Name = "SyncModule"
Option Explicit

' ╔══════════════════════════════════════════════════════════════╗
' ║  CRUD-Planner — Controlador Maestro de Sincronización      ║
' ║  Orquesta V2 (Python) con fallback a V1 (VBA puro)         ║
' ╚══════════════════════════════════════════════════════════════╝

''' <summary>
''' Botón: Iniciar Sesión (Device Flow)
''' </summary>
Public Sub LoginPlanner()
    On Error GoTo ErrorHandler
    ModAuth.Login
    Exit Sub
ErrorHandler:
    MsgBox "Error en Login: " & Err.Description, vbCritical
End Sub

''' <summary>
''' Botón: Actualizar (Pull/Fetch)
''' Descarga datos de Planner. Usa Python si está disponible para parsing avanzado.
''' </summary>
Public Sub ActualizarPlanner()
    On Error GoTo ErrorHandler
    
    If HasPython() Then
        Application.StatusBar = "CRÚD-Planner V2: Sincronizando con Python (Full Sync)..."
        RunPython ("import planner_sync; planner_sync.sync('full')")
        Application.StatusBar = False
    Else
        ' Fallback a V1 (VBA puro) si no hay Python/xlwings
        Application.StatusBar = "CRÚD-Planner V1: Sincronizando con VBA (Modo Legacy)..."
        FetchAll_VBA
        Application.StatusBar = False
    End If
    
    Exit Sub
ErrorHandler:
    Application.StatusBar = False
    MsgBox "Error al actualizar: " & Err.Description, vbCritical, "Crud-Planner"
End Sub

''' <summary>
''' Botón: Comparar (Diff Visual)
''' Solo disponible en V2 (Python).
''' </summary>
Public Sub CompararPlanner()
    On Error GoTo ErrorHandler
    
    If Not HasPython() Then
        MsgBox "La comparación visual requiere Python y xlwings instalados.", vbExclamation
        Exit Sub
    End If
    
    Application.StatusBar = "Analizando diferencias (ETags)..."
    RunPython ("import planner_sync; planner_sync.sync('compare')")
    Application.StatusBar = "Comparación finalizada. Revisa los colores en la hoja."
    
    Exit Sub
ErrorHandler:
    Application.StatusBar = False
    MsgBox "Error al comparar: " & Err.Description, vbCritical
End Sub

''' <summary>
''' Botón: Subir Cambios (Push)
''' Sube las ediciones locales a Planner.
''' </summary>
Public Sub SubirCambiosPlanner()
    On Error GoTo ErrorHandler
    
    If HasPython() Then
        Application.StatusBar = "CRÚD-Planner V2: Subiendo cambios con Python..."
        RunPython ("import planner_sync; planner_sync.sync('push')")
        Application.StatusBar = False
    Else
        MsgBox "La subida de cambios en modo Legacy (VBA) no está implementada en esta versión unificada.", vbInformation
    End If
    
    Exit Sub
ErrorHandler:
    Application.StatusBar = False
    MsgBox "Error al subir cambios: " & Err.Description, vbCritical
End Sub

' ═══════════════════════════════════════════════════════════════
'  LÓGICA LEGACY (V1) - Fallback VBA Puro
' ═══════════════════════════════════════════════════════════════

Private Sub FetchAll_VBA()
    Dim jsonPlans As Object
    Set jsonPlans = GraphGet("/me/planner/plans")
    
    If jsonPlans Is Nothing Then Exit Sub
    
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SHEET_TASKS)
    ws.Cells.ClearContents
    
    ' Encabezados básicos (sin columnas dinámicas)
    ws.Cells(1, 1).Value = "Plan Name"
    ws.Cells(1, 2).Value = "Bucket ID"
    ws.Cells(1, 3).Value = "Task ID"
    ws.Cells(1, 4).Value = "Title"
    ws.Cells(1, 5).Value = "Percent Complete"
    ws.Cells(1, 6).Value = "ETag"
    
    Dim row As Long: row = 2
    Dim plan As Object
    For Each plan In jsonPlans("value")
        Dim planId As String: planId = plan("id")
        Dim planTitle As String: planTitle = plan("title")
        
        Dim jsonTasks As Object
        Set jsonTasks = GraphGet("/planner/plans/" & planId & "/tasks")
        
        If Not jsonTasks Is Nothing Then
            Dim task As Object
            For Each task In jsonTasks("value")
                ws.Cells(row, 1).Value = planTitle
                ws.Cells(row, 2).Value = task("bucketId")
                ws.Cells(row, 3).Value = task("id")
                ws.Cells(row, 4).Value = task("title")
                ws.Cells(row, 5).Value = task("percentComplete")
                ws.Cells(row, 6).Value = task("@odata.etag")
                row = row + 1
            Next
        End If
    Next
    
    ws.Columns.AutoFit
    MsgBox "Sincronización Legacy (VBA) completada. Se cargaron " & (row - 2) & " tareas.", vbInformation
End Sub
