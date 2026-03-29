import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from news.models import Article, Category, Source
from news.utils import generate_ai_summary

class Command(BaseCommand):
    help = "Recupere les derniere news de plusieurs sources tech"

    def handle(self, *args, **options):
        # Liste des sources
        SOURCE_CONFIG = [
            {
                "name" : "Le Monde Informatique",
                "url" : "https://www.lemondeinformatique.fr/flux-rss/thematique/toute-l-actualite/rss.xml"
            },
            {
                "name" : "01Net",
                "url" : "https://www.01net.com/actualites/"
            },
            {
                "name" : "ZDNet",
                "url" : "https://www.zdnet.fr/feeds/rss/actualites/"
            },
        ]

        # Systeme de tri par mot-cles pour les categoies
        CATEGORY_MAP = {
            "Intelligence Artificielle" : ["ia", "ai", "chatgpt", "machine learning", "openai"],
            "Cybersécurité" : ["hack", "faille", "sécurité", "cyber", "ransomware", "virus"],
            "Développement" : ["python", "java", "code", "dev", "framwork", "django", "next.js", "github"],
            "Hardware" : ["processeur", "nvidia", "intel",  "carte graphique", "smartphone", "iphone"],
        }

        def get_category_by_content(text) :
            text = text.lower()
            for cat_name, keywords in CATEGORY_MAP.items() :
                if any(kw in text for kw in keywords) :
                    category, _ = Category.objects.get_or_create(name=cat_name)
                    return category
            default_cat = Category.objects.get_or_create(name="Général")
            return default_cat
        
        # Boucle pour les sources
        for src in SOURCE_CONFIG :
            self.stdout.write(f"Scraping de : {src['name']}...")
            try :
                response = requests.get(src['url'], timeout=10)
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item')

                for item in items[:5] :
                    title = item.title.text
                    link = item.link.text
                    description = item.description.text if item.description else ""

                    if not Article.objects.filter(title=title).exists():
                        category = get_category_by_content(title + " " + description)

                        # Resume IA
                        ai_summary = generate_ai_summary(description)
                        article = Article.objects.create(
                            title=title,
                            summary=description,
                            ai_summary=ai_summary,
                            category=category
                        )
                        self.stdout.write(self.style.SUCCESS(f" Ajouté : {title[:50]}..."))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Erruer sur {src['name']} : {e}")
                )
                self.stdout.write(self.style.SUCCESS("Fin du scaping multi-sources !"))
       