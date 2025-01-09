REM @echo off


echo test
plover_console -s plover_plugins install "C:\Users\msaw\AppData\Local\plover\plover\plugins\win\Python39\site-packages\plover_current_time_loca-1.0.2"

REM python -m pip install "git+https://github.com/merlinsaw/plover-current-time_de_DE.git@main"

REM python -m pip install ./plover_current_time_loca-1.0.2
REM pause
start cmd.exe /k C:\Users\msaw\AppData\Local\plover\plover\msaw\restart_plover.bat
