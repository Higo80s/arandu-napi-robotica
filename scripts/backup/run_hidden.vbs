' VBScript to launch Python script without showing console window
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """" & WScript.Arguments(0) & """ """ & WScript.Arguments(1) & """", 0, False
Set WshShell = Nothing
