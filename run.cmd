@ECHO OFF

IF EXIST "%~dp0tools\cache" GOTO DOWNLOADED
"%~dp0tools\NuGet.exe" install IronPython.Interpreter -Version 2.7.3 -Source https://nuget.org/api/v2/ -OutputDirectory "%~dp0tools\cache" -NonInteractive -Verbosity quiet -ExcludeVersion
"%~dp0tools\NuGet.exe" install SqlMigrator -Version 0.9.1 -Source https://nuget.org/api/v2/ -OutputDirectory "%~dp0tools\cache" -NonInteractive -Verbosity quiet -ExcludeVersion

:DOWNLOADED
"%~dp0tools\cache\IronPython.Interpreter\tools\ipy.exe" "%~dp0prova.py" %*
