@echo off
call venv\Scripts\activate

flask db init
flask db migrate -m "Initial migration."
flask db upgrade

start flask run --host=0.0.0.0

start http://127.0.0.1:5000
