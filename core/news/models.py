from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Article(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(hours=24)

    def __str__(self):
        return self.title

class Source(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sources')
    site_name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return f"{self.site_name} - {self.article.title}"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Assure qu'un utilisateur ne peut pas ajouter le même article plusieurs fois à ses favoris
        unique_together = ('user', 'article')

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Le plus récent en premier

    def __str__(self):
        return f"Commentaire de {self.author.username} sur {self.article.title}"
    
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment') # on ne peux liker qu'une fois

