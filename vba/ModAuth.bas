Attribute VB_Name = "ModAuth"
Option Explicit

''' <summary>
''' Inicia el flujo de Device Code.
''' Muestra un cuadro de mensaje con el código que el usuario debe ingresar en la web de MS.
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
        ' Parsear respuesta (Requiere JsonConverter)
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.ResponseText)
        
        Dim userCode As String: userCode = json("user_code")
        Dim verificationUrl As String: verificationUrl = json("verification_uri")
        Dim deviceCode As String: deviceCode = json("device_code")
        Dim interval As Long: interval = json("interval")
        
        ' Mostrar instrucciones al usuario
        MsgBox "Por favor, visita: " & verificationUrl & vbCrLf & _
               "Ingresa el código: " & userCode & vbCrLf & vbCrLf & _
               "Haz clic en Aceptar DESPUÉS de haber ingresado el código en el navegador.", vbInformation, "Autenticación Planner"
        
        ' Iniciar sondeo (polling) para obtener el token
        PollForToken deviceCode, interval
    Else
        MsgBox "Error al obtener el código de dispositivo: " & http.ResponseText, vbCritical
    End If
End Sub

Private Sub PollForToken(deviceCode As String, interval As Long)
    Dim http As Object
    Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
    
    Dim url As String: url = TOKEN_URL
    Dim body As String: body = "grant_type=urn:ietf:params:oauth:grant-type:device_code" & _
                               "&client_id=" & CLIENT_ID & _
                               "&device_code=" & deviceCode
    
    Dim success As Boolean: success = False
    Dim attempts As Integer: attempts = 0
    
    Do While Not success And attempts < 20 ' Máximo 20 intentos
        http.Open "POST", url, False
        http.SetRequestHeader "Content-Type", "application/x-www-form-urlencoded"
        http.Send body
        
        Dim json As Object
        Set json = JsonConverter.ParseJson(http.ResponseText)
        
        If http.Status = 200 Then
            SaveTokens json("access_token"), json("refresh_token"), json("expires_in")
            MsgBox "¡Autenticación exitosa!", vbInformation
            success = True
        ElseIf json("error") = "authorization_pending" Then
            ' Esperar el intervalo sugerido
            Sleep interval * 1000
            attempts = attempts + 1
        Else
            MsgBox "Error de autenticación: " & json("error_description"), vbCritical
            Exit Sub
        End If
    Loop
End Sub

''' <summary>
''' Intercambia el Refresh Token por un nuevo Access Token.
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

' Función auxiliar para esperar (Declare PtrSafe para 64 bits)
#If VBA7 Then
    Declare PtrSafe Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As LongPtr)
#Else
    Declare Sub Sleep Lib "kernel32" (ByVal dwMilliseconds As Long)
#End If
