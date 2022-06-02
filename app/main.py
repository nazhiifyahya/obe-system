from flask import Flask, render_template, request, session, redirect, url_for
from db_conn import *
from obj import *

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
    return render_template('login.html')

@app.route('/login/educator', methods = ['GET', 'POST'])
def loginEducator():
    if (request.method == 'GET'):
        return render_template('loginEducator.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tenagapendidik')
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            if (request.form['username'] == entry[2]):
                if (request.form['password'] == entry[3]):
                    session['user'] = entry[1]
                    if (entry[5] == 1):
                        return redirect(url_for('educatorSubject'))
                    return redirect(url_for('adminCPL'))
        return redirect(url_for('loginEducator'))
        
@app.route('/login/student', methods = ['GET', 'POST'])
def loginStudent():
    if (request.method == 'GET'):
        return render_template('loginStudent.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM mahasiswa')
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            if (request.form['username'] == entry[2]):
                if (request.form['password'] == entry[3]):
                    session['user'] = entry[1]
                    return redirect(url_for('studentSubject'))
        return redirect(url_for('loginStudent'))

@app.route('/student')
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

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM enroll WHERE NIM = "1953" AND YEAR(date) = 2022')
    result2 = cursor.fetchall()
    conn.close()

    enrolled = []
    for entry in result2 :
        enrolled.append(entry[1])

    return render_template('studentSubject.html', subject = subjects, enr = enrolled)

@app.route('/student/<subjectCode>/enroll', methods = ['POST'])
def studentSubjectEnroll(subjectCode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO enroll(NIM, subjectCode) VALUES ("1953", "%s")' % (subjectCode,))
    conn.commit()
    conn.close()

    return redirect(url_for('studentSubject'))


@app.route('/student/subject/<subjectCode>')
def studentSubjectDetails(subjectCode):
    return render_template('studentSubjectDetails.html', subject = Subject(subjectCode))

@app.route('/student/enrolled')
def studentEnrolled():
    return 'enrolled'

@app.route('/student/enrolled/<subjectCode>')
def studentEnrolledDetails(subjectCode):
    return subjectCode

@app.route('/student/grades')
def studentGrades():
    enroll = Enroll('1953', '2022')
    subjectGrade = []
    for e in enroll.enrolled:
        sg = SubjectGrade(e.code, '1953', '2022', '2022')
        subjectGrade.append(sg)
    return render_template('studentGrades.html', subjectGrade = subjectGrade)

@app.route('/student/grades/<subjectCode>')
def studentGradesDetails(subjectCode):
    return render_template('studentGradesDetails.html', subjectGrade = SubjectGrade(subjectCode, '1953', '2022', '2022'))


@app.route('/admin')
@app.route('/admin/CPL')
def adminCPL():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT cplCode FROM cpl')
    result = cursor.fetchall()
    conn.close()

    cpls = []
    for entry in result:
        cpl = Cpl(entry[0])
        cpls.append(cpl)
    return render_template('adminCpl.html', cpl = cpls)

@app.route('/admin/cpl/add', methods=['GET', 'POST'])
def adminAddCpl():
    if request.method == 'GET':
        return render_template('adminCplAdd.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cpl (cplCode, cplDesc) VALUES ("%s", "%s")' % (request.form['cplCode'], request.form['cplDesc']))
        conn.commit()
        conn.close()

        return redirect(url_for('adminCPL'))

@app.route('/admin/subject')
def adminSubject():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subjectCode FROM subject')
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)
    
    return render_template('adminSubject.html', list = subjectList)

@app.route('/admin/subject/add', methods=['GET', 'POST'])
def adminSubjectAdd():
    if request.method == 'GET':
        return render_template('adminSubjectAdd.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subject (subjectCode, subjectName) VALUES ("%s", "%s")' % (request.form['subjectCode'], request.form['subjectName']))
        conn.commit()
        conn.close()

        return redirect(url_for('adminSubject'))

