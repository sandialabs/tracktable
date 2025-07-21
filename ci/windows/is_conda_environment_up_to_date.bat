@echo off
setlocal EnableDelayedExpansion

REM Check if the argument is provided
if "%~1"=="" (
    echo Usage: %0 ^<YML_FILENAME^>
    exit /b 1
)

set YML_FILENAME=%~1


REM Extract the Conda environment name from the YML file
for /f "tokens=2" %%a in ('findstr /r "^name: " "%YML_FILENAME%"') do (
    set CONDA_ENV_NAME=%%a
)

echo Checking to see if Conda environment %CONDA_ENV_NAME% is up to date.

REM Get the path of the Conda environment by parsing the output of 'conda env list'
for /f "tokens=1,3 delims= " %%a in ('conda env list ^| findstr /i "%CONDA_ENV_NAME%"') do (

    if "%%b" == "*" (
        set CONDA_ENV_PATH=%%c
    ) else (
        set CONDA_ENV_PATH=%%b
    )
)

REM Check if the Conda environment path was found
if not defined CONDA_ENV_PATH (
    echo Conda environment "%CONDA_ENV_NAME%" does not exist.
    exit /b 1
)

set CONDA_HISTORY_FILE=%CONDA_ENV_PATH%\conda-meta\history

REM Check if the history file exists
if not exist "%CONDA_HISTORY_FILE%" (
    echo No history file found for Conda environment "%CONDA_ENV_NAME%".
    echo Expected path: %CONDA_HISTORY_FILE%
    echo Conda environment path: %CONDA_ENV_PATH%
    exit /b 1
)

REM Get the last modification time of the Conda environment from the history file
for /f "tokens=2,3 delims= " %%i in ('findstr /r "^==> " "%CONDA_HISTORY_FILE%" ^| C:\Windows\System32\sort /R') do (
    set LAST_CONDA_MOD_TIME=%%i %%j
    goto :found_conda_time
)


:found_conda_time

if not defined LAST_CONDA_MOD_TIME (
    echo No modification history found for Conda environment "%CONDA_ENV_NAME%".
    exit /b 1
)

REM Convert to Unix timestamp using PowerShell
for /f "UseBackQ" %%u in (`powershell -command "[int][double]::Parse((Get-Date '%LAST_CONDA_MOD_TIME%' -UFormat %%s))"`) do (
    set LAST_CONDA_UNIX_TIME=%%u
)

REM Get the last commit timestamp for the specified YML file
for /f "tokens=* UseBackQ" %%j in (`git log -1 --format^="%%at" "%YML_FILENAME%"`) do (
    set LAST_YML_COMMIT_TIME=%%j
    goto :found_yml_time
)

:found_yml_time
if not defined LAST_YML_COMMIT_TIME (
    echo No commits found for "%YML_FILENAME%". Make sure the file is tracked by Git.
    exit /b 1
)

REM Compare timestamps
if %LAST_YML_COMMIT_TIME% GTR %LAST_CONDA_UNIX_TIME% (
    echo Error: "%YML_FILENAME%" is newer than the last change to Conda environment "%CONDA_ENV_NAME%"  Please update the Conda environment on the runner.
    exit /b 1
) else (
    echo Success: Environment definition file has not been modified since Conda environment was last updated.
    exit /b 0
)

endlocal