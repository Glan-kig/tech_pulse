# Diagrammes Tech Pulse

## Séquence : authentification JWT

```mermaid
sequenceDiagram
    actor Client
    participant API as Django REST
    participant DB as Base de données

    Client->>API: POST /api/token/ (username, password)
    API->>DB: Vérifie les identifiants
    alt Identifiants valides
        API-->>Client: 200 {access, refresh}
    else Identifiants invalides
        API-->>Client: 401
    end
    Client->>API: Requête avec Authorization: Bearer access
    API-->>Client: 200 / 401 si expiré
    Client->>API: POST /api/token/refresh/ (refresh)
    API-->>Client: 200 {access}
```

## Séquence : inscription et mail de bienvenue

```mermaid
sequenceDiagram
    actor Utilisateur
    participant Allauth as Allauth / Django
    participant DB as Base de données
    participant Signal as Signal user_signed_up
    participant Q as Django-Q
    participant SMTP as Serveur SMTP

    Utilisateur->>Allauth: Soumet le formulaire d'inscription
    Allauth->>DB: Crée l'utilisateur
    Allauth->>Signal: user_signed_up
    Signal->>Q: async_task(send_welcome_email_task, user.id)
    Allauth-->>Utilisateur: Redirection vers l'accueil
    Q->>DB: Récupère l'utilisateur
    Q->>SMTP: Envoie le mail de bienvenue (si email renseigné)
```

## Séquence : formulaire de contact

```mermaid
sequenceDiagram
    actor Visiteur
    participant API as POST /api/contact/
    participant DB as Base de données
    participant Q as Django-Q
    participant SMTP as Serveur SMTP

    Visiteur->>API: name, email, subject, message
    API->>DB: Enregistre le Contact
    API->>Q: async_task(send_contact_email_task, contact.id)
    API-->>Visiteur: 201 Created
    Q->>DB: Récupère le Contact
    Q->>SMTP: Envoie l'email à EMAIL_HOST_USER
```

## Séquence : favori et like (bascule)

```mermaid
sequenceDiagram
    actor Utilisateur
    participant API as Django REST
    participant DB as Base de données

    Utilisateur->>API: POST /api/articles/{id}/favorite/ (ou /api/comments/{id}/like/)
    alt Non authentifié
        API-->>Utilisateur: 401
    else Authentifié
        API->>DB: get_or_create(user, cible)
        alt Créé
            API-->>Utilisateur: 201 favorited / liked
        else Déjà existant
            API->>DB: delete()
            API-->>Utilisateur: 200 unfavorited / unliked
        end
    end
```

## Séquence : collecte des articles (`scrape_tech`)

```mermaid
sequenceDiagram
    participant Cron as run_scrape.sh / cron
    participant Cmd as scrape_tech
    participant RSS as Flux RSS
    participant Page as Page de l'article
    participant Groq as API Groq
    participant DB as Base de données

    Cron->>Cmd: manage.py scrape_tech
    loop Pour chaque source
        Cmd->>RSS: GET flux (pause de 2 s avant)
        RSS-->>Cmd: XML
        loop 5 premiers éléments
            alt Titre ou description dans la liste noire
                Cmd->>Cmd: Ignoré
            else Titre déjà en base
                Cmd->>DB: Article.exists()
            else Nouvel article
                Cmd->>Cmd: Détermine la catégorie par mots-clés
                opt Aucune image dans le flux
                    Cmd->>Page: GET og:image
                end
                Cmd->>Groq: generate_ai_summary(description)
                Groq-->>Cmd: Résumé (ou texte tronqué en repli)
                Cmd->>DB: Crée Article et Source
            end
        end
    end
```

## Activité : traitement d'un élément de flux

```mermaid
flowchart TD
    A([Élément RSS/Atom]) --> B{Titre ou description dans la liste noire ?}
    B -- Oui --> Z([Ignoré])
    B -- Non --> C{Titre déjà en base ?}
    C -- Oui --> Z
    C -- Non --> D[Déterminer la catégorie par mots-clés]
    D --> E[Nettoyer la description HTML]
    E --> F{Image dans le flux ?}
    F -- Non --> G[Chercher og:image sur la page]
    F -- Oui --> H
    G --> H[Générer le résumé IA]
    H --> I{Résumé obtenu ?}
    I -- Non --> J[Résumé tronqué à 200 caractères]
    I -- Oui --> K
    J --> K[Créer Article et Source]
    K --> L([Fin])
```

## Activité : consultation d'un article et commentaire

```mermaid
flowchart TD
    A([Ouvrir un article]) --> B[Afficher détail, résumé IA et commentaires]
    B --> C{Utilisateur connecté ?}
    C -- Non --> D[Invitation à se connecter] --> E([Fin])
    C -- Oui --> F{Action}
    F -- Favori --> G[Ajouter ou retirer des favoris]
    F -- Commenter --> H[Soumettre le commentaire]
    F -- Liker --> I[Ajouter ou retirer le like]
    G --> E
    H --> E
    I --> E
```