@app.route('/admin/assign/cpl')
def adminAssignCpl():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT cplCode FROM cpl')
    result = cursor.fetchall()
    conn.close()

    cpls = []
    for entry in result:
        cpl = Cpl(entry[0])
        cpls.append(cpl)
    return render_template('adminAssignCpl.html', cpl = cpls)

@app.route('/admin/assign/<cplCode>/subject', methods=['GET', 'POST'])
def adminAssignCplSubject(cplCode):
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT subjectCode FROM subject')
        result = cursor.fetchall()
        conn.close()

        subjectList = []
        for entry in result:
            subject = Subject(entry[0])
            subjectList.append(subject)

        return render_template('adminAssignCplSubject.html', list = subjectList, cplCode = cplCode)
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE cpl SET subjectCode = "%s" WHERE cplCode = "%s"' % (request.form['subjectCode'], cplCode))
        conn.commit()
        conn.close()

        return redirect(url_for('adminAssignCpl'))

@app.route('/admin/assign/subject')
def adminAssignSubject():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subjectCode FROM subject')
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM course')
    result2 = cursor.fetchall()
    conn.close()

    courseList = []
    for entry in result2:
        courseList.append(entry)

    return render_template('adminAssignSubject.html', list = subjectList, courseList = courseList)

@app.route('/admin/assign/<subjectCode>/educator', methods=['GET', 'POST'])
def adminAssignSubjectEducator(subjectCode):
    if request.method == 'GET':
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tenagapendidik WHERE isDosen = 1')
        result = cursor.fetchall()
        conn.close()

        educatorList = []
        for entry in result:
            educatorList.append(entry)

        return render_template('adminAssignSubjectEducator.html', list = educatorList, subjectCode = subjectCode)
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO course (NIP, subjectCode) VALUES ("%s", "%s")' % (request.form['nip'], subjectCode))
        conn.commit()
        conn.close()

        return redirect(url_for('adminAssignSubject'))

@app.route('/educator')
@app.route('/educator/subject')
def educatorSubject():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subject.subjectCode, subject.subjectName FROM subject INNER JOIN course ON subject.subjectCode=course.subjectCode WHERE course.NIP=2022')
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)
    
    return render_template('educatorSubject.html', list = subjectList)

@app.route('/educator/<subjectCode>/cpmk')
def educatorSubjectCpmk(subjectCode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cpmk WHERE subjectCode = "%s"' % (subjectCode))
    result = cursor.fetchall()
    conn.close()

    cpmk = []
    for entry in result:
        cpmk.append(entry)
    
    return render_template('educatorSubjectCpmk.html', cpmk = cpmk, subjectCode = subjectCode)

@app.route('/educator/<subjectCode>/cpmk/add', methods=['GET', 'POST'])
def educatorSubjectCpmkAdd(subjectCode):
    if (request.method == 'GET'):
        return render_template('educatorSubjectCpmkAdd.html', subjectCode = subjectCode)
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cpmk VALUES ("%s", "%s", "%s", %s)' % (request.form['cpmkCode'], subjectCode, request.form['cpmkDesc'], request.form['gradePercent']))
        conn.commit()
        conn.close()

        return redirect(url_for('educatorSubjectCpmk', subjectCode = subjectCode))

@app.route('/educator/grade')
def educatorGrade():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subject.subjectCode, subject.subjectName FROM subject INNER JOIN course ON subject.subjectCode=course.subjectCode WHERE course.NIP=2022')
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)
    
    return render_template('educatorGrade.html', list = subjectList)

@app.route('/educator/<subjectCode>/student')
def educatorGradeStudent(subjectCode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM enroll WHERE subjectCode = "%s"' % (subjectCode,))
    result = cursor.fetchall()
    conn.close()

    students = []
    for entry in result:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nama FROM mahasiswa WHERE NIM = "%s"' % (entry[0]))
        name = cursor.fetchone()[0]
        conn.close()

        student = [entry[0], name]
        students.append(student) 
    
    return render_template('educatorGradeStudents.html', students = students, subjectCode = subjectCode)

@app.route('/logout')
def logout():
    session['user'] = ''
    return redirect(url_for('login'))