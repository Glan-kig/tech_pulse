from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.conf import settings
from .models import Article, Category, Favorite, Comment, CommentLike
from .forms import CommentForm, MyPasswordChangeForm, CustomRegisterForm, ContactForm
import threading

def home(request):
    query = request.GET.get('q') # Récupération de la requête de recherche depuis les paramètres de la requête
    category_id = request.GET.get('category') # Récupération de l'ID de la catégorie depuis les paramètres de la requête

    # On recupère tous les articles, triés par date de création décroissante, et on précharge les sources associées pour éviter les requêtes supplémentaires
    article_liste = Article.objects.all().order_by('-created_at').prefetch_related('sources')

    recent_comments = Comment.objects.all().order_by('-created_at')[:5]

    # Filtrage par recherche si une requête est présente
    if query:
        article_liste = article_liste.filter(Q(title__icontains=query) | Q(summary__icontains=query))
    
    # Filtrage par catégorie si une catégorie est sélectionnée
    if category_id:
        article_liste = article_liste.filter(category_id=category_id)

    # Logique de pagination
    paginator = Paginator(article_liste, 10) # 10 article par page
    page_number = request.GET.get('page') # On recupere le numero de la page dams l'url
    page_obj = paginator.get_page(page_number)

    # Récupération de toutes les catégories pour les afficher dans le menu de filtrage
    categories = Category.objects.all()

    if request.user.is_authenticated:
        favorite_ids = set(
            Favorite.objects.filter(user=request.user)
            .values_list('article_id', flat=True)
        )

        for article in page_obj:
            article.is_favorited = article.id in favorite_ids
    else:
        for article in page_obj:
            article.is_favorited = False

    # --- LOGIQUE DU FORMULAIRE DE CONTACT ---
    if request.method == 'POST' and 'contact_submit' in request.POST:
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            user_name = contact_form.cleaned_data['name']
            user_email = contact_form.cleaned_data['email']
            user_subject = contact_form.cleaned_data['subject']
            user_message = contact_form.cleaned_data['message']
            
            # 1. Sujet de l'e-mail dans ta boîte de réception
            email_subject = f"[TechPulse Terminal] {user_subject}"
            
            # 2. Message de secours en texte brut (obligatoire pour Django)
            email_body_brut = f"Nouveau message de {user_name} ({user_email}):\n\n{user_message}"
            
            # 3. Ton interface de rapport système premium
            html_message = f"""
            <div style="background-color: #0b0e14; padding: 35px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #11151c; border: 1px solid #222936; border-radius: 12px; overflow: hidden;">
                    
                    <tr>
                        <td style="padding: 30px 35px; border-bottom: 1px solid #1f2633; background-color: #0e1219;">
                            <span style="font-family: 'Courier New', Courier, monospace; color: #f59e0b; font-weight: bold; font-size: 13px; letter-spacing: 1px; display: block; margin-bottom: 5px;">
                                [!] INCOMING_TRANSMISSION_RECEIVED
                            </span>
                            <h1 style="color: #ffffff; font-size: 20px; font-weight: 700; margin: 0;">Alerte Contact Client</h1>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 25px 35px 15px 35px;">
                            <table width="100%" style="background-color: #161c26; border-radius: 6px; padding: 15px;">
                                <tr>
                                    <td style="color: #94a3b8; font-size: 13px; padding-bottom: 5px;"><strong>Expéditeur :</strong> {user_name}</td>
                                </tr>
                                <tr>
                                    <td style="color: #94a3b8; font-size: 13px;"><strong>Adresse e-mail :</strong> <a href="mailto:{user_email}" style="color: #0ea5e9; text-decoration: none;">{user_email}</a></td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 10px 35px 35px 35px;">
                            <h3 style="color: #ffffff; font-size: 15px; margin-top: 0; margin-bottom: 10px; border-bottom: 1px solid #1f2633; padding-bottom: 8px;">
                                Objet : {user_subject}
                            </h3>
                            <p style="color: #e2e8f0; font-size: 14px; line-height: 1.6; white-space: pre-line; background-color: rgba(255,255,255,0.02); padding: 15px; border-radius: 6px; border-left: 3px solid #0ea5e9; margin: 0;">
                                {user_message}
                            </p>
                        </td>
                    </tr>
                    
                    <tr>
                        <td style="padding: 20px 35px; border-top: 1px solid #1f2633; background-color: #0e1219; text-align: center;">
                            <p style="font-size: 11px; font-family: 'Courier New', Courier, monospace; color: #475569; margin: 0; text-transform: uppercase;">
                                TechPulse Admin Core v1.0
                            </p>
                        </td>
                    </tr>
                </table>
            </div>
            """
            
            def _execute_email_send():
                try:
                    send_mail(
                        email_subject,
                        email_body_brut,
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.EMAIL_HOST_USER], # C'est envoyé vers TA propre adresse
                        html_message=html_message,
                        fail_silently=False,
                    )
                
                except Exception as e:
                    messages.error(request, f"Échec de l'envoi du message : {e}")
            messages.success(request, "Transmission réussie ! Votre message a bien été injecté dans le terminal de l'administrateur.")
            threading.Thread(target=_execute_email_send).start()
            return redirect('home')
    else:
        contact_form = ContactForm()

    content = {
        'page_obj' : page_obj,
        'categories': categories,
        'recent_comments' : recent_comments,
        'contact_form': contact_form,
    }

    return render(request, 'news/home.html', content)

