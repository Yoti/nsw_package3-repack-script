@echo off
title %~n0
for %%f in (boot_splash_kefir.inc) do (
	if exist %%f del /q %%f
	wget -q --show-progress https://raw.githubusercontent.com/rashevskyv/Kefirosphere/master/stratosphere/boot/source/%%f
)
pause