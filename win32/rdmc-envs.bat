@echo off

SET ILORESTDIR=%~dp0

:: remove trailing slash
IF %ILORESTDIR:~-1%==\ SET ILORESTDIR=%ILORESTDIR:~0,-1%


SET PATH=%ILORESTDIR%;%PATH%

echo.
echo "ilorest command added to your path"
echo.

echo "Type ilorest --help for usage"

echo.


GOTO END


:ERROR_HPRMCDIR_NOT_FOUND
    echo "ERROR: Unable to locate ilorest directory, please re-install to set the path manually"
    GOTO END

:END

