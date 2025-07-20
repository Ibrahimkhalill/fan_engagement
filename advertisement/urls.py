from django.urls import path
from . import views

urlpatterns = [
    path('advertisements/', views.advertisement_list_create, name='advertisement-list-create'),
    path('advertisements/<int:pk>/', views.advertisement_detail, name='advertisement-detail'),
    path('advertisements/latest/', views.advertisement_list_for_user, name='advertisement-latest'),  # New endpoint
]