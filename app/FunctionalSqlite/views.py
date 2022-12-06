from django.shortcuts import render
from django.http import HttpResponse
from sqlQuery.func import *

def queryGetStudent(request):
    fullName = request.GET.get("fullName")
    course = request.GET.get("course")
    group = request.GET.get("group")

    student =  getStudent(fullName,course,group)
 
    return HttpResponse((f"ID: {st.id} | ФИО: {st.fullName}, Курс: {st.course}, Группа: {st.group}<br>" for st in student) if len(student) else f"Студент не найден в базе")