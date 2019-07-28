@echo off
echo -------------------------------
rd /s /q "windows-target"
git pull
echo -------------------------------
echo Type in "Timecard Processor" when asked for the app name, and "Anton Zakharov" when asked for the author. 
echo Press enter when asked for the Mac Bundle Identifier.
echo -------------------------------
fbs startproject
copy main.py "src\main\python"
fbs freeze
fbs installer
mkdir "target\Timecard Processor\Installer (optional)"
move "target\Timecard ProcessorSetup.exe" "target\Timecard Processor\Installer (optional)\Timecard Processor Setup.exe"
mkdir "windows-target"
move "target\Timecard Processor" ".\windows-target\"
mkdir "windows-target\Timecard Processor\Source"
copy main.py "windows-target\Timecard Processor\Source"
rd /s /q target
rd /s /q src
echo -------------------------------
echo Done!
echo -------------------------------