REM filename is in the 1st arg
REM https://stackoverflow.com/questions/3942265/errorlevel-in-a-for-loop-windows-batch
set enabledelayedexpansion

for /L %%a in (1, 1, 1000) do (
        py run_purge_job_main.py
        if not errorlevel 0 (goto stopme)
)

:stopme