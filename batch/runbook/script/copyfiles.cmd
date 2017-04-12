@echo off
setlocal EnableDelayedExpansion

set _source=%1
set _target=%2
set _recursively=%~3

if "%_recursively%" == "R" (
    xcopy %_source% %_target% /E /R /Y
) else (
    xcopy %_source% %_target% /R /Y
)
