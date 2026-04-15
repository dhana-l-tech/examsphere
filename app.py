"""
ExamSphere - Smart Online Examination System
Flask Backend with SQLite Database
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import os
import json
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'examsphere_secret_key_2024'

DB_PATH = 'examsphere.db'

# ─────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()

    # ── CREATE TABLES ──
    c.executescript("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            department TEXT DEFAULT 'Computer Science',
            year INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS exams (
            exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            duration INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            description TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS questions (
            question_id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            FOREIGN KEY (exam_id) REFERENCES exams(exam_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exam_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (exam_id) REFERENCES exams(exam_id)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ── SEED ADMIN ──
    c.execute("SELECT COUNT(*) FROM admins")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO admins (email, password, name) VALUES (?, ?, ?)",
                  ('admin@exam.com', hash_password('admin123'), 'Administrator'))

    # ── SEED STUDENTS ──
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] == 0:
        students = [
            ('Dhanush Kumar',  'dhan@exam.com',    'CS', 3),
            ('Arun Prakash',   'arun@exam.com',    'IT', 2),
            ('Priya Sharma',   'priya@exam.com',   'ECE', 3),
            ('Karthik Rajan',  'karthik@exam.com', 'CS', 4),
            ('Nivetha S',      'nivetha@exam.com', 'IT', 1),
            ('Rahul Verma',    'rahul@exam.com',   'CS', 2),
            ('Meena Lakshmi',  'meena@exam.com',   'ECE', 3),
            ('Sanjay Dev',     'sanjay@exam.com',  'CS', 4),
            ('Anitha R',       'anitha@exam.com',  'IT', 2),
            ('Vishal Nair',    'vishal@exam.com',  'CS', 1),
            ('Deepak Singh',   'deepak@exam.com',  'ECE', 3),
            ('Sneha Patel',    'sneha@exam.com',   'CS', 2),
            ('Rohit Menon',    'rohit@exam.com',   'IT', 4),
            ('Kavya Reddy',    'kavya@exam.com',   'CS', 3),
            ('Ajay Kumar',     'ajay@exam.com',    'ECE', 1),
        ]
        for name, email, dept, year in students:
            c.execute(
                "INSERT INTO students (name, email, password, department, year) VALUES (?,?,?,?,?)",
                (name, email, hash_password('1234'), dept, year)
            )

    # ── SEED EXAMS ──
    c.execute("SELECT COUNT(*) FROM exams")
    if c.fetchone()[0] == 0:
        exams = [
            ('Data Structures & Algorithms', 30, 50, 'Core CS concepts including arrays, trees, graphs and sorting'),
            ('Database Management Systems',  25, 40, 'SQL, normalization, transactions and ACID properties'),
            ('Operating Systems',            20, 30, 'Process management, memory, scheduling and deadlocks'),
            ('Computer Networks',            30, 50, 'OSI model, TCP/IP, routing and network security'),
            ('Python Programming',           20, 40, 'Python basics, OOP, file I/O and libraries'),
        ]
        for subject, duration, total, desc in exams:
            c.execute(
                "INSERT INTO exams (subject, duration, total_marks, description) VALUES (?,?,?,?)",
                (subject, duration, total, desc)
            )

    # ── SEED QUESTIONS ──
    c.execute("SELECT COUNT(*) FROM questions")
    if c.fetchone()[0] == 0:
        questions = [
            # DSA - exam_id=1
            (1,'What is the time complexity of binary search?','O(n)','O(log n)','O(n²)','O(1)','B'),
            (1,'Which data structure uses LIFO principle?','Queue','Array','Stack','Linked List','C'),
            (1,'What is the height of a complete binary tree with n nodes?','n','n/2','log n','2n','C'),
            (1,'Which sorting algorithm has best average case?','Bubble Sort','Selection Sort','Quick Sort','Insertion Sort','C'),
            (1,'In a min-heap, which element is at the root?','Maximum','Minimum','Median','Random','B'),
            (1,'What is the space complexity of merge sort?','O(1)','O(log n)','O(n)','O(n log n)','C'),
            (1,'Which traversal visits root first?','Inorder','Postorder','Preorder','Level order','C'),
            (1,'A graph with no cycles is called?','Tree','DAG','Connected Graph','Both A and B','D'),
            (1,'Stack overflow occurs due to?','Empty stack','Full stack','Recursive calls','None','C'),
            (1,'Dijkstra finds?','Minimum spanning tree','Shortest path','Longest path','Topological sort','B'),
            # DBMS - exam_id=2
            (2,'What does ACID stand for?','Atomicity Consistency Isolation Durability','All Correct In Database','Automatic Concurrency In DB','None','A'),
            (2,'Which SQL command retrieves data?','INSERT','UPDATE','SELECT','DELETE','C'),
            (2,'Primary key constraint ensures?','Uniqueness','Not null','Both A and B','Foreign reference','C'),
            (2,'Normalization reduces?','Queries','Redundancy','Indexes','Tables','B'),
            (2,'What is a foreign key?','Primary key of another table','Unique key','Index','Null key','A'),
            (2,'Which join returns all rows from both tables?','INNER JOIN','LEFT JOIN','RIGHT JOIN','FULL OUTER JOIN','D'),
            (2,'DDL stands for?','Data Definition Language','Data Deletion Language','Database Design Logic','None','A'),
            (2,'A view is?','Physical table','Virtual table','Stored procedure','Index','B'),
            # OS - exam_id=3
            (3,'What is deadlock?','Process waiting indefinitely','CPU idle','Memory full','Disk error','A'),
            (3,'Round Robin uses?','Priority','Time quantum','FIFO','None','B'),
            (3,'Virtual memory allows?','More RAM','Running programs larger than RAM','Faster CPU','None','B'),
            (3,'Semaphore is used for?','Scheduling','Synchronization','Memory','I/O','B'),
            (3,'Which is not a CPU scheduling algorithm?','FCFS','LIFO','SJF','Round Robin','B'),
            (3,'Paging eliminates?','Fragmentation','Internal fragmentation','External fragmentation','Both','C'),
            # Networks - exam_id=4
            (4,'OSI has how many layers?','5','6','7','8','C'),
            (4,'Which layer handles routing?','Data Link','Network','Transport','Application','B'),
            (4,'TCP is?','Connectionless','Connection-oriented','Both','Neither','B'),
            (4,'DNS resolves?','IP to MAC','Domain to IP','IP to domain','MAC to IP','B'),
            (4,'HTTP default port?','21','80','443','8080','B'),
            (4,'Which is a private IP range?','8.8.8.8','192.168.0.0','172.32.0.0','10.255.0.1','B'),
            # Python - exam_id=5
            (5,'Python is?','Compiled','Interpreted','Both','Assembly','B'),
            (5,'Which is mutable?','Tuple','String','List','Frozenset','C'),
            (5,'def keyword is for?','Variables','Functions','Classes','Loops','B'),
            (5,'What does len() return?','Type','Length','Value','None','B'),
            (5,'Which is used for inheritance?','extend','inherits','class Child(Parent)','super only','C'),
            (5,'List comprehension syntax?','[x for x in list]','(x for x in list)','{x for x in list}','x in list','A'),
            (5,'pip is used for?','Running code','Installing packages','Debugging','Version control','B'),
            (5,'__init__ is?','Destructor','Constructor','Static method','Class method','B'),
        ]
        c.executemany(
            "INSERT INTO questions (exam_id,question_text,option_a,option_b,option_c,option_d,correct_answer) VALUES (?,?,?,?,?,?,?)",
            questions
        )

    # ── SEED RESULTS ──
    c.execute("SELECT COUNT(*) FROM results")
    if c.fetchone()[0] == 0:
        import random as rnd
        c.execute("SELECT id FROM students")
        student_ids = [r[0] for r in c.fetchall()]
        c.execute("SELECT exam_id, total_marks FROM exams")
        exams_data = c.fetchall()
        for sid in student_ids:
            for exam_id, total in rnd.sample(exams_data, rnd.randint(2,4)):
                score = rnd.randint(int(total*0.4), total)
                c.execute(
                    "INSERT INTO results (student_id, exam_id, score, total_marks) VALUES (?,?,?,?)",
                    (sid, exam_id, score, total)
                )

    # ── SEED ANNOUNCEMENTS ──
    c.execute("SELECT COUNT(*) FROM announcements")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO announcements (title, message) VALUES (?,?)",
                  ('Welcome to ExamSphere!', 'The semester examination portal is now live. Good luck to all students!'))
        c.execute("INSERT INTO announcements (title, message) VALUES (?,?)",
                  ('Mid-Term Schedule', 'Mid-term exams are scheduled for the coming weeks. Please prepare accordingly.'))

    conn.commit()
    conn.close()

# ─────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email','').strip()
    password = hash_password(data.get('password',''))
    role = data.get('role','student')

    conn = get_db()
    c = conn.cursor()

    if role == 'admin':
        c.execute("SELECT * FROM admins WHERE email=? AND password=?", (email, password))
        admin = c.fetchone()
        conn.close()
        if admin:
            session['user_id'] = admin['id']
            session['role'] = 'admin'
            session['name'] = admin['name']
            return jsonify({'success': True, 'redirect': '/admin'})
        return jsonify({'success': False, 'message': 'Invalid admin credentials'})
    else:
        c.execute("SELECT * FROM students WHERE email=? AND password=?", (email, password))
        student = c.fetchone()
        conn.close()
        if student:
            session['user_id'] = student['id']
            session['role'] = 'student'
            session['name'] = student['name']
            return jsonify({'success': True, 'redirect': '/student'})
        return jsonify({'success': False, 'message': 'Invalid student credentials'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ─────────────────────────────────────────
# PAGE ROUTES
# ─────────────────────────────────────────

@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect('/login')
    return render_template('student_dashboard.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/login')
    return render_template('admin_dashboard.html')

@app.route('/exam/<int:exam_id>')
def exam_page(exam_id):
    if session.get('role') != 'student':
        return redirect('/login')
    return render_template('exam_page.html', exam_id=exam_id)

@app.route('/result')
def result_page():
    if not session.get('user_id'):
        return redirect('/login')
    return render_template('result_page.html')

# ─────────────────────────────────────────
# STUDENT API
# ─────────────────────────────────────────

@app.route('/api/student/profile')
def student_profile():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, name, email, department, year FROM students WHERE id=?", (session['user_id'],))
    student = dict(c.fetchone())

    c.execute("""
        SELECT COUNT(*) as count, AVG(CAST(score AS FLOAT)/total_marks*100) as avg_pct
        FROM results WHERE student_id=?
    """, (session['user_id'],))
    stats = dict(c.fetchone())
    conn.close()
    student['exams_taken'] = stats['count']
    student['avg_score'] = round(stats['avg_pct'] or 0, 1)
    return jsonify(student)

@app.route('/api/student/exams')
def student_exams():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT e.exam_id, e.subject, e.duration, e.total_marks, e.description,
               r.score, r.date,
               COUNT(q.question_id) as question_count
        FROM exams e
        LEFT JOIN questions q ON q.exam_id = e.exam_id
        LEFT JOIN results r ON r.exam_id = e.exam_id AND r.student_id = ?
        GROUP BY e.exam_id
    """, (session['user_id'],))
    exams = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(exams)

