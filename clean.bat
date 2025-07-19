@echo off
for /d %%d in (atm, atmo, kef, kefir, package3_out) do (
	rd /s /q %%d
)
for %%f in (package3) do (
	del /q %%f
)
