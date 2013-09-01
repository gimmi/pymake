@NuGet.exe install IronPython.Interpreter -Version 2.7.3 -OutputDirectory "%~dp0..\tools" -NonInteractive -Verbosity quiet -ExcludeVersion
@"%~dp0..\tools\IronPython.Interpreter\tools\ipy.exe" -tt "%~dp0..\make.py" "%~dp0makefile.py" %*