@app.route('/api/student/results')
def student_results():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT r.result_id, r.score, r.total_marks, r.date,
               e.subject, e.exam_id
        FROM results r
        JOIN exams e ON e.exam_id = r.exam_id
        WHERE r.student_id = ?
        ORDER BY r.date DESC
    """, (session['user_id'],))
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(results)

@app.route('/api/exam/<int:exam_id>/questions')
def get_exam_questions(exam_id):
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM exams WHERE exam_id=?", (exam_id,))
    exam = dict(c.fetchone())
    c.execute("""
        SELECT question_id, question_text, option_a, option_b, option_c, option_d
        FROM questions WHERE exam_id=?
    """, (exam_id,))
    questions = [dict(row) for row in c.fetchall()]
    random.shuffle(questions)
    conn.close()
    return jsonify({'exam': exam, 'questions': questions})

@app.route('/api/exam/submit', methods=['POST'])
def submit_exam():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    exam_id = data.get('exam_id')
    answers = data.get('answers', {})

    conn = get_db()
    c = conn.cursor()

    # Check already attempted
    c.execute("SELECT * FROM results WHERE student_id=? AND exam_id=?",
              (session['user_id'], exam_id))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Already attempted'}), 400

    c.execute("SELECT question_id, correct_answer FROM questions WHERE exam_id=?", (exam_id,))
    questions = c.fetchall()
    c.execute("SELECT total_marks FROM exams WHERE exam_id=?", (exam_id,))
    exam = c.fetchone()
    total_marks = exam['total_marks']

    correct = sum(1 for q in questions if answers.get(str(q['question_id'])) == q['correct_answer'])
    score = round((correct / len(questions)) * total_marks) if questions else 0

    c.execute(
        "INSERT INTO results (student_id, exam_id, score, total_marks) VALUES (?,?,?,?)",
        (session['user_id'], exam_id, score, total_marks)
    )
    conn.commit()
    conn.close()

    pct = round(score / total_marks * 100, 1)
    grade = 'A+' if pct>=90 else 'A' if pct>=80 else 'B' if pct>=70 else 'C' if pct>=60 else 'D' if pct>=50 else 'F'
    return jsonify({'score': score, 'total': total_marks, 'percentage': pct, 'grade': grade, 'correct': correct, 'total_questions': len(questions)})

# ─────────────────────────────────────────
# ADMIN API
# ─────────────────────────────────────────

@app.route('/api/admin/stats')
def admin_stats():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM students")
    total_students = c.fetchone()['count']
    c.execute("SELECT COUNT(*) as count FROM exams")
    total_exams = c.fetchone()['count']
    c.execute("SELECT AVG(CAST(score AS FLOAT)/total_marks*100) as avg FROM results")
    avg_score = round(c.fetchone()['avg'] or 0, 1)
    c.execute("SELECT COUNT(*) as count FROM results")
    total_attempts = c.fetchone()['count']
    conn.close()
    return jsonify({'total_students': total_students, 'total_exams': total_exams,
                    'avg_score': avg_score, 'total_attempts': total_attempts})

@app.route('/api/admin/students', methods=['GET'])
def admin_get_students():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT s.id, s.name, s.email, s.department, s.year,
               COUNT(r.result_id) as exams_taken,
               AVG(CAST(r.score AS FLOAT)/r.total_marks*100) as avg_score
        FROM students s
        LEFT JOIN results r ON r.student_id = s.id
        GROUP BY s.id ORDER BY s.name
    """)
    students = [dict(row) for row in c.fetchall()]
    for s in students:
        s['avg_score'] = round(s['avg_score'] or 0, 1)
    conn.close()
    return jsonify(students)

