import re
import requests, time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from news.models import Article, Category, Source
from news.utils import generate_ai_summary

class Command(BaseCommand):
    help = "Recupere les dernières news de plusieurs sources tech"

    def handle(self, *args, **options):
        # Configuration des sources (URLs mises à jour)
        SOURCE_CONFIG = [
            {"site_name": "Le Monde Informatique", "url": "https://www.lemondeinformatique.fr/flux-rss/thematique/toute-l-actualite/rss.xml"},
            {"site_name": "ZDNet France", "url": "https://www.zdnet.fr/actualites/rss/"},
            {"site_name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"site_name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"site_name": "Numerama", "url": "https://www.numerama.com/feed"},
            {"site_name": "Undernews", "url": "https://www.undernews.fr/feed"},
            {"site_name": "InCyber", "url": "https://incyber.fr/feed/"},
            {"site_name": "Actu IA", "url": "https://www.actuia.com/feed/"},
            {"site_name": "VentureBeat", "url": "https://venturebeat.com/feed/"},
            {"site_name": "Wired", "url": "https://www.wired.com/feed/rss"},
            {"site_name": "Clubic", "url": "https://www.clubic.com/actualites.rss"},
            {"site_name": "Programmez!", "url": "https://www.programmez.com/rss.xml"},
            {"site_name": "Journal du Net (JDN)", "url": "https://www.journaldunet.com/rss/"},
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        }

        # Liste de mots-clés à ignorer absolument (Gaming, Culture Pop, etc.)
        BLACKLIST = [
            "wow", "world of warcraft", "one piece", "anime", "manga", "film", "série", 
            "disney+", "jeu vidéo", "booster", 
            "reacher", "acteur", "cinéma", "gaming", "zelda", "elden ring", 
            "call of duty", "fifa", "fortnite", "league of legends", "valorant", "overwatch", 
            "minecraft", "roblox", "assassin's creed", "horizon zero dawn", "star wars", "marvel", 
            "dc comics", "avengers", "spiderman", "batman", "superman", "iron man", "thor", "hulk",
        ]

        CATEGORY_MAP = {
            "Intelligence Artificielle": ["ia", "ai", "chatgpt", "machine learning", "openai", "claude", "anthropic", "llm", "claudecode"],
            "Cybersécurité": ["hack", "faille", "sécurité", "cyber", "ransomware", "virus", "phishing", "kaspersky", "incyber", "forum", "anssi", "campus cyber"],
            "Développement": ["python", "java", "code", "dev", "framework", "django", "next.js", "github", "rust", "kotlin"],
            "Hardware": ["processeur", "nvidia", "intel", "carte graphique", "smartphone", "iphone", "macbook", "composant"],
            "Architecture Cloud": ["cloud", "aws", "azure", "gcp", "kubernetes", "docker", "serverless", "summit", "aws summit", "lambda", "s3"],
            "Architecture Logicielle": ["microservices", "architecture", "design pattern", "scalabilité", "performance"],
            "Réseaux et Télécoms": ["5g", "réseau", "télécom", "fibre", "wifi", "starlink"],
            "Données et Big Data": ["big data", "data", "hadoop", "spark", "analytics", "database", "sql", "nosql"],
            "Blockchain et Cryptomonnaies": ["blockchain", "cryptomonnaie", "bitcoin", "ethereum", "web3", "crypto"],
            "DevOps et CI/CD": ["devops", "ci/cd", "jenkins", "gitlab", "terraform", "ansible"],
        }

        def is_blacklisted(text):
            text = text.lower()
            return any(word in text for word in BLACKLIST)

        def get_category_by_content(text):
            text = text.lower()
            for cat_name, keywords in CATEGORY_MAP.items():
                if any(kw in text for kw in keywords):
                    category, _ = Category.objects.get_or_create(name=cat_name)
                    return category
            
            default_cat, _ = Category.objects.get_or_create(name="Général")
            return default_cat
        
        def extract_image_url(item, raw_description, article_link=None):
            enclosure = item.find('enclosure')
            if enclosure and enclosure.get('url') and 'image' in enclosure.get('type', ''):
                return enclosure.get('url')
            
            media_content = item.find(['media:content', 'content'])
            if media_content and media_content.get('url'):
                return media_content.get('url')
            
            media_thumbnail = item.find(['media:thumbnail', 'thumbnail'])
            if media_thumbnail and media_thumbnail.get('url'):
                return media_thumbnail.get('url')
            
            if raw_description:
                inner_soup = BeautifulSoup(raw_description, 'html.parser')
                img_tag = inner_soup.find('img')
                if img_tag and img_tag.get('src'):
                    return img_tag.get('src')
                
            if article_link:
                try:
                    img_response = requests.get(article_link, headers=headers, timeout=5)
                    if img_response.status_code == 200:
                        page_soup = BeautifulSoup(img_response.content, 'html.parser')
                        og_image = page_soup.find('meta', property='og:image') or page_soup.find('meta', attrs={'name': 'og:image'})
                        if og_image and og_image.get('content'):
                            return og_image.get('content')
                except:
                    pass
                
            return None
        
        for src in SOURCE_CONFIG:
            time.sleep(2) # Un peu de politesse
            self.stdout.write(f"Scraping de : {src['site_name']}...")
            try:
                response = requests.get(src['url'], headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.find_all('item') if soup.find_all('item') else soup.find_all('entry')

                for item in items[:5]:

                    title = item.title.text if item.title else "Sans titre"
                    # Gestion du format Atom (Linux.fr) où le lien est dans <link href="...">
                    if item.link and item.link.get('href'):
                        link = item.link.get('href')
                    else:
                        link = item.link.text if item.link else ""
                    
                    description = item.description.text if item.description else (item.summary.text if item.summary else "")

                    # FILTRE : On vérifie si l'article est hors-sujet
                    if is_blacklisted(title + " " + description):
                        self.stdout.write(self.style.WARNING(f"  [IGNORÉ] {title[:40]}... (Hors-sujet)"))
                        continue

                    if not Article.objects.filter(title=title).exists():
                        category = get_category_by_content(title + " " + description)

                        # Nettoyer la description si elle contient des balises HTML complexes (Optionnel mais recommandé)
                        clean_description = BeautifulSoup(description, "html.parser").get_text(separator=" ")
                        clean_description = re.sub(r'\s+', ' ', clean_description).strip()

                        image_url = extract_image_url(item, description, article_link=link)

                        try:
                            ai_summary = generate_ai_summary(description)
                        except:
                            ai_summary = description[:200] + "..."

                        article = Article.objects.create(
                            title=title,
                            summary=clean_description,
                            ai_summary=ai_summary,
                            category=category,
                            image_url=image_url
                        )

                        Source.objects.create(site_name=src['site_name'], url=link, article=article)
                        self.stdout.write(self.style.SUCCESS(f"  [OK] {title[:50]}... (Image: {'Oui' if image_url else 'Non'})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERREUR] {src['site_name']} : {e}"))
                continue

        self.stdout.write(self.style.SUCCESS("\nNettoyage terminé. TechPulse est à jour !"))     