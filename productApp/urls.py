from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('/getAllProduct', views.getAllProduct),
    # path('/getCategory', views.getCategory),
    path('/getOptionsFilter', views.getOptionsFilter),
]
