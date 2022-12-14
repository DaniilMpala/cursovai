# from .models import *
# from django.db import connection
import pysqlite3
from datetime import datetime
import django
def addStudent(fullName, course, group):
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row
    cur = con.cursor()
    print(pysqlite3.sqlite_version, django.VERSION)
    cur.execute('INSERT INTO student ("fullName", "course", "group") VALUES (?,?,?) RETURNING *',(fullName, course, group))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)

def getStudent(fullName, course, group):
    print(fullName, course, group)
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row 
    cur = con.cursor()

    cur.execute('''SELECT * FROM student WHERE "fullName" LIKE ? AND "course" LIKE ? AND "group" LIKE ? ''',(f"%{fullName}%", f"%{course}%", f"%{group}%"))
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]
    print(row)
    return row

def addCompletedWork(idStudent, idPracticalWork):
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row
    cur = con.cursor()

# ругается без запятой в конце
    cur.execute('SELECT fullName FROM student WHERE id = ?', (idStudent,))
    code, = cur.fetchone() or (None,)
    if code is None:
        return {'error':'Такого студента не существует'}

    cur.execute('SELECT title FROM practicalwork WHERE id = ?', (idPracticalWork,))
    code, = cur.fetchone() or (None,)
    if code is None:
        return {'error':'Такой работы существует'}

    cur.execute('INSERT INTO completedwork ("idStudent", "idPracticalWork", "date") VALUES (?,?,?) RETURNING *',(idStudent, idPracticalWork, datetime.now()))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)


def getCompletedWork(idStudent):
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row 
    cur = con.cursor()

    cur.execute(f"""
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
        {f"WHERE idStudent = {int(idStudent)}" if int(idStudent) > 0 else ""}    
        
    """)
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]

    return row

def addPracticalWork(title, subject):
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row
    cur = con.cursor()

    cur.execute('INSERT INTO practicalwork ("title", "subject") VALUES (?,?) RETURNING *',(title, subject))
    row = cur.fetchone()

    cur.close()
    con.commit()

    return dict(row)

def getPracticalWork(title, subject):
    con = pysqlite3.connect("db.sqlite3")#представляет собой соединение с базой данных на диске.
    con.row_factory = pysqlite3.Row 
    cur = con.cursor()

    cur.execute('''SELECT * FROM practicalwork WHERE "title" LIKE ? AND "subject" LIKE ?''',(f"%{title}%", f"%{subject}%"))
    row = cur.fetchall()

    cur.close()
    con.commit()

    row = [dict(twmpRow) for twmpRow in row]

    return row