from django.shortcuts import render
from django.db.models import Q
from .models import Article, Category

def home(request):
    query = request.GET.get('q') # Récupération de la requête de recherche depuis les paramètres de la requête
    category_id = request.GET.get('category') # Récupération de l'ID de la catégorie depuis les paramètres de la requête
    
    # On recupère tous les articles, triés par date de création décroissante, et on précharge les sources associées pour éviter les requêtes supplémentaires
    articles = Article.objects.all().order_by('-created_at').prefetch_related('sources')

    # Filtrage par recherche si une requête est présente
    if query:
        articles = articles.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    
    # Filtrage par catégorie si une catégorie est sélectionnée
    if category_id:
        articles = articles.filter(category_id=category_id)

    # Récupération de toutes les catégories pour les afficher dans le menu de filtrage
    categories = Category.objects.all()

    content = {
        'articles': articles,
        'categories': categories,
    }

    return render(request, 'news/home.html', content)
