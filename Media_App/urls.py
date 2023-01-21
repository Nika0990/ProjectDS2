from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('query_results', views.query_results, name='query_results'),
    path('rankings', views.rankings, name='rankings'),
    path('records_management', views.records_management, name='records_management')
]