from django.db import models


class Student(models.Model):
    fullName = models.TextField()
    course = models.IntegerField()
    group = models.TextField()

class PracticalWork(models.Model):
    title = models.TextField()
    subject = models.TextField()

class CompletedWork(models.Model):
    idStudent = models.IntegerField()
    idPracticalWork = models.IntegerField()
    date = models.DateField(auto_now=True)