Set WinScriptHost = CreateObject("WScript.Shell")
Dim cmd
cmd = Chr(34) & WScript.Arguments(0) & Chr(34)
If WScript.Arguments.Count > 1 Then
    Dim i
    For i = 1 To WScript.Arguments.Count - 1
        cmd = cmd & " " & WScript.Arguments(i)
    Next
End If

' Add cmd.exe /c so it properly resolves the batch file and doesn't crash on paths!
WinScriptHost.Run "cmd.exe /c " & Chr(34) & cmd & Chr(34), 0, False
