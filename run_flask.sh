source venv/bin/activate

pip install Flask Flask-WTF Flask-Bcrypt Flask-Login Flask-SQLAlchemy Flask-Migrate email-validator werkzeug

flask db init
flask db migrate -m "Initial migration."
flask db upgrade

flask run --host=0.0.0.0 &

xdg-open http://127.0.0.1:5000
