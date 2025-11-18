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
            print(f"❌ ERROR: Cannot connect to MySQL → {err}")
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
    print("🔧 Initializing database...")

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
        print("✓ Database exists.")

    except mysql.connector.Error as err:
        print(f"❌ Could not create database: {err}")
        return

    db = get_db()
    if not db:
        print("❌ Could not connect to study_companion_db after creation.")
        return

    cursor = db.cursor()
    try:
        create_table_query = """
        CREATE TABLE IF NOT EXISTS subjects (
            id INT PRIMARY KEY AUTO_INCREMENT,
            subject_name VARCHAR(255) NOT NULL,
            subject_unit INT DEFAULT 0,
            chapter_name VARCHAR(500) NOT NULL,
            difficulty INT,
            deadline DATE,
            progress_pct INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_subject_chapter (subject_name, chapter_name)
        )
        """
        cursor.execute(create_table_query)
        db.commit()
        print("✓ Table created.")
    except mysql.connector.Error as err:
        print(f"❌ Table creation failed: {err}")
    finally:
        cursor.close()

def calculate_days_left(subjects):
    today = date.today()
    processed = []

    for sub in subjects:
        item = dict(sub)
        deadline = item['deadline']

        if isinstance(deadline, datetime):
            deadline = deadline.date()

        if deadline:
            item['days_left'] = (deadline - today).days
        else:
            item['days_left'] = None

        processed.append(item)
    return processed

@app.route('/')
def index():
    cursor = get_cursor()
    if not cursor:
        return "Database Connection Error. Check your MySQL server & config.", 500

    try:
        cursor.execute("""
            SELECT id, subject_name, chapter_name, difficulty, deadline, progress_pct, subject_unit
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

        active = calculate_days_left(active)

        return render_template("index.html",
                               subjects=active,
                               completed_subjects=completed)
    finally:
        cursor.close()


@app.route('/add_subject', methods=['POST'])
def add_subject():
    cursor = get_cursor()
    if not cursor:
        return redirect(url_for('index'))

    subject_name = request.form['syllabus_unit']
    subject_unit = int(request.form.get('unit_number', 0))
    chapter = request.form['name']
    sub_topic = request.form.get('sub_topic')
    difficulty = int(request.form['difficulty'])
    deadline = request.form['deadline']

    final_chapter = f"{chapter}: {sub_topic}" if sub_topic else chapter

    try:
        cursor.execute("""
            INSERT INTO subjects (subject_name, subject_unit, chapter_name, difficulty, deadline)
            VALUES (%s, %s, %s, %s, %s)
        """, (subject_name, subject_unit, final_chapter, difficulty, deadline))
        cursor.connection.commit()
    except mysql.connector.Error as err:
        print(f"❌ Insert failed: {err}")
    finally:
        cursor.close()

    return redirect(url_for('index'))


@app.route('/complete_subject', methods=['POST'])
def complete_subject():
    cursor = get_cursor()
    if not cursor:
        return redirect(url_for('index'))

    subject_id = request.form.get('subject_id')

    if subject_id:
        try:
            cursor.execute("UPDATE subjects SET progress_pct = 100 WHERE id = %s", (subject_id,))
            cursor.connection.commit()
        except mysql.connector.Error as err:
            print(f"❌ Update failed: {err}")

    cursor.close()
    return redirect(url_for('index'))


@app.route('/delete_subject', methods=['POST'])
def delete_subject():
    cursor = get_cursor()
    if not cursor:
        return redirect(url_for('index'))

    subject_id = request.form.get('subject_id')

    if subject_id:
        try:
            cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))
            cursor.connection.commit()
        except mysql.connector.Error as err:
            print(f"❌ Delete failed: {err}")

    cursor.close()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
