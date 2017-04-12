@echo off

set owswork=%~1
set dirstruct=%~2

for /F "usebackq tokens=1" %%A in (%dirstruct%) do (
	echo "%owswork%%%A"
	mkdir "%owswork%%%A"
)

exit /B 0
