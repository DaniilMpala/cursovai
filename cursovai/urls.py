from FunctionalSqlite import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('FunctionalSqlite/', include('FunctionalSqlite.urls')),
    path('api/', include('api.urls'))
]
