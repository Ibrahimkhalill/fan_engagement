from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.news_list_create, name='news-list-create'),
    path('news/<int:pk>/', views.news_detail, name='news-detail'),
  
]