@app.route('/api/admin/students', methods=['POST'])
def admin_add_student():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO students (name, email, password, department, year) VALUES (?,?,?,?,?)",
            (data['name'], data['email'], hash_password(data['password']), data['department'], data['year'])
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already exists'})

@app.route('/api/admin/students/<int:sid>', methods=['PUT'])
def admin_update_student(sid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE students SET name=?, email=?, department=?, year=? WHERE id=?",
              (data['name'], data['email'], data['department'], data['year'], sid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/students/<int:sid>', methods=['DELETE'])
def admin_delete_student(sid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/exams', methods=['GET'])
def admin_get_exams():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT e.*, COUNT(q.question_id) as question_count
        FROM exams e LEFT JOIN questions q ON q.exam_id=e.exam_id
        GROUP BY e.exam_id ORDER BY e.exam_id
    """)
    exams = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(exams)

@app.route('/api/admin/exams', methods=['POST'])
def admin_add_exam():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO exams (subject, duration, total_marks, description) VALUES (?,?,?,?)",
              (data['subject'], data['duration'], data['total_marks'], data.get('description','')))
    conn.commit()
    exam_id = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'exam_id': exam_id})

@app.route('/api/admin/exams/<int:eid>', methods=['PUT'])
def admin_update_exam(eid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE exams SET subject=?, duration=?, total_marks=?, description=? WHERE exam_id=?",
              (data['subject'], data['duration'], data['total_marks'], data.get('description',''), eid))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/exams/<int:eid>', methods=['DELETE'])
def admin_delete_exam(eid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM exams WHERE exam_id=?", (eid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/questions/<int:exam_id>', methods=['GET'])
def admin_get_questions(exam_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE exam_id=?", (exam_id,))
    questions = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(questions)

@app.route('/api/admin/questions', methods=['POST'])
def admin_add_question():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer)
        VALUES (?,?,?,?,?,?,?)
    """, (data['exam_id'], data['question_text'], data['option_a'], data['option_b'],
          data['option_c'], data['option_d'], data['correct_answer']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/questions/<int:qid>', methods=['DELETE'])
def admin_delete_question(qid):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE question_id=?", (qid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin/results')
def admin_get_results():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT r.result_id, r.score, r.total_marks, r.date,
               s.name as student_name, s.department,
               e.subject
        FROM results r
        JOIN students s ON s.id=r.student_id
        JOIN exams e ON e.exam_id=r.exam_id
        ORDER BY r.date DESC
    """)
    results = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(results)

@app.route('/api/admin/leaderboard')
def admin_leaderboard():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        SELECT s.name, s.department,
               COUNT(r.result_id) as exams_taken,
               AVG(CAST(r.score AS FLOAT)/r.total_marks*100) as avg_pct
        FROM students s JOIN results r ON r.student_id=s.id
        GROUP BY s.id ORDER BY avg_pct DESC LIMIT 10
    """)
    leaders = [dict(row) for row in c.fetchall()]
    for l in leaders:
        l['avg_pct'] = round(l['avg_pct'] or 0, 1)
    conn.close()
    return jsonify(leaders)

@app.route('/api/admin/announcements', methods=['GET'])
def get_announcements():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM announcements ORDER BY created_at DESC")
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(items)

@app.route('/api/admin/announcements', methods=['POST'])
def add_announcement():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO announcements (title, message) VALUES (?,?)", (data['title'], data['message']))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
