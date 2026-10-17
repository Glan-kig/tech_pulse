# Documentation de l'API Tech Pulse

Base URL (dev) : `http://127.0.0.1:8000`

## Authentification

- JWT (`Authorization: Bearer <access_token>`) ou session Django.
- Permission par défaut : lecture publique, écriture authentifiée.

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtenir `access` et `refresh` (body : `username`, `password`) |
| POST | `/api/token/refresh/` | Renouveler l'access token (body : `refresh`) |
| POST | `/api/auth/login/` | Connexion (dj-rest-auth) |
| POST | `/api/auth/logout/` | Déconnexion |
| POST | `/api/auth/password/change/` | Changer le mot de passe |
| GET/PUT/PATCH | `/api/auth/user/` | Profil de l'utilisateur connecté |
| POST | `/api/auth/registration/` | Inscription |
| POST | `/api/auth/google/` | Connexion Google (body : `access_token` ou `code`) |

Exemple :

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret"}'
```

## Pagination

Les listes sont paginées : `?page=<n>`. Réponse :

```json
{ "count": 42, "next": "...?page=2", "previous": null, "results": [] }
```

Pour les articles : `?page_size=<n>` (défaut 6, max 100). Les autres listes utilisent `PAGE_SIZE = 10`.

## Catégories (lecture seule, public)

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/categories/` | Liste des catégories |
| GET | `/api/categories/{id}/` | Détail d'une catégorie |

```json
{ "id": 1, "name": "IA" }
```

## Articles (lecture seule, public)

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/articles/` | Non | Liste paginée, du plus récent au plus ancien |
| GET | `/api/articles/{id}/` | Non | Détail d'un article |
| POST | `/api/articles/{id}/favorite/` | Oui | Ajoute ou retire l'article des favoris (bascule) |

Paramètres de `GET /api/articles/` :

| Paramètre | Description |
|---|---|
| `q` | Recherche dans le titre et le résumé |
| `category` | Filtre par id de catégorie |
| `page`, `page_size` | Pagination |

Objet article :

```json
{
  "id": 1,
  "title": "...",
  "summary": "...",
  "ai_summary": "...",
  "image_url": "https://...",
  "slug": "...",
  "created_at": "2026-10-17T14:26:12Z",
  "is_new": true,
  "category": { "id": 1, "name": "IA" },
  "sources": [{ "id": 1, "site_name": "...", "url": "https://..." }],
  "is_favorited": false
}
```

Réponses de `favorite` : `201 {"status": "favorited"}` ou `200 {"status": "unfavorited"}`.

## Commentaires

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/comments/` | Non | Liste des commentaires |
| POST | `/api/comments/` | Oui | Créer un commentaire (auteur = utilisateur connecté) |
| GET | `/api/comments/{id}/` | Non | Détail |
| PUT/PATCH | `/api/comments/{id}/` | Oui | Modifier |
| DELETE | `/api/comments/{id}/` | Oui | Supprimer |
| POST | `/api/comments/{id}/like/` | Oui | Ajoute ou retire un like (bascule) |

Création :

```json
{ "article": 1, "content": "Super article" }
```

Objet commentaire :

```json
{
  "id": 1,
  "article": 1,
  "author": "alice",
  "content": "Super article",
  "created_at": "2026-10-17T14:30:00Z",
  "likes_count": 0,
  "is_liked": false
}
```

Réponses de `like` : `201 {"status": "liked", "likes_count": n}` ou `200 {"status": "unliked", "likes_count": n}`.

## Favoris (lecture seule, authentifié)

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/favorites/` | Favoris de l'utilisateur connecté |
| GET | `/api/favorites/{id}/` | Détail d'un favori |

```json
{ "id": 1, "article": { "...": "objet article" }, "added_at": "2026-10-17T14:35:00Z" }
```

## Contact (public)

| Méthode | Endpoint | Description |
|---|---|---|
| POST | `/api/contact/` | Envoie un message ; un email est envoyé en tâche asynchrone |

```json
{ "name": "Alice", "email": "alice@example.com", "subject": "Bonjour", "message": "..." }
```

Réponse `201` : les champs ci-dessus plus `id` et `created_at`.

## Codes d'erreur

| Code | Signification |
|---|---|
| 400 | Données invalides |
| 401 | Authentification requise ou token invalide |
| 403 | Accès refusé |
| 404 | Ressource introuvable |
