\
@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
if not exist ".env" copy .env.example .env
python db_init.py
python app.py
