from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('favorite/add/<int:article_id>/', views.add_favorite, name='add_favorite'),# URL pour ajouter un article aux favoris
    path('favorites/', views.my_favorites, name='my_favorites'), # URL pour afficher les favoris de l'utilisateur
    path('profile/', views.profile, name='profile'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
]