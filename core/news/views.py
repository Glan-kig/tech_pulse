from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from .models import Article, Category, Favorite, Comment
from .forms import CommentForm

def home(request):
    query = request.GET.get('q') # Récupération de la requête de recherche depuis les paramètres de la requête
    category_id = request.GET.get('category') # Récupération de l'ID de la catégorie depuis les paramètres de la requête

    # On recupère tous les articles, triés par date de création décroissante, et on précharge les sources associées pour éviter les requêtes supplémentaires
    articles = Article.objects.all().order_by('-created_at').prefetch_related('sources')

    recent_comments = Comment.objects.all().order_by('-created_at')[:5]

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
        'recent_comments' : recent_comments,
    }

    return render(request, 'news/home.html', content)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connecte automatiquement l'utilisateur après l'inscription
            return redirect('home') # Redirige vers la page d'accueil après l'inscription
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_favorite(request, article_id):
    article = Article.objects.get(id=article_id)

    # Ajoute l'article aux favoris de l'utilisateur, en évitant les doublons grâce à get_or_create
    Favorite.objects.get_or_create(user=request.user, article=article)

    return redirect('home')

@login_required
def my_favorites(request):
    # Récupère les articles favoris de l'utilisateur connecté, triés par date d'ajout décroissante
    user_favorites = Favorite.objects.filter(user=request.user).order_by('-added_at').select_related('article')

    return render(request, 'news/favorites.html', {'favorites': user_favorites})

@login_required
def profile(request):
    fav_count = Favorite.objects.filter(user=request.user).count()
    recent_fav = Favorite.objects.filter(user=request.user).order_by('-added_at')[:5]

    content = {
        'fav_count' : fav_count,
        'recent_fav' : recent_fav,
    }

    return render(request, 'news/profile.html', content)

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all().order_by('-created_at')
    
    if request.method == 'POST':
        # On vérifie d'abord que l'utilisateur est bien connecté
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                # 1. On crée l'objet en mémoire sans l'enregistrer en BDD
                comment = form.save(commit=False)
                
                # 2. On remplit MANUELLEMENT les champs manquants
                comment.article = article
                comment.author = request.user  # C'est cette ligne qui corrige ton erreur !
                
                # 3. Maintenant on peut sauvegarder pour de vrai
                comment.save()
                
                return redirect('article_detail', pk=article.pk)
        else:
            # Si un malin bypass le template, on le renvoie vers le login
            return redirect('login')
    else:
        form = CommentForm()
        
    return render(request, 'news/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form
    })