@echo off
title %~n0 by Yoti
echo %~n0 by Yoti
for %%f in (*.inc) do (
	python3 convert_inc_bmp.py %%f
)
pause