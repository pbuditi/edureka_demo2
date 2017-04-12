@echo off

setlocal EnableDelayedExpansion

set outfile=%1

for /F "tokens=1* delims=]" %%A in ('find /N /V ""') do (
	> CON echo.%%B
	>> %outfile% echo.!date! !time! %%B
)
