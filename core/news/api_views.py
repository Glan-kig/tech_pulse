from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_q.tasks import async_task
from django.db.models import Q
from .models import (
    Article, Category, Comment, 
    Favorite, CommentLike, Contact
)
from .serializers import (
    ArticleSerializer, CategorySerializer, 
    CommentSerializer, FavoriteSerializer,
    ContactSerializer
)
from .tasks import send_contact_email_task

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class StandardPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100
    

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.AllowAny]

    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = Article.objects.all().order_by('-created_at').prefetch_related('sources')
        query = self.request.query_params.get('q')
        category_id = self.request.query_params.get('category')

        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(summary__icontains=query))
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        article = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, article=article)
        if not created:
            favorite.delete()
            return Response({'status': 'unfavorited'}, status=status.HTTP_200_OK)
        return Response({'status': 'favorited'}, status=status.HTTP_201_CREATED)



class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            like.delete()
            return Response({'status': 'unliked', 'likes_count': comment.likes.count()}, status=status.HTTP_200_OK)
        return Response({'status': 'liked', 'likes_count': comment.likes.count()}, status=status.HTTP_201_CREATED)


class FavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('article').order_by('-added_at')


class ContactCreateView(generics.CreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        contact = serializer.save()
        async_task(send_contact_email_task, contact.id)