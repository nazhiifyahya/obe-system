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
    def __init__(self, subjectCode, cpmkCode, code, name, gradePercent):
        self.subjectCode = subjectCode
        self.cpmkCode = cpmkCode
        self.code = code
        self.name = name
        self.gradePercent = gradePercent
        self.assessmentIndicator = []
        
        self.setAssessmentIndicator()
    
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
        cursor.execute('SELECT subCpmkCode, subCpmkDesc, gradePercent FROM subcpmk WHERE subjectCode = "%s" AND cpmkCode = "%s"' % (self.subjectCode, self.code))
        result = cursor.fetchall()
        conn.close()

        for entry in result:
            subCpmk = SubCpmk(self.subjectCode, self.code, entry[0], entry[1], entry[2])
            self.subCpmk.append(subCpmk)
        
    def setNameAndGradePercent(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT CPMKDesc, gradePercent FROM cpmk WHERE subjectCode = "%s" AND cpmkCode = "%s"' % (self.subjectCode, self.code))
        result = cursor.fetchone()
        conn.close()

        self.name = result[0]
        self.gradePercent = result[1]

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
        self.subjectCode = subjectCode
        self.cpmkCode = cpmkCode
        self.subCpmkCode = subCpmkCode
        self.code = code
        self.nim = nim
        self.nip = nip
        self.subCpmkGradePercent = 0
        self.year = year
        self.grade = 0

        self.setGradePercent()
        self.setGrade()
    
    def setGradePercent(self):
        subject = Subject(self.subjectCode)
        for c in subject.cpmk:
            if (c.code == self.cpmkCode):
                for s in c.subCpmk:
                    if (s.code == self.subCpmkCode): 
                        for i in s.assessmentIndicator:
                            if (i.code == self.code):
                                self.subCpmkGradePercent = i.gradePercent


    def setGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT grade FROM indikatorpenilaiangrade WHERE subjectCode = "%s" AND cpmkCode = "%s" AND subCpmkCode = "%s" AND indikatorPenilaianCode = "%s" AND NIM = "%s" AND NIP = "%s" AND YEAR(date) = %s' % (self.subjectCode, self.cpmkCode, self.subCpmkCode, self.code, self.nim, self.nip, self.year))
        self.grade = cursor.fetchone()[0]
        conn.close()

class SubCpmkGrade:
    def __init__(self, subjectCode, cpmkCode, code, nim, nip, year):
        self.subjectCode = subjectCode
        self.cpmkCode = cpmkCode
        self.code = code
        self.nim = nim
        self.nip = nip
        self.cpmkGradePercent = 0
        self.year = year
        self.grade = 0

        self.setGradePercent()
        self.setGrade()
    
    def setGradePercent(self):
        subject = Subject(self.subjectCode)
        for c in subject.cpmk:
            if (c.code == self.cpmkCode):
                for s in c.subCpmk:
                    if (s.code == self.code):
                        self.cpmkGradePercent = s.gradePercent
                            

    def setGrade(self):
        assIndGrade = []
        subject = Subject(self.subjectCode)
        for c in subject.cpmk:
            if (c.code == self.cpmkCode):
                for s in c.subCpmk:
                    if (s.code == self.code):
                        for i in s.assessmentIndicator:
                            indGrade = AssessmentIndicatorGrade(subject.code, c.code, s.code, i.code, self.nim, self.nip, self.year)
                            gradeAndPercent = [indGrade.subCpmkGradePercent, indGrade.grade]
                            assIndGrade.append(gradeAndPercent)
        
        for g in assIndGrade:
            self.grade += g[1]*g[0]/100
    
    def inputGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO subcpmkgrade (subCpmkCode, cpmkCode, subjectCode, NIM, NIP, grade) VALUES ("%s", "%s", "%s", "%s", "%s", %s)' % (self.code, self.cpmkCode, self.subjectCode, self.nim, self.nip, self.grade))
        conn.commit()
        conn.close()
    
class CpmkGrade:
    def __init__(self, subjectCode, code, nim, nip, year):
        self.subjectCode = subjectCode
        self.subject = Subject(self.subjectCode)
        self.code = code
        self.nim = nim
        self.nip = nip
        self.year = year
        self.subjectGradePercent = 0
        self.subCpmkGrades = []
        self.grade = 0

        self.setSubCpmkGrades()
        self.setGradePercent()
        self.setGrade()

    def setSubCpmkGrades(self):
        subject = Subject(self.subjectCode)
        for c in subject.cpmk:
            if (c.code == self.code):
                for s in c.subCpmk:
                    subCpmk = SubCpmkGrade(subject.code, c.code, s.code, self.nim, self.nip, self.year)
                    self.subCpmkGrades.append(subCpmk)
    
    def setGradePercent(self):
        subject = Subject(self.subjectCode)
        for c in subject.cpmk:
            if (c.code == self.code):
                self.subjectGradePercent = c.gradePercent

    def setGrade(self):
        for s in self.subCpmkGrades:
            self.grade += s.grade*s.cpmkGradePercent/100
    
class FinalExamGrade:
    def __init__(self, subjectCode, nim, nip, year):
        self.subjectCode = subjectCode
        self.nim = nim
        self.nip = nip
        self.year = year
        self.grade = 0
        
    
    def setGrade(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT grade FROM finalexamgrade WHERE subjectCode = "%s" AND NIM = "%s" AND NIP = "%s" AND YEAR(date) = %s' % (self.subjectCode, self.nim, self.nip, self.year))
        self.grade = cursor.fetchone()[0]
        conn.close()

class SubjectGrade:
    def __init__(self, subjectCode, nim, nip, year):
        self.subjectCode = subjectCode
        self.subject = Subject(self.subjectCode)
        self.cpmkGrades= []
        self.nim = nim
        self.nip = nip
        self.year = year
        self.grade = 0

        self.setCpmkGrades()
        self.setGrade()

    def setCpmkGrades(self):
        for c in self.subject.cpmk:
            cpmkGrade = CpmkGrade(self.subject.code, c.code, self.nim, self.nip, self.year)
            self.cpmkGrades.append(cpmkGrade)

    def setGrade(self):
        finalExamGrade = FinalExamGrade(self.subjectCode, self.nim, self.nip, self.year)
        finalExamGradePercent = 100
        
        for g in self.cpmkGrades:
            self.grade += g.grade*g.subjectGradePercent/100
            finalExamGradePercent -= g.subjectGradePercent
        
        self.grade += finalExamGrade.grade*finalExamGradePercent/100
    
    def getCpmkGrade(self, cpmkCode):
        for c in self.cpmkGrades:
            if (c.code == cpmkCode):
                return c

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