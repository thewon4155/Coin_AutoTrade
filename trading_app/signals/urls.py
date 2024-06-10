from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('chart-data/', views.chart_data, name='chart_data'),
]
