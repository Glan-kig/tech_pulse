from django.views.generic.base import RedirectView
from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from . import views
from news.sitemaps import (
    ArticleSitemap,
)

sitemaps = {
    "articles": ArticleSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('favorite/add/<int:article_id>/', views.add_favorite, name='add_favorite'),# URL pour ajouter un article aux favoris
    path('favoris/remove/<int:article_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.my_favorites, name='my_favorites'), # URL pour afficher les favoris de l'utilisateur
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('comment/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.png')),
    path(
        "googlee536a5e64b4fa2b6.html",
        TemplateView.as_view(
            template_name="googlee536a5e64b4fa2b6.html",
            content_type="text/html",
        ),
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]