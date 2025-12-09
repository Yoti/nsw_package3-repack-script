@echo off
title %~n0 by Yoti
echo %~n0 by Yoti
for %%f in (boot_splash_screen_notext.inc, boot_splash_screen_text.inc) do (
	if exist %%f del /q %%f
	wget -q --show-progress https://raw.githubusercontent.com/Atmosphere-NX/Atmosphere/master/stratosphere/boot/source/%%f
)
pause