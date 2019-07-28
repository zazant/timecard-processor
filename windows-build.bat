@echo off
rd /s /q "windows-target"
git pull
fbs startproject
copy main.py "src\main\python"
fbs freeze
fbs installer
mkdir "target\Timecard Processor\Installer (optional)"
move "target\Timecard ProcessorSetup.exe" "target\Timecard Processor\Installer (optional)\Timecard Processor Setup.exe"
move "target\Timecard Processor" ".\windows-target"
rd /s /q target
rd /s /q src