def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Connecte automatiquement l'utilisateur après l'inscription
            return redirect('home') # Redirige vers la page d'accueil après l'inscription
    else:
        form = CustomRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def add_favorite(request, article_id):
    article = Article.objects.get(id=article_id)

    # Ajoute l'article aux favoris de l'utilisateur, en évitant les doublons grâce à get_or_create
    Favorite.objects.get_or_create(user=request.user, article=article)

    next_url = request.META.get('HTTP_REFERER', 'home')
    messages.success(request, f"L'article '{article.title}' a été ajouté à vos favoris.")

    if next_url:
        return HttpResponseRedirect(next_url)
    return redirect('home')

@login_required
def remove_from_favorites(request, article_id):
    favorite = get_object_or_404(Favorite, user=request.user, article_id=article_id)
    favorite.delete()
    messages.success(request, f"L'article '{favorite.article.title}' a été retiré de vos favoris.")
    next_url = request.META.get('HTTP_REFERER', 'home')

    if next_url:
        return HttpResponseRedirect(next_url)
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

    if request.user.is_authenticated:
        liked_comment_ids = CommentLike.objects.filter(
            user=request.user,
            comment__article=article
        ).values_list('comment_id', flat=True)

        for comment in comments:
            comment.is_liked = comment.id in liked_comment_ids

        has_commented = comments.filter(author=request.user).exists()
    else:
        for comment in comments:
            comment.is_liked = False

        has_commented = False
    
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
        'form': form,
        'has_commented': has_commented,
    })

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    article_pk = comment.article.pk

    if comment.author == request.user or request.user.is_staff: # Seul l'auteur du commentaire ou un admin peut le supprimer
        comment.delete()
        messages.success(request, "Votre commentaire a été supprimé avec succès.")
    else:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce commentaire.")

    return redirect('article_detail', pk=article_pk)

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id = comment_id)
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)

    if not created:
        like.delete()

    return redirect('article_detail', pk=comment.article.pk)

@login_required # Seuls les connectés peuvent changer leur mot de passe
def change_password(request):
    if request.method == 'POST':
        form = MyPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # IMPORTANT : évite de déconnecter l'utilisateur après le changement
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès !')
            return redirect('profile') # Ou l'URL de ton choix
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = MyPasswordChangeForm(request.user)
    
    return render(request, 'news/change_password.html', {'form': form})