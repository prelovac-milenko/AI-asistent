import google.generativeai as genai
import json
from config import AI_KEY

genai.configure(api_key=AI_KEY)

def ask_ai(emitent: str, bilansi: dict, pitanje: str) -> str:
    context_text = json.dumps({emitent: bilansi}, ensure_ascii=False, indent=2)
    prompt = f"""
        Koristi sljedeće finansijske podatke kako bi odgovorio na postavljeno pitanje:
        {context_text}

        Pitanje: {pitanje}

        Odgovori kao stručnjak iz oblasti finansija, analizirajući trendove i dajući preporuke zasnovane na podacima.
        """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text
