from FunctionalSqlite import views
from django.contrib import admin
from django.urls import path, include
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('addStudent', views.queryAddStudent),
    path('getStudent', views.queryGetStudent),
    path('addPracticalWork', views.queryAddPracticalWork),
    path('getPracticalWork', views.queryGetPracticalWork),
    path('addCompletedWork', views.queryAddCompletedWork),
    path('getCompletedWork', views.queryGetCompletedWork),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
        )
]
