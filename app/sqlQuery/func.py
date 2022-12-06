# from .models import *
# from django.db import connection
import sqlite3
from datetime import datetime

def addStudent(fullName, course, group):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('INSERT INTO student ("fullName", "course", "group") VALUES (?,?,?) RETURNING *',(fullName, course, group))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)

def getStudent(fullName, course, group):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row 
    cur = con.cursor()

    cur.execute('''SELECT * FROM student WHERE "fullName" LIKE ? AND "course" LIKE ? AND "group" LIKE ? ''',(f"%{fullName}%", f"%{course}%", f"%{group}%"))
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]

    return row

def addCompletedWork(idStudent, idPracticalWork):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('INSERT INTO completedwork ("idStudent", "idPracticalWork", "date") VALUES (?,?,?) RETURNING *',(idStudent, idPracticalWork, datetime.now()))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)


def getCompletedWork(idStudent):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row 
    cur = con.cursor()

    cur.execute('''
        SELECT
            date,
            fullName,
            course,
            "group",
            subject,
            title
        FROM completedwork
        LEFT JOIN practicalwork ON practicalwork.id = completedwork.idPracticalWork      
        LEFT JOIN student ON student.id = completedwork.idStudent      
        WHERE idStudent = ?
    ''',(idStudent))
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]

    return row

def addPracticalWork(title, subject):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cur.execute('INSERT INTO practicalwork ("title", "subject") VALUES (?,?) RETURNING *',(title, subject))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)

def getPracticalWork(title, subject):
    con = sqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = sqlite3.Row 
    cur = con.cursor()

    cur.execute('''SELECT * FROM practicalwork WHERE "title" LIKE ? AND "subject" LIKE ?''',(f"%{title}%", f"%{subject}%"))
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]

    return row