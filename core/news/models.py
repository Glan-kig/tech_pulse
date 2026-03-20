from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
class Article(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Source(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sources')
    site_name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return f"{self.site_name} - {self.article.title}"