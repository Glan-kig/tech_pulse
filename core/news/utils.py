import os
import requests
import time
import html

HF_TOKEN = os.getenv('HF_TOKEN')
# L'URL corrigée et stable avec la structure /models/
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization" : f"Bearer {HF_TOKEN}"}

def generate_ai_summary(text):
    if not text:
        return "Résumé indisponible."
        
    text_clean = html.unescape(text)

    if len(text_clean) < 100:
        return text_clean  # Trop court pour résumer

    payload = {
        "inputs": text_clean,
        "parameters": {"max_length": 150, "min_length": 50, "do_sample": False}
    }

    # Tentatives en cas de modèle endormi (Erreur 503)
    for i in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                # Sécurité si l'API renvoie un dictionnaire au lieu d'une liste
                if isinstance(result, list):
                    summary = result[0].get('summary_text')
                else:
                    summary = result.get('summary_text')
                
                if summary:
                    return html.unescape(summary)
            
            elif response.status_code == 503:
                # Le modèle charge chez Hugging Face, on attend le temps estimé
                try:
                    wait_time = response.json().get('estimated_time', 20)
                except Exception:
                    wait_time = 20
                print(f"IA en cours de chargement... attente de {int(wait_time)}s")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"Erreur IA ({response.status_code}): {response.text}")
                break
                
        except Exception as e:
            print(f"Erreur technique lors de l'appel IA : {e}")
            break

    # Si tout échoue, on renvoie un extrait propre plutôt qu'un texte vide
    return text_clean[:200] + "..."