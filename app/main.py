from http.cookies import _unquote
from flask import Flask, render_template, request, session, redirect, url_for
from db_conn import *
from obj import *
import urllib.parse

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
    return redirect(url_for('loginEducator')) #render_template('login.html') 

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
                    session['nip'] = entry[0]
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
                    session['nim'] = entry[0]
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
    cursor.execute('SELECT * FROM enroll WHERE NIM = "%s" AND YEAR(date) = 2022' % (session['nim'],))
    result2 = cursor.fetchall()
    conn.close()

    enrolled = []
    for entry in result2 :
        enrolled.append(entry[1])

    return render_template('student/studentSubject.html', subject = subjects, enr = enrolled)

@app.route('/student/<subjectCode>/enroll', methods = ['POST'])
def studentSubjectEnroll(subjectCode):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO enroll(NIM, subjectCode) VALUES ("%s", "%s")' % (session['nim'],subjectCode))
    conn.commit()
    conn.close()

    return redirect(url_for('studentSubject'))


@app.route('/student/subject/<subjectCode>')
def studentSubjectDetails(subjectCode):
    return render_template('student/studentSubjectDetails.html', subject = Subject(subjectCode))

@app.route('/student/enrolled')
def studentEnrolled():
    return 'enrolled'

@app.route('/student/enrolled/<subjectCode>')
def studentEnrolledDetails(subjectCode):
    return subjectCode

@app.route('/student/grades')
def studentGrades():
    enroll = Enroll(session['nim'], '2022')
    subjectGrade = []
    for e in enroll.enrolled:
        sg = SubjectGrade(e.code, session['nim'], '2022', '2022')
        subjectGrade.append(sg)
    return render_template('student/studentGrades.html', subjectGrade = subjectGrade)

@app.route('/student/grades/<subjectCode>')
def studentGradesDetails(subjectCode):
    subjectGrade = SubjectGrade(subjectCode, session['nim'], '2022', '2022')
    finalExamGrade = FinalExamGrade(subjectCode, session['nim'], '2022', '2022')
    return render_template('student/studentGradesDetails.html', subjectGrade = subjectGrade, finalExamGrade = finalExamGrade)

@app.route('/student/grades/<subjectCode>/<cpmkCode>')
def studentGradesDetailsCpmk(subjectCode, cpmkCode):
    cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
    cpmkGrade = CpmkGrade(subjectCode, cpmkCodeParsed, session['nim'], '2022', '2022')
    return render_template('student/studentGradesDetailsCpmk.html', cpmkGrade = cpmkGrade )

@app.route('/student/grades/<subjectCode>/<cpmkCode>/<subCpmkCode>')
def studentGradesDetailsCpmkSubCpmk(subjectCode, cpmkCode, subCpmkCode):
    cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
    subCpmkGrade = SubCpmkGrade(subjectCode, cpmkCodeParsed, subCpmkCode, session['nim'], '2022', '2022')
    return render_template('student/studentGradesDetailsCpmkSubCpmk.html', subCpmkGrade = subCpmkGrade )

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
    return render_template('admin/adminCpl.html', cpl = cpls)

@app.route('/admin/cpl/add', methods=['GET', 'POST'])
def adminAddCpl():
    if request.method == 'GET':
        return render_template('admin/adminCplAdd.html')
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
    
    return render_template('admin/adminSubject.html', list = subjectList)

@app.route('/admin/subject/add', methods=['GET', 'POST'])
def adminSubjectAdd():
    if request.method == 'GET':
        return render_template('admin/adminSubjectAdd.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subject (subjectCode, subjectName) VALUES ("%s", "%s")' % (request.form['subjectCode'], request.form['subjectName']))
        conn.commit()
        conn.close()

        return redirect(url_for('adminSubject'))

@app.route('/admin/educators/')
def adminEducator():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tenagapendidik WHERE isDosen = 1')
    result = cursor.fetchall()
    conn.close()

    educatorList = []
    for entry in result:
        educatorList.append(entry)
    
    return render_template('admin/adminEducator.html', list = educatorList)

@app.route('/admin/students/')
def adminStudents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mahasiswa')
    result = cursor.fetchall()
    conn.close()

    studentList = []
    for entry in result:
        studentList.append(entry)
    
    return render_template('admin/adminStudent.html', list = studentList)

@app.route('/admin/assignmentsModel/')
def adminAssignmentsModel():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assignmentmodel')
    result = cursor.fetchall()
    conn.close()
    return render_template('admin/adminAssignmentsModel.html', list = result)

