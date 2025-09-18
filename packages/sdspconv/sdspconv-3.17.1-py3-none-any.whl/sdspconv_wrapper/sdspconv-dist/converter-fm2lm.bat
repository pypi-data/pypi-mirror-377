@echo off
setlocal enabledelayedexpansion
REM Auto-generated file: this file originated in template file "template-script.bat" and changed in Pack.kt by sa
if "%ENV_DIR%"=="" (
    set "BASEPATH=%~dp0"
    set "ENV_DIR=!BASEPATH!"
)
set "CPText="
REM Read file contents
for /f "Tokens=* Delims=" %%x in (%ENV_DIR%\converter-fm2lm\jib-classpath-file) do set CPText=!CPText!%%x

REM replace / with \
set "CP=!CPText:/=\!"
REM replace converter-fm2lm\libs to libs
set "CP=!CP:converter-fm2lm\libs=libs!"
REM replace : with ;ENV_DIR
set "CP=!CP::=;%ENV_DIR%!"
REM append ENV_DIR at the start of text
set "CP=%ENV_DIR%%CP%"

set /p JIB_MC=<%ENV_DIR%\converter-fm2lm\jib-main-class-file

java -Xss32m %JVM_PARAMS% -cp "%CP%" %JIB_MC% %*
