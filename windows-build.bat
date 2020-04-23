@echo off
echo -------------------------------
git pull
echo -------------------------------
fbs freeze
fbs installer
mkdir "target\Timecard Processor\Source"
copy "src\main\python\main.py" "target\Timecard Processor\Source"
echo -------------------------------
echo Done!
echo -------------------------------