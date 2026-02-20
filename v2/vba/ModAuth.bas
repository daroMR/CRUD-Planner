Attribute VB_Name = "ModAuth"
Option Explicit

' ╔══════════════════════════════════════════════════════════════╗
' ║  CRUD-Planner — Autenticación Device Flow (Definitiva)     ║
' ║  Desde V1: Auth directa desde VBA sin servidor backend     ║
' ╚══════════════════════════════════════════════════════════════╝

' Función auxiliar para esperar (64 bits compatible)
#If VBA7 Then
    Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As LongPtr)
#Else
    Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
#End If

''' <summary>
''' Inicia Device Flow: muestra código al usuario para autenticarse en la web de MS.
''' </summary>
Public Sub Login()
    Dim http As Object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    Dim url As String: url = DEVICE_CODE_URL
    Dim body As String
    body = "client_id=" & CLIENT_ID & "&scope=" & SCOPES
    
    http.Open "POST", url, False
    http.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
    http.Send body
    
    If http.Status = 200 Then
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.ResponseText)
        
        Dim userCode As String: userCode = json("user_code")
        Dim verificationUrl As String: verificationUrl = json("verification_uri")
        Dim deviceCode As String: deviceCode = json("device_code")
        Dim interval As Long: interval = json("interval")
        
        ' Copiar código al portapapeles para conveniencia
        Dim clipboard As Object
        Set clipboard = CreateObject("new:{1C3B4210-F441-11CE-B9EA-00AA006B1A69}")
        clipboard.SetText userCode
        clipboard.PutInClipboard
        
        MsgBox "1. Visita: " & verificationUrl & vbCrLf & _
               "2. Pega el código: " & userCode & " (ya está en tu portapapeles)" & vbCrLf & vbCrLf & _
               "Haz clic en Aceptar DESPUÉS de completar la autenticación.", _
               vbInformation, "Crud-Planner — Autenticación"
        
        PollForToken deviceCode, interval
    Else
        MsgBox "Error al obtener el código de dispositivo: " & http.ResponseText, vbCritical
    End If
End Sub

''' <summary>
''' Sondea el endpoint de token hasta obtener el access_token.
''' </summary>
Private Sub PollForToken(deviceCode As String, interval As Long)
    Dim http As Object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    Dim url As String: url = TOKEN_URL
    Dim body As String: body = "grant_type=urn:ietf:params:oauth:grant-type:device_code" & _
                               "&client_id=" & CLIENT_ID & _
                               "&device_code=" & deviceCode
    
    Dim success As Boolean: success = False
    Dim attempts As Integer: attempts = 0
    
    Application.StatusBar = "Esperando autenticación del usuario..."
    
    Do While Not success And attempts < 30
        http.Open "POST", url, False
        http.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
        http.Send body
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.ResponseText)
        
        If http.Status = 200 Then
            SaveTokens json("access_token"), json("refresh_token"), json("expires_in")
            Application.StatusBar = False
            MsgBox "¡Autenticación exitosa! Ya puedes sincronizar.", vbInformation, "Crud-Planner"
            success = True
        ElseIf json("error") = "authorization_pending" Then
            Sleep interval * 1000
            attempts = attempts + 1
        Else
            Application.StatusBar = False
            MsgBox "Error de autenticación: " & json("error_description"), vbCritical
            Exit Sub
        End If
    Loop
    
    If Not success Then
        Application.StatusBar = False
        MsgBox "Tiempo de autenticación agotado. Intenta de nuevo.", vbExclamation
    End If
End Sub

''' <summary>
''' Renueva el Access Token usando el Refresh Token.
''' </summary>
Public Function RefreshTokenSession() As Boolean
    If RefreshToken = "" Then LoadTokens
    If RefreshToken = "" Then
        RefreshTokenSession = False
        Exit Function
    End If
    
    Dim http As Object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    Dim url As String: url = TOKEN_URL
    Dim body As String: body = "grant_type=refresh_token" & _
                               "&client_id=" & CLIENT_ID & _
                               "&refresh_token=" & RefreshToken
    
    http.Open "POST", url, False
    http.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
    http.Send body
    
    If http.Status = 200 Then
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.ResponseText)
        SaveTokens json("access_token"), json("refresh_token"), json("expires_in")
        RefreshTokenSession = True
    Else
        RefreshTokenSession = False
    End If
End Function
