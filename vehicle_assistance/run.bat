@echo off
echo Installing requirements...
python -m pip install -r requirements.txt

echo Starting app...
python app.py

pause