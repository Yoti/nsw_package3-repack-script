@echo off
title %~n0 by Yoti
echo %~n0 by Yoti
for /d %%d in (atm, atmo, kef, kefir, package3_out) do (
	rd /s /q %%d
)
for %%f in (package3, *-fix.zip) do (
	del /q %%f
)