@echo off
title %~n0
for %%f in (*.inc) do (
	python3 convert_inc_bmp.py %%f
)
pause