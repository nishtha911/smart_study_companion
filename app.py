from flask import Flask, render_template, g, request, redirect, url_for
import mysql.connector
from datetime import date, datetime 

app = Flask(__name__)

MYSQL_CONFIG = {
    'user': 'root', 
    'password': 'root', 
    'host': '127.0.0.1',
    'database': 'study_companion_db'
}

def get_db():
    if 'db_conn' not in g:
        try:
            g.db_conn = mysql.connector.connect(**MYSQL_CONFIG)
            g.db_conn.autocommit = True
        except mysql.connector.Error as err:
            print(f"ERROR: Cannot connect to MySQL: {err}")
            g.db_conn = None 
    return g.db_conn

def get_cursor():
    db = get_db()
    if db:
        return db.cursor(dictionary=True, buffered=True)
    return None

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db_conn', None)
    if db and db.is_connected():
        db.close()

def init_db():
    print("Initializing database...")

    try:
        conn = mysql.connector.connect(
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            host=MYSQL_CONFIG['host']
        )
        cursor = conn.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS study_companion_db;")
        conn.commit()

        cursor.close()
        conn.close()
        print("Database exists.")

    except mysql.connector.Error as err:
        print(f"Could not create database: {err}")
        return

    db = get_db()
    if not db:
        print("Could not connect to study_companion_db after creation.")
        return

    cursor = db.cursor()
    try:
        print("Table setup complete.")
    except mysql.connector.Error as err:
        print(f"Table creation failed: {err}")
    finally:
        cursor.close()

def calculate_days_left(subjects): 
    today = date.today()
    processed = []

    for sub in subjects: #converted the format from yyyy-mm-dd to dd-mm-yyyy
        item = dict(sub)
        
        if 'deadline' in item: 
            date_raw = item['deadline']
            date_key = 'formatted_deadline'
        elif 'exam_date' in item:
            date_raw = item['exam_date']
            date_key = 'formatted_deadline' 
        else:
            date_raw = None
            date_key = 'formatted_deadline'


        if isinstance(date_raw, datetime):
            date_obj = date_raw.date()
        elif date_raw:
            date_obj = datetime.strptime(str(date_raw), '%Y-%m-%d').date()
        else:
            date_obj = None

        if date_obj:
            item['days_left'] = (date_obj - today).days
            item[date_key] = date_obj.strftime('%d-%m-%Y') 
        else:
            item['days_left'] = None
            item[date_key] = 'N/A'

        processed.append(item)
    return processed

@app.route('/')
def index():
    cursor = get_cursor()
    if not cursor:
        return "Database Connection Error. Check your MySQL server & config.", 500

    try:
        cursor.execute("""
            SELECT id, subject_name, chapter_name, topic_name, difficulty, deadline, progress_pct, subject_unit
            FROM subjects
            WHERE progress_pct < 100
            ORDER BY deadline ASC;
        """)
        active = cursor.fetchall()

        cursor.execute("""
            SELECT id, subject_name, chapter_name, subject_unit, deadline
            FROM subjects
            WHERE progress_pct = 100
            ORDER BY deadline DESC;
        """)
        completed = cursor.fetchall()
        
        cursor.execute("""
            SELECT subject_name, exam_type, exam_date 
            FROM exams 
            ORDER BY exam_date ASC;
        """)
        exams = cursor.fetchall()

        active = calculate_days_left(active)
        completed_formatted = calculate_days_left(completed)
        exams_formatted = calculate_days_left(exams)


        return render_template("index.html",
                               subjects=active,
                               completed_subjects=completed_formatted,
                               exams=exams_formatted) 
    finally:
        cursor.close()


@app.route('/add_subject', methods=['POST'])
def add_subject():
    cursor = get_cursor()
    db = get_db() 
    if not cursor or not db:
        return redirect(url_for('index'))

    subject_name = request.form['syllabus_unit']
    subject_unit = int(request.form.get('unit_number', 0))
    chapter_name = request.form['name']
    topic_name = request.form.get('sub_topic')
    difficulty = int(request.form['difficulty'])
    deadline = request.form['deadline'] 

    final_chapter = f"{chapter_name}: {topic_name}" if topic_name else chapter_name

    try:
        cursor.execute("""
            INSERT INTO subjects (subject_name, subject_unit, chapter_name, topic_name, difficulty, deadline)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (subject_name, subject_unit, chapter_name, topic_name, difficulty, deadline))
        db.commit() 
    except mysql.connector.Error as err:
        print(f"Insert failed: {err}")
    finally:
        cursor.close()

    return redirect(url_for('index'))


@app.route('/complete_subject', methods=['POST'])
def complete_subject():
    cursor = get_cursor()
    db = get_db() 
    if not cursor or not db:
        return redirect(url_for('index'))

    subject_id = request.form.get('subject_id')

    if subject_id:
        try:
            cursor.execute("UPDATE subjects SET progress_pct = 100 WHERE id = %s", (subject_id,))
            db.commit() 
        except mysql.connector.Error as err:
            print(f"Update failed: {err}")

    cursor.close()
    return redirect(url_for('index'))


@app.route('/delete_subject', methods=['POST'])
def delete_subject():
    cursor = get_cursor()
    db = get_db() 
    if not cursor or not db:
        return redirect(url_for('index'))

    subject_id = request.form.get('subject_id')

    if subject_id:
        try:
            cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))
            db.commit() 
        except mysql.connector.Error as err:
            print(f"Delete failed: {err}")

    cursor.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)