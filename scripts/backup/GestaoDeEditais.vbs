Set WshShell = CreateObject("WScript.Shell")
strPath = WshShell.CurrentDirectory
' Executa run_app.bat de forma oculta (0)
' Aspas extras sao para garantir caminhos com espaco
WshShell.Run chr(34) & strPath & "\run_app.bat" & chr(34), 0
Set WshShell = Nothing
