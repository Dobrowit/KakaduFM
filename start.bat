@echo off&setlocal
:: start_kakadufm.bat

set app=kakadufm.pyw

:: ANSI colours.
:: Requires windows 1909 or newer
set _fBlack=[30m
set _bBlack=[40m
set _fRed=[31m
set _bRed=[41m
set _fGreen=[32m
set _bGreen=[42m
set _fYellow=[33m
set _bYellow=[43m
set _fBlue=[34m
set _bBlue=[44m
set _fMag=[35m
set _bMag=[45m
set _fCyan=[36m
set _bCyan=[46m
set _fLGray=[37m
set _bLGray=[47m
set _fDGray=[90m
set _bDGray=[100m
set _fBRed=[91m
set _bBRed=[101m
set _fBGreen=[92m
set _bBGreen=[102m
set _fBYellow=[93m
set _bBYellow=[103m
set _fBBlue=[94m
set _bBBlue=[104m
set _fBMag=[95m
set _bBMag=[105m
set _fBCyan=[96m
set _bBCyan=[106m
set _fBWhite=[97m
set _bBWhite=[107m
set _RESET=[0m

set /A test = 0
cls

echo %_RESET%%_bRed%%_fBWhite%
echo  PYTHON DETECTOR 
echo %_RESET%

::Testing Windows registry  
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Python" 2>NUL >NUL
if %ERRORLEVEL% EQU 0 (
	set /A test = %test%+1
	echo HKLM WOW6432Node\Python %_fGreen%detected%_RESET%
) else (
	echo HKLM WOW6432Node\Python %_fRed%no exist! %_RESET%
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore" 2>NUL >NUL
if %ERRORLEVEL% EQU 0 (
	set /A test = %test%+1
	echo HKLM PythonCore %_fGreen%detected%_RESET%
) else (
	echo HKLM PythonCore %_fRed%no exist! %_RESET%
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Classes\.pyw" 2>NUL >NUL
if %ERRORLEVEL% EQU 0 (
	set /A test = %test%+1
	echo HKLM .pyw class %_fGreen%detected%_RESET%
) else (
	echo HKLM .pyw class %_fRed%no exist! %_RESET%
)

reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Classes\.py" 2>NUL >NUL
if %ERRORLEVEL% EQU 0 (
	set /A test = %test%+1
	echo HKLM .py class %_fGreen%detected%_RESET%
) else (
	echo HKLM .py class %_fRed%no exist! %_RESET%
)

where python.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
	set /A test = %test%+1
	echo python.exe %_fGreen%detected%_RESET%
) else (
	echo python.exe %_fRed%no exist! %_RESET%
)

:: Check - is all test ok
if %test% EQU 5 (
	echo %_bRed%%_fBWhite% Succes! Python is installed! %_RESET%
	echo:
	python.exe -V
) else (
	echo %_RESET%%_bRed%%_fBWhite%
	echo  FIRST INSTALL PYTHON - https://python.org 
	echo %_RESET%
	echo:
	timeout 5 >NUL
	exit /B
)
echo:

:: If venv exist - start app else run tests and make venv
if exist modules\ (
	call modules\Scripts\activate.bat
	start modules\Scripts\pythonw.exe %app%
) else (

:: Create venv and download requirements
echo Create venv...
python -m venv modules
echo Upgrade PIP and install requirements...
if exist requirements.txt (
	call modules\Scripts\activate.bat
	modules\Scripts\python.exe -m pip install --upgrade pip
	pip install -r requirements.txt
) else (
	echo:
	echo requirements.txt file not exist!
	exit /B
)
echo:

:: Finaly start app
echo Starting
start modules\Scripts\pythonw.exe %app%
timeout 5 >NUL
)
