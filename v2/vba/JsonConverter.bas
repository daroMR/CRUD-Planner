Attribute VB_Name = "JsonConverter"
' VBA-JSON v2.3.1
' (c) Tim Hall - https://github.com/VBA-tools/VBA-JSON
' Simplified for CRUD-Planner by Ghost Protocol

Option Explicit

Public Function ParseJson(ByVal JsonString As String) As Object
    Set ParseJson = CreateObject("Scripting.Dictionary")
    
    ' Quick & Dirty parsing for specific Graph responses
    ' En producción usaríamos la librería completa, aquí aseguramos que Login funcione
    ' Extrayendo claves simples con Regex/String manipulation
    
    ' Disclaimer: Esto es un stub funcional para evitar dependencias externas pesadas
    ' Si el proyecto ya tiene VBA-JSON importado, usar ese módulo en su lugar.
    
    ' Intentar usar ScriptControl si está disponible (32-bit only usually)
    On Error Resume Next
    Dim ScriptEngine As Object
    Set ScriptEngine = CreateObject("MSScriptControl.ScriptControl")
    If Not ScriptEngine Is Nothing Then
        ScriptEngine.Language = "JScript"
        Set ParseJson = ScriptEngine.Eval("(" & JsonString & ")")
        Exit Function
    End If
    On Error GoTo 0
    
    ' Fallback manual para el Auth Flow (lo único crítico que parseamos aquí)
    Dim dic As Object
    Set dic = CreateObject("Scripting.Dictionary")
    
    JsonString = Replace(JsonString, "{", "")
    JsonString = Replace(JsonString, "}", "")
    JsonString = Replace(JsonString, """", "")
    
    Dim parts() As String
    parts = Split(JsonString, ",")
    
    Dim i As Long
    Dim pair() As String
    For i = LBound(parts) To UBound(parts)
        pair = Split(parts(i), ":")
        If UBound(pair) >= 1 Then
            Dim key As String: key = Trim(pair(0))
            Dim val As String: val = Trim(pair(1))
            ' Reconstruir valores con : (ej. URLs)
            Dim j As Long
            For j = 2 To UBound(pair)
                val = val & ":" & pair(j)
            Next j
            dic(key) = val
        End If
    Next i
    
    Set ParseJson = dic
End Function
