CALL SET PYTTHONPATH=.
CALL .venv\Scripts\activate.bat
CALL start chrome "http://127.0.0.1:5000/"
cmd /k python app.py
