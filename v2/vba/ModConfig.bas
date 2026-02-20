Attribute VB_Name = "ModConfig"
Option Explicit

' ╔══════════════════════════════════════════════════════════════╗
' ║  CRUD-Planner — Configuración Centralizada (Definitiva)    ║
' ║  Fusión de V1 (constantes VBA) + V2 (Python bridge)        ║
' ╚══════════════════════════════════════════════════════════════╝

' --- Azure / MS Graph ---
Public Const CLIENT_ID As String = "1844799e-1ce4-4d2d-9c40-3beff517f243"
Public Const TENANT_ID As String = "common"
Public Const SCOPES As String = "Tasks.ReadWrite User.Read openid profile offline_access"

' --- Endpoints ---
Public Const DEVICE_CODE_URL As String = "https://login.microsoftonline.com/" & TENANT_ID & "/oauth2/v2.0/devicecode"
Public Const TOKEN_URL As String = "https://login.microsoftonline.com/" & TENANT_ID & "/oauth2/v2.0/token"
Public Const GRAPH_API_BASE As String = "https://graph.microsoft.com/v1.0"

' --- Hojas de Excel ---
Public Const SHEET_TASKS As String = "Tareas"
Public Const SHEET_CONFIG As String = "Config"

' --- Variables Globales (Tokens en memoria) ---
Public AccessToken As String
Public RefreshToken As String
Public TokenExpiry As Date

''' <summary>
''' Guarda los tokens en la hoja Config (persistencia entre sesiones).
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
''' Carga los tokens desde la hoja Config.
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

''' <summary>
''' Verifica si Python + xlwings están disponibles.
''' </summary>
Public Function HasPython() As Boolean
    On Error GoTo NoPython
    Dim testResult As String
    testResult = Application.Run("RunPython", "print('ok')")
    HasPython = True
    Exit Function
NoPython:
    HasPython = False
End Function

Private Function GetOrCreateSheet(sheetName As String) As Worksheet
    On Error Resume Next
    Set GetOrCreateSheet = ThisWorkbook.Sheets(sheetName)
    If GetOrCreateSheet Is Nothing Then
        Set GetOrCreateSheet = ThisWorkbook.Sheets.Add(After:=ThisWorkbook.Sheets(ThisWorkbook.Sheets.Count))
        GetOrCreateSheet.Name = sheetName
    End If
    On Error GoTo 0
End Function
