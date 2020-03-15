@echo off
echo -------------------------------
git pull
echo -------------------------------
echo Type in "Timecard Processor" when asked for the app name, and "Anton Zakharov" when asked for the author. 
echo Press enter when asked for the Mac Bundle Identifier.
echo -------------------------------
fbs freeze
fbs installer
mkdir "target\Timecard Processor\Installer (optional)"
move "target\Timecard ProcessorSetup.exe" "target\Timecard Processor\Installer (optional)\Timecard Processor Setup.exe"
mkdir "target\Timecard Processor\Source"
copy "src\main\python\main.py" "target\Timecard Processor\Source"
echo -------------------------------
echo Done!
echo -------------------------------