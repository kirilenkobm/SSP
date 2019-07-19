:: like Makefile but for Windows
:: was not tested yet! (19.07.2019)
SET "CL_PARAMS=/O2 /Iall /Iyour /Iincludes /D_USRDLL /DLL"
CALL "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\bin\amd64\vcvars64.bat
CALL cl %CL_PARAMS% src\SSP_lib.c /LD /Febin\SSP_lib.dll /link /DEF:src\SSP_lib.def
DEL ".\SSP_lib.obj" /f /q
