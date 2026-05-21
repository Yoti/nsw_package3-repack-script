@echo off
title %~n0 by Yoti
echo %~n0 by Yoti
pyinstaller --onefile --console --clean --workpath "%cd%\psc_repack_package3_tmp" --distpath "%cd%" --specpath "C:/Dev/Projects/NintendoSwitch/package3-repack-script" "%cd%\repack_package3.py"
if not exist repack_package3.exe (
	pause
)
for /d %%d in (atm kef psc_repack_package3_tmp) do (
	rmdir /s /q %%d
)
for %%f in (pk31_bpatcher.exe repack_package3.spec) do (
	del /q %%f
)
if exist repack_package3.exe (
	ren repack_package3.exe pk31_bpatcher.exe
)
