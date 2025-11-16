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
            print(f"Error connecting to MySQL: {err}")
            g.db_conn = None 
    return g.db_conn

def get_cursor():
    if 'db_conn' in g and g.db_conn:
        return g.db_conn.cursor(dictionary=True, buffered=True)
    return None

def close_connection(e=None):
    db = g.pop('db_conn', None)
    if db is not None and db.is_connected():
        db.close()

def init_db():
    db_conn = get_db()
    if not db_conn: return 
    
    cursor = db_conn.cursor()
    
    try:
        # Create database if not exists
        temp_config = MYSQL_CONFIG.copy()
        temp_db_name = temp_config.pop('database')
        temp_conn = mysql.connector.connect(**temp_config)
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {temp_db_name}")
        temp_cursor.close()
        temp_conn.close()
        
        # Reconnect to the specific database
        db_conn = get_db()
        cursor = db_conn.cursor()

        # Create table directly in Python (MySQL compatible syntax)
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
        
        # Insert sample data
        insert_query = """
        INSERT IGNORE INTO subjects 
        (subject_name, subject_unit, chapter_name, difficulty, deadline, progress_pct) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        sample_data = [
            ('DBMS', 3, 'Normalization', 3, '2024-12-15', 0),
            ('CN', 3, 'Network Layer', 4, '2024-12-10', 0),
            ('WT', 3, 'Java Servlets', 2, '2024-12-05', 100),
            ('AI', 3, 'Games', 5, '2024-12-20', 0)
        ]
        
        for data in sample_data:
            try:
                cursor.execute(insert_query, data)
            except mysql.connector.Error as err:
                if "Duplicate entry" not in str(err):
                    print(f"Error inserting sample data: {err}")
                    
        db_conn.commit()
        print("MySQL database and tables created successfully.")

    except mysql.connector.Error as err:
        print(f"Initial setup failed: {err}")
    finally:
        if cursor: cursor.close()


def calculate_days_left(raw_subjects):
    processed_subjects = []
    today = date.today()

    for row in raw_subjects:
        subject = dict(row)
        deadline_raw = subject['deadline']
        
        deadline_date = deadline_raw
            
        if isinstance(deadline_date, datetime):
            deadline_date = deadline_date.date()
        
        if deadline_date:
            time_difference = deadline_date - today
            subject['days_left'] = time_difference.days
        else:
            subject['days_left'] = 'N/A (Error)'
        
        processed_subjects.append(subject)
    return processed_subjects

@app.route('/')
def index():
    cursor = get_cursor()
    if not cursor:
        return "Database Connection Error. Check your MySQL server and configuration in app.py.", 500
    
    try:
        active_query = (
            'SELECT id, subject_name, chapter_name, difficulty, deadline, progress_pct, subject_unit '
            'FROM subjects WHERE progress_pct < 100 ORDER BY deadline ASC'
        )
        cursor.execute(active_query)
        active_subjects_raw = cursor.fetchall()
        
        completed_query = (
            'SELECT id, subject_name, chapter_name, subject_unit, deadline '
            'FROM subjects WHERE progress_pct = 100 ORDER BY deadline DESC'
        )
        cursor.execute(completed_query)
        completed_subjects_raw = cursor.fetchall()
        
        active_subjects = calculate_days_left(active_subjects_raw)
        
        return render_template('index.html', 
                               subjects=active_subjects, 
                               completed_subjects=completed_subjects_raw)
                               
    except mysql.connector.Error as err:
        print(f"Database query error: {err}")
        return "Error fetching data from database", 500
    finally:
        cursor.close()

@app.route('/add_subject', methods=['POST'])
def add_subject():
    cursor = get_cursor()
    if not cursor: 
        return redirect(url_for('index'))

    if request.method == 'POST':
        subject_name = request.form['syllabus_unit']
        subject_unit = int(request.form['unit_number']) if 'unit_number' in request.form and request.form['unit_number'] else 0
        chapter_name = request.form['name']
        sub_topic = request.form.get('sub_topic')
        difficulty = int(request.form['difficulty']) 
        deadline = request.form['deadline']

        if sub_topic:
            final_chapter_name = f"{chapter_name}: {sub_topic}"
        else:
            final_chapter_name = chapter_name
            
        try:
            insert_query = (
                'INSERT INTO subjects (subject_name, subject_unit, chapter_name, difficulty, deadline) '
                'VALUES (%s, %s, %s, %s, %s)'
            )
            cursor.execute(
                insert_query,
                (subject_name, subject_unit, final_chapter_name, difficulty, deadline)
            )
            cursor.connection.commit()
        except mysql.connector.Error as err:
            if "Duplicate entry" in str(err):
                print("Duplicate subject-chapter combination ignored")
            else:
                print(f"Insert failed: {err}")
        finally:
            cursor.close()
            
        return redirect(url_for('index'))

@app.route('/complete_subject', methods=['POST'])
def complete_subject():
    cursor = get_cursor()
    if not cursor: 
        return redirect(url_for('index'))

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        
        if subject_id:
            try:
                cursor.execute(
                    'UPDATE subjects SET progress_pct = 100 WHERE id = %s',
                    (subject_id,)
                )
                cursor.connection.commit()
            except mysql.connector.Error as err:
                print(f"Update failed: {err}")
            finally:
                cursor.close()
                
        return redirect(url_for('index'))

@app.route('/delete_subject', methods=['POST'])
def delete_subject():
    cursor = get_cursor()
    if not cursor: 
        return redirect(url_for('index'))

    if request.method == 'POST':
        subject_id = request.form.get('subject_id')
        
        if subject_id:
            try:
                cursor.execute(
                    'DELETE FROM subjects WHERE id = %s',
                    (subject_id,)
                )
                cursor.connection.commit()
            except mysql.connector.Error as err:
                print(f"Delete failed: {err}")
            finally:
                cursor.close()
                
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.teardown_appcontext(close_connection) 
    
    with app.app_context():
        init_db()
        
    app.run(debug=True)