Attribute VB_Name = "ModConfig"
Option Explicit

' --- Configuración de Azure / MS Graph ---
' Para cuentas personales, puedes usar una App Registration genérica o crear la tuya en el portal de Azure.
' IMPORTANTE: Reemplaza "YOUR_CLIENT_ID" con tu Client ID real.
Public Const CLIENT_ID As String = "1844799e-1ce4-4d2d-9c40-3beff517f243"
Public Const TENANT_ID As String = "common" ' "common" para cuentas personales y corporativas
Public Const SCOPES As String = "Tasks.ReadWrite User.Read openid profile offline_access"

' --- Endpoints ---
Public Const DEVICE_CODE_URL As String = "https://login.microsoftonline.com/" & TENANT_ID & "/oauth2/v2.0/devicecode"
Public Const TOKEN_URL As String = "https://login.microsoftonline.com/" & TENANT_ID & "/oauth2/v2.0/token"
Public Const GRAPH_API_BASE As String = "https://graph.microsoft.com/v1.0"

' --- Hojas de Excel ---
Public Const SHEET_TASKS As String = "Tareas"
Public Const SHEET_CONFIG As String = "Config"

' --- Variables Globales ---
Public AccessToken As String
Public RefreshToken As String
Public TokenExpiry As Date

''' <summary>
''' Guarda el token en la hoja de configuración (oculta opcionalmente)
''' </summary>
Public Sub SaveTokens(ByVal accToken As String, ByVal refToken As String, ByVal expiresIn As Long)
    Dim ws As Worksheet
    Set ws = GetOrCreateSheet(SHEET_CONFIG)
    
    ws.Cells(1, 1).Value = "AccessToken"
    ws.Cells(1, 2).Value = accToken
    ws.Cells(2, 1).Value = "RefreshToken"
    ws.Cells(2, 2).Value = refToken
    ws.Cells(3, 1).Value = "ExpiryDate"
    ws.Cells(3, 2).Value = DateAdd("s", expiresIn, Now)
    
    AccessToken = accToken
    RefreshToken = refToken
    TokenExpiry = ws.Cells(3, 2).Value
End Sub

''' <summary>
''' Carga los tokens desde la hoja de configuración
''' </summary>
Public Sub LoadTokens()
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Sheets(SHEET_CONFIG)
    If Not ws Is Nothing Then
        AccessToken = ws.Cells(1, 2).Value
        RefreshToken = ws.Cells(2, 2).Value
        TokenExpiry = ws.Cells(3, 2).Value
    End If
    On Error GoTo 0
End Sub

Private Function GetOrCreateSheet(sheetName As String) As Worksheet
    On Error Resume Next
    Set GetOrCreateSheet = ThisWorkbook.Sheets(sheetName)
    If GetOrCreateSheet Is Nothing Then
        Set GetOrCreateSheet = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        GetOrCreateSheet.Name = sheetName
    End If
    On Error GoTo 0
End Function
