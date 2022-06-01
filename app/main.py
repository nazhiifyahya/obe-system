from re import sub
from flask import Flask, render_template, session, redirect, url_for
import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="obe_system"
    )

    return conn

app = Flask(__name__)
app.secret_key = 'thisIsSecret'

@app.route('/')
def home():
    if 'user' in session:
        return 'hi'
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    session['user'] = 'nazhiif'
    return redirect(url_for('home'))

@app.route('/student')
def student():
    return 'hello student'

@app.route('/student/subject')
def studentSubject():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subject')
    result = cursor.fetchall()
    conn.close()

    subjects = []
    for entry in result :
        subject = {
            'code': entry[0],
            'name': entry[1]
        }
        subjects.append(subject)
    return render_template('studentSubject.html', subject = subjects)

@app.route('/student/subject/<subjectCode>')
def studentSubjectDetails(subjectCode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subject WHERE subjectCode = %s' % (subjectCode,))
    result = cursor.fetchall()
    conn.close()
    return subjectCode

@app.route('/student/enrolled')
def studentEnrolled():
    return 'enrolled'

@app.route('/student/enrolled/<subjectCode>')
def studentEnrolledDetails(subjectCode):
    return subjectCode

@app.route('/student/grades')
def studentGrades():
    return 'grade'

@app.route('/student/grades/<subjectCode>')
def studentGradesDetails(subjectCode):
    return subjectCode