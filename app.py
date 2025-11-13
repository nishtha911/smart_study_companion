from flask import Flask, render_template, g, request, redirect, url_for
import sqlite3
from datetime import date, datetime 

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

def calculate_days_left(raw_subjects):
    """Helper function to calculate days left and convert rows to dicts."""
    processed_subjects = []
    today = date.today()

    for row in raw_subjects:
        subject = dict(row)
        deadline_raw = subject['deadline']
        
        deadline_date = None
        if isinstance(deadline_raw, str):
            try:
                deadline_date = datetime.strptime(deadline_raw, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            deadline_date = deadline_raw
            
        if deadline_date:
            time_difference = deadline_date - today
            subject['days_left'] = time_difference.days
        else:
            subject['days_left'] = 'N/A (Error)'
        
        processed_subjects.append(subject)
    return processed_subjects

@app.route('/')
def index():
    db = get_db()
    
    active_subjects_raw = db.execute(
        'SELECT id, name, difficulty, deadline, progress_pct, syllabus_unit FROM subjects WHERE progress_pct < 100 ORDER BY deadline ASC'
    ).fetchall()
    
    completed_subjects_raw = db.execute(
        'SELECT id, name, syllabus_unit, deadline FROM subjects WHERE progress_pct = 100 ORDER BY deadline DESC'
    ).fetchall()

    active_subjects = calculate_days_left(active_subjects_raw)
    
    return render_template('index.html', 
                           subjects=active_subjects, 
                           completed_subjects=completed_subjects_raw) 

@app.route('/add_subject', methods=['POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form['name']
        syllabus_unit = request.form['syllabus_unit']
        difficulty = int(request.form['difficulty']) 
        deadline = request.form['deadline']
        
        db = get_db()
        try:
            db.execute(
                'INSERT INTO subjects (name, syllabus_unit, difficulty, deadline) VALUES (?, ?, ?, ?)',
                (name, syllabus_unit, difficulty, deadline)
            )
            db.commit()
        except sqlite3.IntegrityError:
            pass
            
        return redirect(url_for('index'))

@app.route('/complete_subject', methods=['POST'])
def complete_subject():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        
        if subject_id:
            db = get_db()
            db.execute(
                'UPDATE subjects SET progress_pct = 100 WHERE id = ?',
                (subject_id,)
            )
            db.commit()
            
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.teardown_appcontext(close_connection) 
    
    with app.app_context():
        init_db()
        
    app.run(debug=True)