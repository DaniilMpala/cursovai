from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('/auth', views.loginOrRegistration),
    path('/getDataUserSetting', views.getDataUserSetting),
    path('/changeNotifyUser', views.changeNotifyUser),
    path('/getDataUserFavoriteProducts', views.getDataUserFavoriteProducts),
    path('/saveBasket', views.saveBasket),
    path('/getDataSaveBasket', views.getDataSaveBasket),
    path('/deleteSaveBasket', views.deleteSaveBasket),
]
