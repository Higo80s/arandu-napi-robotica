Set WshShell = CreateObject("WScript.Shell")
' Run the launcher batch file invisibly (0 means hidden window)
WshShell.Run chr(34) & "c:\Users\higosantos\Documents\gestao_editais\arandu-napi-robotica\launch_with_postgres.bat" & Chr(34), 0
Set WshShell = Nothing
