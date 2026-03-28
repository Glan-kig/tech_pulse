import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from news.models import Article, Category, Source
from news.utils import generate_ai_summary

class Command(BaseCommand):
    help = "Recupere les derniere news de LemondeInformatique"

    def handle(self, *args, **options):
        url = "https://www.lemondeinformatique.fr/flux-rss/thematique/toute-l-actualite/rss.xml"
        response = requests.get(url)
        response.encoding = response.apparent_encoding

        # On utilise un parseur XML ici car c'est un flux RSS (plus stable que le HTML)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all('item')
        cat, _= Category.objects.get_or_create(name="Actualité Générale")
        count = 0
        for item in items[:10]: # On recupere les 10 derniers
            title = item.title.text
            link = item.link.text
            description = item.description.text if item.description else "Pas de Résumé."

            # Eviter les doublons
            if not Article.objects.filter(title=title).exists():
                # summary_ia = generate_ai_summary(description) # appel a l'IA
                article = Article.objects.create(
                    title=title,
                    summary = description[:500],
                    # ai_summary = summary_ia, # On enregistre le resumer de l'IA
                    category = cat
                )

                # On cree les sources liée
                Source.objects.create(
                    article = article,
                    site_name = "Le Monde Informatique",
                    url = link
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Succès : {count} nouveaux articles ajoutés ! "))