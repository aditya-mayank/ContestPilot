Set WinScriptHost = CreateObject("WScript.Shell")
Dim cmd
cmd = Chr(34) & WScript.Arguments(0) & Chr(34)
If WScript.Arguments.Count > 1 Then
    Dim i
    For i = 1 To WScript.Arguments.Count - 1
        cmd = cmd & " " & WScript.Arguments(i)
    Next
End If
WinScriptHost.Run cmd, 0, False