@app.route('/admin/assignmentsModel/add', methods=['GET', 'POST'])
def adminAssignmentsModelAdd():
    if (request.method == 'GET'):
        return render_template('admin/adminAssignmentsModelAdd.html')
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO assignmentmodel VALUES ("%s", "%s")' % (request.form['modelCode'], request.form['modelName']))
        conn.commit()

        cursor.execute('INSERT INTO assignmentrubric VALUES ("%s", "%s", "%s", "%s")' % (request.form['modelCode'], request.form['code1'], request.form['desc1'], request.form['g1']))
        conn.commit()
        cursor.execute('INSERT INTO assignmentrubric VALUES ("%s", "%s", "%s", "%s")' % (request.form['modelCode'], request.form['code2'], request.form['desc2'], request.form['g2']))
        conn.commit()
        cursor.execute('INSERT INTO assignmentrubric VALUES ("%s", "%s", "%s", "%s")' % (request.form['modelCode'], request.form['code3'], request.form['desc3'], request.form['g3']))
        conn.commit()
        cursor.execute('INSERT INTO assignmentrubric VALUES ("%s", "%s", "%s", "%s")' % (request.form['modelCode'], request.form['code4'], request.form['desc4'], request.form['g4']))
        conn.commit()
        cursor.execute('INSERT INTO assignmentrubric VALUES ("%s", "%s", "%s", "%s")' % (request.form['modelCode'], request.form['code5'], request.form['desc5'], request.form['g5']))
        conn.commit()
        conn.close()
        return redirect(url_for('adminAssignmentsModel'))

@app.route('/admin/assignmentsModel/<assignmentModelCode>')
def adminAssignmentsModelRubric(assignmentModelCode):
    assignmentModel = AssignmentModel(assignmentModelCode)
    return render_template('admin/adminAssignmentsModelRubric.html', list = assignmentModel.assignmentRubric.getCriteria())

adminAssignmentsModelAdd
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
    return render_template('admin/adminAssignCpl.html', cpl = cpls)

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

        return render_template('admin/adminAssignCplSubject.html', list = subjectList, cplCode = cplCode)
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
    cursor.execute('SELECT NIP, subjectCode FROM course WHERE date in (SELECT MAX(date) FROM course GROUP BY subjectCode)')
    result2 = cursor.fetchall()
    conn.close()

    courseList = []
    for entry in result2:
        courseList.append(entry)

    return render_template('admin/adminAssignSubject.html', list = subjectList, courseList = courseList)

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

        return render_template('admin/adminAssignSubjectEducator.html', list = educatorList, subjectCode = subjectCode)
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO course (NIP, subjectCode) VALUES ("%s", "%s")' % (request.form['nip'], subjectCode))
        conn.commit()
        conn.close()

        return redirect(url_for('adminAssignSubject'))

@app.route('/educator')
@app.route('/educator/subjects/')
def educatorSubject():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subject.subjectCode, subject.subjectName FROM subject INNER JOIN course ON subject.subjectCode=course.subjectCode WHERE course.NIP="%s"' % (session['nip'],))
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)
    
    return render_template('educator/educatorSubject.html', list = subjectList)

@app.route('/educator/<subjectCode>/')
def educatorSubjectCpmk(subjectCode):
    return render_template('educator/educatorSubjectCpmk.html', subject = Subject(subjectCode))

@app.route('/educator/<subjectCode>/CPMK/add', methods=['GET', 'POST'])
def educatorSubjectCpmkAdd(subjectCode):
    if (request.method == 'GET'):
        return render_template('educator/educatorSubjectCpmkAdd.html', subjectCode = subjectCode)
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cpmk VALUES ("%s", "%s", "%s", %s)' % (request.form['cpmkCode'], subjectCode, request.form['cpmkDesc'], request.form['gradePercent']))
        conn.commit()
        conn.close()

        return redirect(url_for('educatorSubjectCpmk', subjectCode = subjectCode))

@app.route('/educator/<subjectCode>/<cpmkCode>/')
def educatorSubjectCpmkSubCpmk(subjectCode, cpmkCode):
    cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
    cpmk = Cpmk(subjectCode, cpmkCodeParsed)
    
    return render_template('educator/educatorSubjectCpmkSubCpmk.html', cpmk = cpmk)

