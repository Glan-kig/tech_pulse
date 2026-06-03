import os
import html
from groq import Groq

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def generate_ai_summary(text) -> str:
    if not text:
        return "Résumé indisponible."
    
    text_clean = html.unescape(text)

    if len(text_clean) < 100:
        return text_clean
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role" : "system",
                    "content": (
                        "Tu es un assistant expert en résumé d'actualités technologiques. "
                        "Fais un résumé clair, concis et fluide en français du text fourni. "
                        "Donne une introduction d'une phrase, puis 3 points clés maximum. "
                    )
                },
                {
                    "role": "user",
                    "content": f"Voici l'article à résumer : {text_clean}"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=250
        )

        summary = chat_completion.choices[0].message.content

        if summary:
            return html.unescape(summary).strip()
        
    except Exception as e:
        print(f"Erreur lors de la génération du résumé : {e}")

    return text_clean[:250] + "..." if len(text_clean) > 250 else text_clean