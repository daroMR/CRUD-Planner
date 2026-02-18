Attribute VB_Name = "ModSync"
Option Explicit

''' <summary>
''' Fetch: Descarga todos los planes y tareas del usuario.
''' </summary>
Public Sub FetchAll()
    Dim jsonPlans As Object
    Set jsonPlans = GraphGet("/me/planner/plans")
    
    If jsonPlans Is Nothing Then Exit Sub
    
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SHEET_TASKS)
    ws.Cells.ClearContents
    
    ' Encabezados
    ws.Cells(1, 1).Value = "Plan Name"
    ws.Cells(1, 2).Value = "Task ID"
    ws.Cells(1, 3).Value = "Title"
    ws.Cells(1, 4).Value = "Percent Complete"
    ws.Cells(1, 5).Value = "ETag"
    
    Dim row As Long: row = 2
    Dim plan As Object
    For Each plan In jsonPlans("value")
        Dim planId As String: planId = plan("id")
        Dim planTitle As String: planTitle = plan("title")
        
        ' Obtener tareas del plan
        Dim jsonTasks As Object
        Set jsonTasks = GraphGet("/planner/plans/" & planId & "/tasks")
        
        If Not jsonTasks Is Nothing Then
            Dim task As Object
            For Each task In jsonTasks("value")
                ws.Cells(row, 1).Value = planTitle
                ws.Cells(row, 2).Value = task("id")
                ws.Cells(row, 3).Value = task("title")
                ws.Cells(row, 4).Value = task("percentComplete")
                ws.Cells(row, 5).Value = task("@odata.etag")
                row = row + 1
            Next
        End If
    Next
    
    MsgBox "Fetch completado. Se cargaron " & (row - 2) & " tareas.", vbInformation
End Sub

''' <summary>
''' Pull: Actualiza las tareas locales con los datos más recientes de Planner.
''' </summary>
Public Sub PullChanges()
    ' Por simplicidad, ejecutaremos un FetchAll
    ' En una implementación avanzada, compararíamos IDs y ETags
    FetchAll
End Sub

''' <summary>
''' Push: Sube los cambios locales a Planner.
''' Enviará un PATCH por cada tarea en la hoja "Tareas".
''' </summary>
Public Sub PushChanges()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets(SHEET_TASKS)
    
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 2).End(xlUp).row
    
    Dim i As Long
    Dim count As Integer: count = 0
    
    For i = 2 To lastRow
        Dim taskId As String: taskId = ws.Cells(i, 2).Value
        Dim title As String: title = ws.Cells(i, 3).Value
        Dim percent As Long: percent = ws.Cells(i, 4).Value
        Dim eTag As String: eTag = ws.Cells(i, 5).Value
        
        ' Crear el cuerpo del JSON para el PATCH
        Dim body As String
        body = "{""title"":""" & title & """,""percentComplete"":" & percent & "}"
        
        ' Enviar petición a Graph API
        Dim result As Object
        Set result = GraphPatch("/planner/tasks/" & taskId, body, eTag)
        
        If Not result Is Nothing Then
            ' Actualizar el ETag local con el nuevo devuelto por el servidor
            ws.Cells(i, 5).Value = result("@odata.etag")
            count = count + 1
        End If
    Next
    
    MsgBox "Push completado. Se actualizaron " & count & " tareas.", vbInformation
End Sub
