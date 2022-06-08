from flask import g
from db_conn import *

class AssessmentIndicator:
    def __init__(self, subjectCode, cpmkCode, subCpmkCode, code):
        self.subjectCode = subjectCode
        self.cpmkCode = cpmkCode
        self.subCpmkCode = subCpmkCode
        self.code = code
        self.name = ''
        self.gradePercent = ''

        self.setNameAndGradePercent()

    def setNameAndGradePercent(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT indikatorPenilaianDesc, gradePercent FROM indikatorpenilaian WHERE subjectCode = "%s" AND cpmkCode = "%s" AND subCpmkCode = "%s" AND indikatorPenilaianCode = "%s"' % (self.subjectCode, self.cpmkCode, self.subCpmkCode, self.code))
        result = cursor.fetchone()
        conn.close()

        self.name = result[0]
        self.gradePercent = result[1]
    
class SubCpmk:
    def __init__(self, subjectCode, cpmkCode, code):
        self.subjectCode = subjectCode
        self.cpmkCode = cpmkCode
        self.code = code
        self.name = 'name'
        self.gradePercent = 0
        self.assessmentIndicator = []
        
        self.setNameAndGradePercent()
        self.setAssessmentIndicator()

    def setNameAndGradePercent(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT subCpmkDesc, gradePercent FROM subcpmk WHERE subjectCode = "%s" AND cpmkCode = "%s" AND subCpmkCode = "%s"' % (self.subjectCode, self.cpmkCode, self.code))
        result = cursor.fetchone()
        conn.close()

        self.name = result[0]
        self.gradePercent = result[1]
    
    def setAssessmentIndicator(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT indikatorPenilaianCode FROM indikatorpenilaian WHERE subjectCode = "%s" AND cpmkCode = "%s" AND subCpmkCode = "%s"' % (self.subjectCode, self.cpmkCode, self.code))
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            assessInd = AssessmentIndicator(self.subjectCode, self.cpmkCode, self.code, entry[0])
            self.assessmentIndicator.append(assessInd)

class Cpmk:
    def __init__(self, subjectCode, code):
        self.subjectCode = subjectCode
        self.code = code
        self.name = ''
        self.gradePercent = ''
        self.subCpmk = []
        
        self.setSubCpmk()
        self.setNameAndGradePercent()
    
    def setSubCpmk(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT subCpmkCode FROM subcpmk WHERE subjectCode = "%s" AND cpmkCode = "%s"' % (self.subjectCode, self.code))
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            subCpmk = SubCpmk(self.subjectCode, self.code, entry[0])
            self.subCpmk.append(subCpmk)
        
    def setNameAndGradePercent(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT CPMKDesc, gradePercent FROM cpmk WHERE subjectCode = "%s" AND cpmkCode = "%s"' % (self.subjectCode, self.code))
        result = cursor.fetchone()
        conn.close()

        self.name = result[0]
        self.gradePercent = result[1]

class FinalExam:
    def __init__(self, subjectCode):
        self.subjectCode = subjectCode
        self.gradePercent = 0

        self.setGradePercent()

    def setGradePercent(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT gradePercent FROM finalexam WHERE subjectCode = "%s"' % (self.subjectCode))
        result = cursor.fetchone()
        conn.close()

        self.gradePercent = result[0]

class Subject:
    def __init__(self, code):
        self.code = code
        self.name = ''
        self.cpmk = []
        
        self.setName()
        self.setCpmk()

    def setName(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT subjectName FROM subject WHERE subjectCode = "%s"' % (self.code,))
        self.name = cursor.fetchone()[0]
        conn.close()

    def setCpmk(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT cpmkCode FROM cpmk WHERE subjectCode = "%s"' % (self.code,))
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            cpmk = Cpmk(self.code, entry[0])
            self.cpmk.append(cpmk)

class AssessmentIndicatorGrade:
    def __init__(self, subjectCode, cpmkCode, subCpmkCode, code, nim, nip, year):
        self.assessmentIndicator = AssessmentIndicator(subjectCode, cpmkCode, subCpmkCode, code)
        self.nim = nim
        self.nip = nip
        self.year = year
        self.subCpmkGradePercent = self.assessmentIndicator.gradePercent
        self.grade = 0

        self.setGrade()

    def setGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT grade FROM indikatorpenilaiangrade WHERE subjectCode = "%s" AND cpmkCode = "%s" AND subCpmkCode = "%s" AND indikatorPenilaianCode = "%s" AND NIM = "%s" AND NIP = "%s" AND YEAR(date) = %s' % (self.assessmentIndicator.subjectCode, self.assessmentIndicator.cpmkCode, self.assessmentIndicator.subCpmkCode, self.assessmentIndicator.code, self.nim, self.nip, self.year))
        self.grade = cursor.fetchone()[0]
        conn.close()

class SubCpmkGrade:
    def __init__(self, subjectCode, cpmkCode, code, nim, nip, year):
        self.subCpmk = SubCpmk(subjectCode, cpmkCode, code)
        self.nim = nim
        self.nip = nip
        self.year = year
        self.cpmkGradePercent = self.subCpmk.gradePercent
        self.assessmentIndicatorGrade = []
        self.grade = 0

        self.setAssessmentIndicatorGrades()
        self.setGrade()
                            
    def setAssessmentIndicatorGrades(self):
        for i in self.subCpmk.assessmentIndicator:
            ig = AssessmentIndicatorGrade(self.subCpmk.subjectCode, self.subCpmk.cpmkCode, self.subCpmk.code, i.code, self.nim, self.nip, self.year)
            self.assessmentIndicatorGrade.append(ig)
    
    def setGrade(self):
        for ig in self.assessmentIndicatorGrade:
            grade = ig.grade * ig.subCpmkGradePercent/100
            self.grade += grade
    
    def inputGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subcpmkgrade (subCpmkCode, cpmkCode, subjectCode, NIM, NIP, grade) VALUES ("%s", "%s", "%s", "%s", "%s", %s)' % (self.code, self.cpmkCode, self.subjectCode, self.nim, self.nip, self.grade))
        conn.commit()
        conn.close()
    
class CpmkGrade:
    def __init__(self, subjectCode, code, nim, nip, year):
        self.cpmk = Cpmk(subjectCode, code)
        self.nim = nim
        self.nip = nip
        self.year = year
        self.subjectGradePercent = self.cpmk.gradePercent
        self.subCpmkGrades = []
        self.grade = 0

        self.setSubCpmkGrades()
        self.setGrade()

    def setSubCpmkGrades(self):
        for s in self.cpmk.subCpmk:
            sg = SubCpmkGrade(self.cpmk.subjectCode, self.cpmk.code, s.code, self.nim, self.nip, self.year)
            self.subCpmkGrades.append(sg)

    def setGrade(self):
        for sg in self.subCpmkGrades:
            grade = sg.grade * sg.cpmkGradePercent/100
            self.grade += grade
    
    def inputGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO cpmkgrade (cpmkCode, subjectCode, NIM, NIP, grade) VALUES ("%s", "%s", "%s", "%s", %s)' % (self.cpmk.code, self.cpmk.subjectCode, self.nim, self.nip, self.grade))
        conn.commit()
        conn.close()
    
class FinalExamGrade:
    def __init__(self, subjectCode, nim, nip, year):
        self.finalExam = FinalExam(subjectCode)
        self.nim = nim
        self.nip = nip
        self.year = year
        self.subjectGradePercent= self.finalExam.gradePercent
        self.grade = 0
        
        self.setGrade()
        
    def setGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT grade FROM finalexamgrade WHERE subjectCode = "%s" AND NIM = "%s" AND NIP = "%s" AND YEAR(date) = %s' % (self.finalExam.subjectCode, self.nim, self.nip, self.year))
        self.grade = cursor.fetchone()[0]
        conn.close()

class SubjectGrade:
    def __init__(self, subjectCode, nim, nip, year):
        self.subject = Subject(subjectCode)
        self.nim = nim
        self.nip = nip
        self.year = year
        self.cpmkGrades= []
        self.finalExamGrade = FinalExamGrade(subjectCode, nim, nip, year)
        self.grade = 0

        self.setCpmkGrades()
        self.setGrade()

    def setCpmkGrades(self):
        for c in self.subject.cpmk:
            cpmkGrade = CpmkGrade(self.subject.code, c.code, self.nim, self.nip, self.year)
            self.cpmkGrades.append(cpmkGrade)

    def setGrade(self):
        for cg in self.cpmkGrades:
            cpmkGrade = cg.grade * cg.subjectGradePercent/100
            self.grade += cpmkGrade
        
        finalGrade = self.finalExamGrade.grade * self.finalExamGrade.subjectGradePercent/100
        self.grade += finalGrade

    def inputGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subjectgrade (subjectCode, NIM, NIP, grade) VALUES ("%s", "%s", "%s", %s)' % (self.subject.code, self.nim, self.nip, self.grade))
        conn.commit()
        conn.close()
    
    def getCpmkGrade(self, cpmkCode):
        for cg in self.cpmkGrades:
            if (cg.cpmk.code == cpmkCode):
                return cg.grade

class Enroll:
    def __init__(self, nim, year):
        self.nim = nim
        self.year = year
        self.enrolled = []
        
        self.setEnrolled()

    def setEnrolled(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM enroll WHERE NIM = "%s" AND YEAR(date) = %s' % (self.nim, self.year))
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            subject = Subject(entry[1])
            self.enrolled.append(subject)

class Cpl:
    def __init__(self, code):
        self.code = code
        self.name = ''
        self.subjectCode = ''

        self.setName()
        self.setSubjectCode()

    def setName(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT cplDesc FROM cpl WHERE cplCode = "%s"' % (self.code,))
        self.name = cursor.fetchone()[0]
        conn.close()
    
    def setSubjectCode(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT subjectCode FROM cpl WHERE cplCode = "%s"' % (self.code,))
        self.subjectCode = cursor.fetchone()[0]
        conn.close()