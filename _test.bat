:: todo for Windows also
CALL win_make.bat
:: quit if cannot build
:: todo: some verbose
if %ERRORLEVEL% != 0 (EXIT \b 1)
python .\SSP.py test_input\1.txt 10 \s 4
