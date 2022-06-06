from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('/getAllProduct', views.getAllProduct),
    path('/getChoiceBuyers', views.getChoiceBuyers),
    path('/getOptionsFilter', views.getOptionsFilter),
    path('/updateDemandItem', views.updateDemandItem),

    path('/makeFavorite', views.makeFavorite),
]
