@echo off & title

for %%a in (*.m4a) do (
 "D:\Program Files\ffmpeg-2022-04-07-git-607ecc27ed-essentials_build\bin\ffmpeg.exe" -i "%%~sa" -y -acodec libmp3lame -aq 0 "%%~na.mp3"
)

pause