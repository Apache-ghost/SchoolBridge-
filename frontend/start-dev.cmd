@echo off
cd /d "C:\Users\SOP\Documents\Distributed system\school\frontend"
echo Current directory: %cd%
echo Starting Vite from frontend directory...
npx vite --host 0.0.0.0
pause