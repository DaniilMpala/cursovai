from django.test import TestCase
from .func import *

class TestAddStudent(TestCase):
    def test(self):
        res = addStudent("TestFunc", 0, 'ТЕСТ-0-0')
        res.pop('id')
        self.assertEqual(res, {'course': 0, 'fullName': 'TestFunc', 'group': 'ТЕСТ-0-0'})

class TestGetStudent(TestCase):
    def test(self):
        res = getStudent("TestFunc", 0, 'ТЕСТ-0-0')
        self.assertEqual(res[0], {
        "id": 69,
        "fullName": "TestFunc",
        "course": 0,
        "group": "ТЕСТ-0-0"
    })

class TestAddCompletedWork(TestCase):
    def test(self):
        res = addCompletedWork(6,6)
        res.pop('id')
        res.pop('date')
        self.assertEqual(res, {
            "idStudent": 6,
            "idPracticalWork": 6
        })

class TestGetCompletedWork(TestCase):
    def test(self):
        res = getCompletedWork("5")
        self.assertEqual(res[0], {
            "date": "2022-11-01",
            "fullName": "Кирилл Иванов Владимирович",
            "course": 3,
            "group": "ИНБО-10-20",
            "subject": "ЦТ",
            "title": "Работа 1"
        })

class TestAddPracticalWork(TestCase):
    def test(self):
        res = addPracticalWork("Работа тестовая test","Теsr")
        res.pop('id')
        self.assertEqual(res, {
            "title": "Работа тестовая test",
            "subject": "Теsr"
        })

class TestGetPracticalWork(TestCase):
    def test(self):
        res = getPracticalWork("Работа 1", '')
        self.assertEqual(res,  [
            {
                "id": 1,
                "title": "Работа 1",
                "subject": "ЦТ"
            },
            {
                "id": 3,
                "title": "Работа 1",
                "subject": "ИТ"
            }
        ])