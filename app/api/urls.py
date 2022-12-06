from FunctionalSqlite import views
from django.contrib import admin
from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('addStudent', views.queryAddStudent, name="AddStudent"),
    path('getStudent', views.queryGetStudent, name="GetStudent"),
    path('addPracticalWork', views.queryAddPracticalWork, name="AddPracticalWork"),
    path('getPracticalWork', views.queryGetPracticalWork, name="GetPracticalWork"),
    path('addCompletedWork', views.queryAddCompletedWork, name="AddCompletedWork"),
    path('getCompletedWork', views.queryGetCompletedWork, name="GetCompletedWork"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
        )
]
