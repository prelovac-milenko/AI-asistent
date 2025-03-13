# pip install spacy google-generativeai flask-cors pymupdf  python -m spacy download en_core_web_md

from flask import Flask, request, jsonify
import fitz  
import google.generativeai as genai
from flask_cors import CORS
import spacy  # Za semantičko prepoznavanje ključnih reči u pitanju

#Gemini API ključ
genai.configure(api_key="AIzaSyBpkgGt-WuxjAve6ZAZcNBryCAZUBWjSHE")


nlp = spacy.load("en_core_web_md")  

app = Flask(__name__)
CORS(app)  


# funkcija za pretragu teksta u PDF-u
def search_text_in_pdf(pdf_path, query):
    doc = fitz.open(pdf_path)
    results = []

    
    query_doc = nlp(query)
    query_keywords = [token.text for token in query_doc if not token.is_stop and not token.is_punct]

    for page in doc:
        text = page.get_text("text")
        page_doc = nlp(text)

        
        if any(keyword in text.lower() for keyword in query_keywords):
            results.append(text)

    return "\n".join(results) if results else None


# funkcija za slanje upita 
def ask_gemini(context_text, query):
    prompt = f"Koristi sledeći deo dokumenta da odgovoriš na pitanje:\n\n{context_text}\n\nPitanje: {query}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


# API ruta za primanje upita
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    pitanje = data.get("question", "").strip()

    if not pitanje:
        return jsonify({"error": "Pitanje ne može biti prazno."}), 400

    pdf_path = "ORGANIZACIJA.pdf"  # Naziv tvog PDF fajla
    relevant_text = search_text_in_pdf(pdf_path, pitanje)

    if not relevant_text:
        return jsonify({"answer": "⚠️ Nema relevantnog teksta za ovo pitanje."})

    odgovor = ask_gemini(relevant_text, pitanje)
    return jsonify({"answer": odgovor})


if __name__ == "__main__":
    app.run(debug=True)
