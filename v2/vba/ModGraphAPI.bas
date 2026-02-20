Attribute VB_Name = "ModGraphAPI"
Option Explicit

' ╔══════════════════════════════════════════════════════════════╗
' ║  CRUD-Planner — Graph API Helper (Definitiva)              ║
' ║  Desde V1: GET/PATCH con If-Match, retry 401 automático    ║
' ╚══════════════════════════════════════════════════════════════╝

''' <summary>
''' Realiza una petición GET a Microsoft Graph.
''' </summary>
Public Function GraphGet(endpoint As String) As Object
    Set GraphGet = GraphRequest("GET", endpoint, "")
End Function

''' <summary>
''' Realiza una petición PATCH con If-Match ETag (concurrencia optimista).
''' </summary>
Public Function GraphPatch(endpoint As String, body As String, eTag As String) As Object
    Set GraphPatch = GraphRequest("PATCH", endpoint, body, eTag)
End Function

''' <summary>
''' Función centralizada para peticiones HTTP a Graph.
''' Maneja: Authorization, Content-Type, If-Match, retry 401.
''' </summary>
Private Function GraphRequest(method As String, endpoint As String, body As String, Optional eTag As String = "") As Object
    If AccessToken = "" Then LoadTokens
    
    ' Verificar si el token ha expirado
    If TokenExpiry > 0 And Now > TokenExpiry Then
        If Not ModAuth.RefreshTokenSession() Then
            MsgBox "Tu sesión ha expirado. Por favor, inicia sesión de nuevo con LoginPlanner.", vbExclamation, "Crud-Planner"
            Set GraphRequest = Nothing
            Exit Function
        End If
    End If
    
    Dim http As Object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    Dim fullUrl As String
    If Left(endpoint, 4) = "http" Then
        fullUrl = endpoint
    Else
        fullUrl = GRAPH_API_BASE & endpoint
    End If
    
    http.Open method, fullUrl, False
    http.SetRequestHeader "Authorization", "Bearer " & AccessToken
    http.SetRequestHeader "Content-Type", "application/json"
    
    ' If-Match header para operaciones PATCH en Planner (concurrencia optimista)
    If eTag <> "" Then
        http.SetRequestHeader "If-Match", eTag
    End If
    
    http.Send body
    
    If http.Status >= 200 And http.Status < 300 Then
        If http.ResponseText <> "" Then
            Set GraphRequest = JsonConverter.ParseJson(http.ResponseText)
        Else
            Set GraphRequest = Nothing
        End If
    ElseIf http.Status = 401 Then
        ' Token expirado — intentar refresh automático
        If ModAuth.RefreshTokenSession() Then
            Set GraphRequest = GraphRequest(method, endpoint, body, eTag)
        Else
            MsgBox "Sesión expirada. Por favor, ejecuta LoginPlanner.", vbCritical, "Crud-Planner"
            Set GraphRequest = Nothing
        End If
    ElseIf http.Status = 412 Then
        ' Precondition Failed — alguien más modificó el recurso
        MsgBox "Conflicto: La tarea fue modificada por otro usuario." & vbCrLf & _
               "Ejecuta ActualizarPlanner para obtener la versión más reciente.", _
               vbExclamation, "Crud-Planner — Conflicto"
        Set GraphRequest = Nothing
    Else
        MsgBox "Error en Graph API (" & http.Status & "): " & http.ResponseText, vbCritical, "Crud-Planner"
        Set GraphRequest = Nothing
    End If
End Function
