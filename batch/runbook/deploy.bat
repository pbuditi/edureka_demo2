@echo off

set _curdir=%~dp0

call %_curdir%\setvars.cmd

set _deploytools="%_curdir%\deployment\"
set _runbookexe="%_deploytools:"=%\script\runbook.cmd"
set _repository="%_curdir%"
set _runbook="%_repository:"=%\runbook\%_version:"=%\%_runbookname:"=%"
set _toutexe="%_deploytools:"=%\script\tout.cmd"
set _logfile="%_owswork:"=%\%_version:"=%_log.done"

rem call %_runbookexe% %_deploytools% %_repository% %_runbook% %_owsdb% %_owsusr% %_owspwd% %_owshome% %_owswork% %_version% 2>&1 | %_toutexe% %_logfile%
call %_runbookexe% %_deploytools% %_repository% %_runbook% %_owsdb% %_owspwd% %_owsapwd% %_owshome% %_owswork% %_version% >> %_logfile% 2>>&1
