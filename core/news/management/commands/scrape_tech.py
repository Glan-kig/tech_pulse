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
            {"site_name": "L'Informatique", "url": "https://www.linformatique.com/flux-rss/"},
            {"site_name": "ZDNet France", "url": "https://www.zdnet.fr/actualites/rss/"},
            {"site_name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"site_name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"site_name": "Developpez.com", "url": "https://www.developpez.com/index/rss.php?cat=actualites"},
            {"site_name": "Clubic", "url": "https://www.clubic.com/actualites.rss"},
            {"site_name": "Programmez!", "url": "https://www.programmez.com/rss.xml"},
            {"site_name": "InfoQ (FR/EN)", "url": "https://www.infoq.com/fr/feed/"},
            {"site_name": "Journal du Net (JDN)", "url": "https://www.journaldunet.com/rss/"},
            {"site_name": "Numerama", "url": "https://www.numerama.com/feed"},
            {"site_name": "LeMagIT", "url": "https://www.lemagit.fr/actualites"},
            {"site_name": "Undernews", "url": "https://www.undernews.fr/feed"},
            #{"site_name": "Linux.fr", "url": "https://linuxfr.org/news.atom"}
        ]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        }

        # Liste de mots-clés à ignorer absolument (Gaming, Culture Pop, etc.)
        BLACKLIST = [
            "wow", "world of warcraft", "one piece", "anime", "manga", "film", "série", 
            "netflix", "disney+", "jeu vidéo", "ps5", "xbox", "nintendo", "booster", 
            "reacher", "acteur", "cinéma", "gaming", "zelda", "elden ring", "cyberpunk", "gta", 
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

                        Source.objects.create(site_name=src['site_name'], url=link, article=article)
                        self.stdout.write(self.style.SUCCESS(f"  [OK] {title[:50]}..."))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERREUR] {src['site_name']} : {e}"))
                continue

        self.stdout.write(self.style.SUCCESS("\nNettoyage terminé. TechPulse est à jour !"))     