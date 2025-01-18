from django.urls import path
from . import views

urlpatterns = [
    path('search_companies/', views.search_companies, name='search_companies'),
]