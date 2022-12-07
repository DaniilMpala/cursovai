from django.urls import path, include
from . import views

urlpatterns = [
    path('getStudent', views.queryGetStudent)
]
