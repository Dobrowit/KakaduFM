@echo off&setlocal
:: start_kakadufm.bat

set app=kakadufm.pyw
set python_url=https://www.python.org/ftp/python/3.10.6/python-3.10.6-amd64.exe
set python_file=python-3.10.6-amd64.exe

:: If venv exist - start app else run tests and make venv
if exist venv\ (
echo Delete venv...
rd /S /Q venv
) else (

:: Create venv and download requirements
echo Create venv...
python -m venv venv
echo Upgrade PIP and install requirements...
venv\Scripts\python.exe -m pip install --upgrade pip
echo:
)

:: Finaly start app
::echo Starting
::start venv\Scripts\pythonw.exe %app%
timeout 5 >NUL
