@echo off

set _path="%~1"
set _recursively=%~2
rem Y - with subdirs, R - only files in subdirs

if "%_recursively%" == "Y" (
    rmdir /S /Q %_path%
) else if "%_recursively%" == "R" (
	del /F /Q /S %_path%
) else (
    del /F /Q %_path%
)

exit /B 0
