@echo off
setlocal enabledelayedexpansion

REM Default logger settings
set LOGGER_FORMAT=TEXT
set LOGGER_LEVEL=INFO

set "BASEPATH=%~dp0"
set "ENV_DIR=%BASEPATH%"

REM Remove the trailing backslash from ENV_DIR
if "%ENV_DIR:~-1%"=="\" set "ENV_DIR=%ENV_DIR:~0,-1%"

set "args=%*"
set "scripts="converter-frontend.bat" "tiling-advisor.bat" "converter-backend.bat" "converter-fm2lm.bat" "converter-packer.bat" "converter-main.bat""

REM Parse command line arguments for logger settings
call :parseArgs %*

REM Check for the existence of scripts
call :checkScripts

call %ENV_DIR%\converter-main.bat --env-dir %ENV_DIR% %args%
goto :eof

:parseArgs
    :parseLoop
    if "%~1"=="" goto :eof
    set "KEY=%~1"
    shift
    if /i "%KEY%"=="--logger-format" (
        set "LOGGER_FORMAT=%~1"
        shift
    ) else if /i "%KEY%"=="--logger-level" (
        set "LOGGER_LEVEL=%~1"
        shift
    )
    goto :parseLoop

:logWarning
    REM warning msg will be appear in the following levels: warn, debug, trace, or info
    setlocal
    set "message=%~1"
    set "lc_logger_level=!LOGGER_LEVEL!"

    REM Compare and check if the level is among the acceptable ones
    if /i "%lc_logger_level%"=="warn" goto :logMessage
    if /i "%lc_logger_level%"=="debug" goto :logMessage
    if /i "%lc_logger_level%"=="trace" goto :logMessage
    if /i "%lc_logger_level%"=="info" goto :logMessage
    goto :eof

:logMessage
    REM Extract date components (YYYY-MM-DD)
    for /f "tokens=1-3 delims=/- " %%A in ("%date%") do (
        set "year=%%C"
        set "month=%%A"
        set "day=%%B"
    )

    REM Extract time components (HH:MM:SS,sss)
    for /f "tokens=1-4 delims=:., " %%A in ("%time%") do (
        set "hour=%%A"
        set "minute=%%B"
        set "seconds=%%C"
        set "milliseconds=%%D"
    )

    REM Format timestamp as: YYYY-MM-DD HH:MM:SS,sss
    set "TIMESTAMP=%year%-%month%-%day% %hour%:%minute%:%seconds%,%milliseconds%"
    set "lc_logger_format=!LOGGER_FORMAT!"

    if /i "%lc_logger_format%"=="json" (
         echo {"@timestamp":"%TIMESTAMP%","ecs.version":"1.2.0","log.level":"WARNING","message":"CODE: [SCRPT] %message%","process.thread.name":"main","log.logger":"sdspconv","component.name":"sdspconv","component.type":"sdspconv-script","context":"","message.code":"SCRPT"}
    ) else (
        echo %TIMESTAMP% WARNING : %message%
    )
    endlocal
    exit /b

    goto :eof

:checkScripts
    for %%s in (%scripts%) do (
        if not exist "%ENV_DIR%\%%s" (
            call :logWarning "Script '%%s' does not exist in path: '%ENV_DIR%\%%s'."
        )
    )
    goto :eof
