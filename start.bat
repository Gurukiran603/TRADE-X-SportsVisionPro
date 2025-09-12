@echo off
echo Starting SportsVision Pro Application...
echo.

echo Starting Backend Server...
cd backend
start cmd /k "python main.py"
cd ..

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo Starting Frontend Server...
cd frontend
start cmd /k "npm start"
cd ..

echo.
echo Application is starting up!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
