@echo off

set deploytools="%~1"
set repository="%~2"
set runbook="%~3"
set owsdb=%~4
set owsusr=ows
set owspwd=%~5
set owsausr=ows_a
set owsapwd=%~6
set owshome="%~7"
set owswork="%~8"
set version=%~9

set runbooktool="%deploytools:"=%\script\runbook1.cmd"
set runbooktoolextra="%deploytools:"=%\script\runbook_extra.cmd"
set err=-1
set errinvalidaction=-2

rem set owsausr=OWS_A
rem set owsapwd=%~4
rem set schinstance=%~7
rem set testresults="%~8"
rem set python="%~9"
rem for /L %%n in (1,1,9) do ( shift )
rem set dwhdb=%~2
rem set dwhusr=DWH
rem set dwhpwd=%~3

call %runbooktool% %runbook%
if %errorlevel% neq 0 (
	echo # Error: RUNBOOK %runbook% failed
	exit /B -1
) else (
	echo # RUNBOOK %runbook% finished
	exit /B 0
)
