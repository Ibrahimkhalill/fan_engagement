from django.urls import path
from . import views

urlpatterns = [
    path('players/', views.player_list_create, name='player-list-create'),
    path('players/<int:pk>/', views.player_detail, name='player-detail'),
  
]