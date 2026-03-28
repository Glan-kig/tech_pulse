import os
import requests
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv('HF_TOKEN')
# API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization" : f"Bearer {HF_TOKEN}"}

def test_summary():
    texte_test = """
        L'intelligence artificielle générative transforme radicalement le développement logiciel en 2026. 
        De plus en plus d'entreprises adoptent des outils comme GitHub Copilot pour accélérer le codage 
        et réduire les erreurs humaines. Cette révolution permet aux développeurs de se concentrer sur 
        l'architecture plutôt que sur la syntaxe répétitive.
    """

    payload = {
        "inputs": f"summarize: {texte_test}",
        "parameters": {
            "max_length": 100,
            "min_length": 30
        }
    }
    print("Envoi a Hugging Face...")

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 410:
        new_url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
        response = requests.post(new_url, headers=headers, json=payload)

    if response.status_code == 200 :
        result = response.json()
        print("\n Resume Reussi :")
        
        summary = result[0].get('summary_text') or result[0].get('generated_text')
        print(summary)
    elif response.status_code == 503:
        # Très fréquent : le modèle "dort", il faut attendre qu'il se charge
        est_time = response.json().get('estimated_time', 20)
        print(f"\nModèle en cours de réveil... Réessaie dans {int(est_time)} secondes.")
    else :
        print(f"\n Erreur {response.status_code} : {response.text}")

if __name__ == "__main__" :
    test_summary()