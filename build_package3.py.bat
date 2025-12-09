@echo off
title %~n0 by Yoti
echo %~n0 by Yoti
if not exist build_package3.py (
	wget -q --show-progress https://raw.githubusercontent.com/Atmosphere-NX/Atmosphere/refs/heads/master/fusee/build_package3.py
)