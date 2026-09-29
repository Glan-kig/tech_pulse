from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ArticleViewSet, CategoryViewSet, 
    CommentViewSet, FavoriteViewSet,
    ContactCreateView
)

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'favorites', FavoriteViewSet, basename='favorite')


urlpatterns = [
    path('', include(router.urls)),
    path('contact/', ContactCreateView.as_view(), name='api_contact'),
]