@echo off
set SCRIPT_NAME=main.pyw

:: 1. Cicha instalacja bibliotek (tylko jeśli ich brakuje)
echo Sprawdzanie bibliotek...
python -m pip install pystray Pillow --quiet

:: 2. Uruchomienie skryptu w trybie "Windowless" (bez okna konsoli)
:: start "" pozwala na natychmiastowe zamkniecie tego okna .bat
start "" pythonw "%~dp0%SCRIPT_NAME%"

:: 3. Zamkniecie konsoli
exit