@app.route('/educator/<subjectCode>/<cpmkCode>/SubCPMK/Add/', methods=['GET', 'POST'])
def educatorSubjectCpmkSubCpmkAdd(subjectCode, cpmkCode):
    if (request.method == 'GET'):
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        return render_template('educator/educatorSubjectCpmkSubCpmkAdd.html', subjectCode = subjectCode, cpmkCode = cpmkCodeParsed)
    else:
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subcpmk VALUES ("%s", "%s", "%s", "%s", "%s")' % (request.form['subCpmkCode'], cpmkCodeParsed, subjectCode, request.form['subCpmkDesc'], request.form['gradePercent']))
        conn.commit()
        conn.close()

        return redirect(url_for('educatorSubjectCpmkSubCpmk', subjectCode = subjectCode, cpmkCode = cpmkCodeParsed))

@app.route('/educator/<subjectCode>/<cpmkCode>/<subCpmkCode>/')
def educatorSubjectCpmkSubCpmkIndikator(subjectCode, cpmkCode, subCpmkCode):
    cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
    cpmk = Cpmk(subjectCode, cpmkCodeParsed)
    
    for subCpmk in cpmk.subCpmk:
        if (subCpmk.code == subCpmkCode):
            return render_template('educator/educatorSubjectCpmkSubCpmkIndikator.html', subCpmk = subCpmk)

@app.route('/educator/<subjectCode>/<cpmkCode>/<subCpmkCode>/indikatorPenilaian/Add', methods=['GET', 'POST'])
def educatorSubjectCpmkSubCpmkIndikatorAdd(subjectCode, cpmkCode, subCpmkCode):
    if (request.method == 'GET'):
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        return render_template('educator/educatorSubjectCpmkSubCpmkIndikatorAdd.html', subjectCode = subjectCode, cpmkCode = cpmkCodeParsed, subCpmkCode = subCpmkCode)
    else:
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO indikatorpenilaian VALUES ("%s", "%s", "%s", "%s", "%s", "%s")' % (request.form['indikatorCode'], subCpmkCode, cpmkCodeParsed, subjectCode, request.form['indikatorDesc'], request.form['gradePercent']))
        conn.commit()
        conn.close()

        return redirect(url_for('educatorSubjectCpmkSubCpmkIndikator', subjectCode = subjectCode, cpmkCode = cpmkCodeParsed, subCpmkCode = subCpmkCode))

@app.route('/educator/<subjectCode>/<cpmkCode>/<subCpmkCode>/<indikatorPenilaianCode>', methods = ['GET', 'POST'])
def educatorSubjectCpmkSubCpmkIndikatorRubric(subjectCode, cpmkCode, subCpmkCode, indikatorPenilaianCode):
    if (request.method == 'GET'):
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        indikator = AssessmentIndicator(subjectCode, cpmkCodeParsed, subCpmkCode, indikatorPenilaianCode)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT assignmentModelCode FROM indikatorpenilaian_assignmentmodel WHERE indikatorPenilaianCode = "%s" AND subCpmkCode = "%s" AND cpmkCode = "%s" AND subjectCode = "%s"' % (indikatorPenilaianCode, subCpmkCode, cpmkCodeParsed, subjectCode))
        result = cursor.fetchone()
        conn.close()
        code = []
        rubric = []
        if (result == None):
            pass
        else:
            code = result[0]
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM assignmentrubric WHERE assignmentModelCode = "%s"' % (code[0]))
            result2 = cursor.fetchall()
            conn.close()
            rubric = result2

        return render_template('educator/educatorSubjectCpmkSubCpmkIndikatorRubric.html', list = code, rub = rubric, indikator = indikator)
    else:
        cpmkCodeParsed = urllib.parse.unquote(cpmkCode)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO indikatorpenilaian_assignmentmodel VALUES ("%s", "%s", "%s", "%s", "%s")' % (indikatorPenilaianCode, subCpmkCode, cpmkCodeParsed, subjectCode,  request.form['model']))
        conn.commit()
        conn.close()

        return redirect(url_for('educatorSubjectCpmkSubCpmkIndikatorRubric', subjectCode = subjectCode, cpmkCode = cpmkCodeParsed, subCpmkCode = subCpmkCode, indikatorPenilaianCode = indikatorPenilaianCode))

@app.route('/educator/grade')
def educatorGrade():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT subject.subjectCode, subject.subjectName FROM subject INNER JOIN course ON subject.subjectCode=course.subjectCode WHERE course.NIP="%s"' % (session['nip'],))
    result = cursor.fetchall()
    conn.close()

    subjectList = []
    for entry in result:
        subject = Subject(entry[0])
        subjectList.append(subject)
    
    return render_template('educator/educatorGrade.html', list = subjectList)

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
    
    return render_template('educator/educatorGradeStudents.html', students = students, subjectCode = subjectCode)

@app.route('/logout')
def logout():
    session['user'] = ''
    return redirect(url_for('login'))