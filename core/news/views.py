from django.shortcuts import render
from .models import Article

def home(request):
    # On recupère tous les articles, triés par date de création décroissante, et on précharge les sources associées pour éviter les requêtes supplémentaires
    articles = Article.objects.all().order_by('-created_at').prefetch_related('sources')
    return render(request, 'news/home.html', {'articles': articles})
