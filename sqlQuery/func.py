from .models import *
from django.db import connection

def addStudent(fullName, course, group):
    student = Student(fullName=fullName, course=course, group=group)
    student.save()
    return student

def getStudent(fullName, course, group):
    try:
        student = Student.objects.filter( fullName__icontains=fullName) & Student.objects.filter( course__icontains=course) & Student.objects.filter( group__icontains=group)
    except Student.DoesNotExist:
        student = None
    return student

def addCompletedWork(idStudent, idPracticalWork):
    work = CompletedWork(idStudent=idStudent,idPracticalWork=idPracticalWork )
    work.save()
    return work

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def getCompletedWork(idStudent):
    cur = connection.cursor()
    cur.execute(f'''
    SELECT
        date,
        fullName,
        course,
        "group",
        subject,
        title
    FROM sqlQuery_completedwork
    LEFT JOIN sqlQuery_practicalwork ON sqlQuery_practicalwork.id = sqlQuery_completedwork.idPracticalWork      
	LEFT JOIN sqlQuery_student ON sqlQuery_student.id = sqlQuery_completedwork.idStudent      
    WHERE idStudent = {idStudent}
    ''')
    works = dictfetchall(cur)
    print(works)
    return works

def addPracticalWork(title, subject):
    work = PracticalWork(title=title,subject=subject )
    work.save()
    return work

def getPracticalWork(title, subject):
    try:
        works = PracticalWork.objects.filter( title__icontains=title) & PracticalWork.objects.filter( subject__icontains=subject)
    except PracticalWork.DoesNotExist:
        works = None
    return works