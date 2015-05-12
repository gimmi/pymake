@ECHO OFF
SETLOCAL
"%~dp0tools\NuGet.exe" install IronPython.Interpreter -Version 2.7.4 -OutputDirectory "%~dp0tools" -NonInteractive -Verbosity quiet -ExcludeVersion
SET IRONPYTHON_EXE=ipy64.exe
REM http://blogs.msdn.com/b/david.wang/archive/2006/03/26/howto-detect-process-bitness.aspx
IF "%PROCESSOR_ARCHITECTURE%" == "x86" (
    IF NOT DEFINED PROCESSOR_ARCHITEW6432 (
        SET IRONPYTHON_EXE=ipy.exe
    )
)
"%~dp0tools\IronPython.Interpreter\tools\%IRONPYTHON_EXE%" -tt "%~dp0tools\make.py" "%~dp0makefile.py" %*
