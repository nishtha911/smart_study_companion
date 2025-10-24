from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)

DATABASE = 'study_companion.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row 
    return g.db

def close_connection(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()
        print("Database initialized successfully.")

@app.route('/')
def index():
    db = get_db()
    subjects = db.execute('SELECT id, name, difficulty, deadline FROM subjects').fetchall()
    
    return render_template('index.html', subjects=subjects)

if __name__ == '__main__':
    app.teardown_appcontext(close_connection) 
    
    with app.app_context():
        init_db()
        
    app.run(debug=True)