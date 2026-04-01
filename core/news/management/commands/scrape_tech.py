import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from news.models import Article, Category, Source
from news.utils import generate_ai_summary

class Command(BaseCommand):
    help = "Recupere les dernières news de plusieurs sources tech"

    def handle(self, *args, **options):
        # Configuration des sources (Inchangée)
        SOURCE_CONFIG = [
            {"site_name": "Le Monde Informatique", "url": "https://www.lemondeinformatique.fr/flux-rss/thematique/toute-l-actualite/rss.xml"},
            {"site_name": "L'Informatique", "url": "https://www.linformatique.com/rss/actualites.xml"},
            {"site_name": "ZDNet France", "url": "https://www.zdnet.fr/rss.xml"},
            {"site_name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"site_name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"site_name": "Developpez.com", "url": "https://www.developpez.com/index/rss.php?cat=actualites"},
            {"site_name": "Clubic", "url": "https://www.clubic.com/rss/actualites-informatique.xml"},
            {"site_name": "Programmez!", "url": "https://www.programmez.com/rss/actualites.xml"},
            {"site_name": "InfoQ (FR/EN)", "url": "https://www.infoq.com/fr/feed/"},
            {"site_name": "Journal du Net (JDN)", "url": "https://www.journaldunet.com/web-tech/rss.xml"},
            {"site_name": "Numerama", "url": "https://www.numerama.com/feed"},
            {"site_name": "LeMagIT", "url": "https://www.lemagit.fr/securite/rss.xml"},
            {"site_name": "Undernews", "url": "https://www.undernews.fr/feed"},
            {"site_name": "Linux.fr", "url": "https://linuxfr.org/rss/actualites.xml"}
        ]

        headers = { 
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' 
        }

        CATEGORY_MAP = {
            "Intelligence Artificielle": ["ia", "ai", "chatgpt", "machine learning", "openai"],
            "Cybersécurité": ["hack", "faille", "sécurité", "cyber", "ransomware", "virus"],
            "Développement": ["python", "java", "code", "dev", "framework", "django", "next.js", "github"],
            "Hardware": ["processeur", "nvidia", "intel", "carte graphique", "smartphone", "iphone"],
            "Architecture Cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker"],
            "Architecture Logicielle": ["microservices", "architecture", "design pattern", "scalabilité", "performance"],
            "Réseaux et Télécoms": ["5g", "réseau", "télécom", "fibre", "wifi", "edge computing"],
            "Données et Big Data": ["big data", "data", "hadoop", "spark", "analytics", "data lake"],
            "Blockchain et Cryptomonnaies": ["blockchain", "cryptomonnaie", "bitcoin", "ethereum", "defi", "nft"],
            "DevOps et CI/CD": ["devops", "ci/cd", "intégration continue", "déploiement continu", "jenkins", "gitlab ci"],
        }

        def get_category_by_content(text):
            text = text.lower()
            for cat_name, keywords in CATEGORY_MAP.items():
                if any(kw in text for kw in keywords):
                    # CORRECTION : Utilisation de get_or_create pour éviter le bug des doublons
                    category, _ = Category.objects.get_or_create(name=cat_name)
                    return category
            
            default_cat, _ = Category.objects.get_or_create(name="Général")
            return default_cat
        
        # Boucle pour les sources
        for src in SOURCE_CONFIG:
            self.stdout.write(f"Scraping de : {src['site_name']}...")
            try:
                # CORRECTION : Ajout d'un timeout de 15s pour éviter que Numerama ou d'autres bloquent le script
                response = requests.get(src['url'], headers=headers, timeout=15)
                response.raise_for_status() # Génère une erreur si le code HTTP n'est pas 200
                
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')

                for item in items[:10]:
                    title = item.title.text if item.title else "Sans titre"
                    link = item.link.text if item.link else ""
                    description = item.description.text if item.description else ""

                    if not Article.objects.filter(title=title).exists():
                        category = get_category_by_content(title + " " + description)

                        # Resume IA (On l'entoure aussi d'un try pour que si l'IA plante, l'article soit quand même créé)
                        try:
                            ai_summary = generate_ai_summary(description)
                        except:
                            ai_summary = "Résumé indisponible."

                        article = Article.objects.create(
                            title=title,
                            summary=description,
                            ai_summary=ai_summary,
                            category=category
                        )

                        Source.objects.create(
                            site_name=src['site_name'],
                            url=link,
                            article=article
                        )
                        
                        self.stdout.write(self.style.SUCCESS(f"  [OK] {title[:50]}..."))

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.WARNING(f"  [ERREUR RÉSEAU] {src['site_name']} : {e}"))
                continue # CORRECTION : On passe à la source suivante au lieu d'arrêter le script
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERREUR LOGIQUE] {src['site_name']} : {e}"))
                continue # CORRECTION : On passe à la source suivante

        self.stdout.write(self.style.SUCCESS("\nFin du scraping multi-sources !"))      