# import openai # A utiliser plus tard 
import os
import requests
import time
import html

"""
def generate_ai_summary(text):
    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role" : "system",
                "content" : "Tu es un expert en veille  technologique pour etudiants. Resume l'article suivant en 3 points cles maximum."
            },
            {
                "role" : "user",
                "content" : text
            }
        ],
        max_tokens=150
    )
    return response.choices[0].message.content
"""
HF_TOKEN = os.getenv('HF_TOKEN')
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization" : f"Bearer {HF_TOKEN}"}

def generate_ai_summary(text):
    text_clean = html.unescape(text)
    """
    Génère un résumé automatique pour les articles de TechPulse.
    """
    if not text_clean or len(text_clean) < 100:
        return text_clean  # Trop court pour résumer

    payload = {
        "inputs": text_clean,
        "parameters": {"max_length": 150, "min_length": 50, "do_sample": False}
    }

    # Tentatives en cas de modèle endormi (Erreur 503)
    for i in range(3):
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            summary = result[0].get('summary_text')
            return html.unescape(summary)
        
        elif response.status_code == 503:
            # Le modèle charge, on attend un peu
            wait_time = response.json().get('estimated_time', 20)
            print(f"IA en cours de chargement... attente de {int(wait_time)}s")
            time.sleep(wait_time)
            continue
            
        elif response.status_code == 410:
            # Fallback vers le Router si Hugging Face force la migration
            router_url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
            response = requests.post(router_url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()[0].get('summary_text')
            break
        else:
            print(f"Erreur IA ({response.status_code}): {response.text}")
            break

    return text[:200] + "..." # Retourne un extrait simple en cas d'échec total