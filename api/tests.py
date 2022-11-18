from django.urls import reverse
from rest_framework.test import APITestCase
import json 

class QueryAddStudent(APITestCase):
    def test_addStudent_success(self):
        url = reverse('AddStudent')
        dataTest = {'fullName': 'Test','course': '0','group': 'Test'}
        response = self.client.post(url, dataTest, format='json')
        # т.к в ответе у нас id и он всегда новый, то удаляем id из ответа и проверям ответ
        response.data.pop('id')
        self.assertEqual(response.data, {'fullName': 'Test','course': 0,'group': 'Test'})
    def test_addStudent_error(self):
        url = reverse('AddStudent')
        dataTest = {'fullName': 'Test','course': 'fefefef','group': 'Test'}
        response = self.client.post(url, dataTest, format='json')
        self.assertEqual(response.data, {'error': 'Ошибка вводе параметра'})

class QueryGetStudent(APITestCase):
    def test_queryGetStudent_success(self):
        response = self.client.get('/api/getStudent?course=2&fullName=Артем Иванов Иванович')
        self.assertEqual(json.loads(response.content), [
            {
                "id": 4,
                "fullName": "Артем Иванов Иванович",
                "course": 2,
                "group": "ИНБО-11-20"
            }
        ])
    def test_queryGetStudent_error(self):
        response = self.client.get('/api/getStudent?course=&fullName=-')
        self.assertEqual(json.loads(response.content), {
            "error": "Ошибка вводе параметра"
        })

class AddPracticalWork(APITestCase):
    def test_addPracticalWork_success(self):
        url = reverse('AddPracticalWork')
        dataTest = {'title': 'Работа тестовая test','subject': 'Теsr'}
        response = self.client.post(url, dataTest, format='json')
        # т.к в ответе у нас id и он всегда новый, то удаляем id из ответа и проверям ответ
        response.data.pop('id')
        self.assertEqual(response.data, {
            "title": "Работа тестовая test",
            "subject": "Теsr"
        })
    def test_addPracticalWork_error(self):
        url = reverse('AddPracticalWork')
        dataTest = {'title': 'Работа тестовая test!!!!!!','subject': 'Теsr'}
        response = self.client.post(url, dataTest, format='json')
        self.assertEqual(response.data, {
            "error": "Ошибка вводе параметра"
        })

class GetPracticalWork(APITestCase):
    def test_getPracticalWork_success(self):
        response = self.client.get('/api/getPracticalWork?title=Работа 1&subject=')
        self.assertEqual(json.loads(response.content), [
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
    def test_getPracticalWork_error(self):
        response = self.client.get('/api/getPracticalWork?title=Работа !!!!1&subject=')
        self.assertEqual(json.loads(response.content), {
            "error": "Ошибка вводе параметра"
        })

class AddCompletedWork(APITestCase):
    def test_addCompletedWork_success(self):
        url = reverse('AddCompletedWork')
        dataTest = {'idStudent': '6','idPracticalWork': '6'}
        response = self.client.post(url, dataTest, format='json')
        # т.к в ответе у нас id и он всегда новый, то удаляем id из ответа и проверям ответ
        response.data.pop('id')
        self.assertEqual(response.data, {
            "idStudent": 6,
            "idPracticalWork": 6
        })
    def test_addCompletedWork_error(self):
        url = reverse('AddCompletedWork')
        dataTest = {'idStudent': '6DFGHJM,','idPracticalWork': '6'}
        response = self.client.post(url, dataTest, format='json')
        self.assertEqual(response.data, {
            "error": "Ошибка вводе параметра"
        })

class GetCompletedWork(APITestCase):
    def test_getCompletedWork_success(self):
        response = self.client.get('/api/getCompletedWork?idStudent=5')
        self.assertEqual(json.loads(response.content), [
            {
                "date": "2022-11-01",
                "fullName": "Кирилл Иванов Владимирович",
                "course": 3,
                "group": "ИНБО-10-20",
                "subject": "ЦТ",
                "title": "Работа 1"
            }
        ])
    def test_getCompletedWork_error(self):
        response = self.client.get('/api/getCompletedWork?idStudent=5G')
        self.assertEqual(json.loads(response.content), {
            "error": "Ошибка вводе параметра"
        })