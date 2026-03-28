import openai
import os

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