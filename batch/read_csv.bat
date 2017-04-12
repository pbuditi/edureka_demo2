@ECHO OFF
setlocal EnableDelayedExpansion

:parse
IF "%~1"=="" GOTO endparse
IF "%~2"=="" GOTO endparse
IF "%~3"=="" GOTO endparse
IF "%~4"=="" GOTO endparse
IF "%~5"=="" GOTO endparse


set connectionString=%1
set owsa_pwd=%2
set fi_name=%3
set account_type=%4
set new_pwd=%5
set userfile="%fi_name%_%account_type%_users.csv"

for /F "tokens=1-4* delims=," %%A in ('type %userfile%') do (
    echo creating user %%B
	sqlplus -S OWS_A/%owsa_pwd%@%connectionString% @create_user.sql "%%A" "%%B" "%new_pwd%" "%%C" "%%D"

    REM ${bamboo.ssp_bat} "connect=ows/"${bamboo.OwsPassword}"@"${bamboo.ConnectionString}" "  "%%A"
)

if %errorlevel% neq 0 (
	echo # Error: User creation failed
	exit /B -1
) else (
	echo # Done: user creation finished
	exit /B 0
)

:endparse
ECHO Script execution failed
