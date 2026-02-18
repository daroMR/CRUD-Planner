Attribute VB_Name = "ModGraphAPI"
Option Explicit

''' <summary>
''' Realiza una petición GET a Microsoft Graph
''' </summary>
Public Function GraphGet(endpoint As String) As Object
    Set GraphGet = GraphRequest("GET", endpoint, "")
End Function

''' <summary>
''' Realiza una petición PATCH a Microsoft Graph (para actualizaciones)
''' </summary>
Public Function GraphPatch(endpoint As String, body As String, eTag As String) As Object
    Set GraphPatch = GraphRequest("PATCH", endpoint, body, eTag)
End Function

''' <summary>
''' Función centralizada para peticiones HTTP
''' </summary>
Private Function GraphRequest(method As String, endpoint As String, body As String, Optional eTag As String = "") As Object
    If AccessToken = "" Then LoadTokens
    
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
    
    ' Manejo de ETags para Planner (optimistic concurrency)
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
        ' Token expirado? Intentar refresh
        If ModAuth.RefreshTokenSession() Then
            ' Reintentar la misma petición con el nuevo token
            Set GraphRequest = GraphRequest(method, endpoint, body, eTag)
        Else
            MsgBox "Sesión expirada y no se pudo renovar. Por favor, inicia sesión de nuevo.", vbCritical
            Set GraphRequest = Nothing
        End If
    Else
        MsgBox "Error en Graph API (" & http.Status & "): " & http.ResponseText, vbCritical
        Set GraphRequest = Nothing
    End If
End Function
