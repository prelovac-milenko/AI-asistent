import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS

# --- Web Scraper za finansijske podatke --- #

codes = ["AERD"]  # Lista kompanija

def clean_number(number_text):
    """Konvertuje broj iz stringa u float."""
    if number_text:
        number_text = number_text.replace(".", "").replace(",", ".")
        try:
            return float(number_text)
        except ValueError:
            return 0.0
    return 0.0

# Struktura podataka po vrstama izvještaja
type_data = {1: [], 2: [], 3: []}

for code in codes:
    for type_id in range(1, 4):
        for year in range(2022, 2025):
            url = f'https://www.blberza.com/Pages/FinRepBalance.aspx?code={code}&type={type_id}&year={year}&semiannual=0'
            response = requests.get(url)

            if response.status_code != 200:
                print(f"❌ Greška: {code}, {year}, tip {type_id}. Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find(id="ctl00_ctl00_Content_SideContent_dgBilans")

            if not table:
                print(f"⚠️ Nema podataka za {code}, {year}, tip {type_id}.")
                continue

            print(f"✅ Učitani podaci za {code}, {year}, tip {type_id}!")

            rows = table.find_all('tr')
            data = []

            for row in rows:
                cols = row.find_all('td')
                row_data = []

                for i, col in enumerate(cols):
                    text = col.get_text(strip=True)
                    row_data.append(clean_number(text) if i != 1 else text)

                if row_data:
                    row_data.append(code)
                    row_data.append(year)
                    data.append(row_data)

            type_data[type_id].extend(data)

# Imena fajlova
type_names = {
    1: "Bilans_stanja",
    2: "Bilans_uspjeha",
    3: "Bilans_tokova_gotovine"
}

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Čuvanje podataka u JSON fajlove
for type_id in range(1, 4):
    if type_data[type_id]:
        json_data = []
        for row in type_data[type_id]:
            if type_id == 1:
                json_data.append({
                    "AOP": row[0],
                    "Opis": row[1],
                    "Bruto_tekuca": row[2],
                    "Ispravka_vrijednosti": row[3],
                    "Neto_tekuca": row[4],
                    "Kompanija": row[5],
                    "Godina": row[6]
                })
            else:
                json_data.append({
                    "AOP": row[0],
                    "Opis": row[1],
                    "Bruto_tekuca": row[2],
                    "Kompanija": row[3],
                    "Godina": row[4]
                })

        filename = f"finansijski_izvestaj_{type_names[type_id]}_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Sačuvano u {filename}")

# --- AI Chat Backend --- #

genai.configure(api_key="xxxxxxxxxxxxx")  # Postavi API ključ za Gemini

app = Flask(__name__)
CORS(app)

# Funkcija za pronalaženje i agregaciju podataka iz JSON fajlova
def extract_relevant_data(query):
    folder_path = "."  # Folder sa JSON fajlovima
    relevant_data = []

    # Ključne reči koje mogu biti od značaja za finansijske analize
    keywords = ["Bruto_tekuca", "Neto_tekuca", "Ispravka_vrijednosti", "Bilans", "Godina", "Kompanija"]

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)

                for record in data:
                    # Pronalazi samo relevantne podatke na osnovu ključnih reči
                    for key in keywords:
                        if key in record:
                            relevant_data.append(record)
                            break  # Ako nađe relevantne podatke u ovom zapisu, ne proverava dalje

    # Ako nije nađeno ništa relevantno, vraćamo prazan string
    if not relevant_data:
        return None

    # Grupisanje podataka po godinama radi analize trendova
    summary = {}
    for record in relevant_data:
        year = record.get("Godina", "Nepoznato")
        if year not in summary:
            summary[year] = []
        summary[year].append(record)

    return summary


# Funkcija za slanje podataka AI modelu
def ask_gemini(context_text, query):
    prompt = f"""
Koristi sljedeće finansijske podatke kako bi odgovorio na postavljeno pitanje:
{context_text}

Pitanje: {query}

Odgovori kao stručnjak iz oblasti finansija, analizirajući trendove i dajući preporuke zasnovane na podacima.
"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


# API ruta za postavljanje pitanja
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    pitanje = data.get("question", "").strip()

    if not pitanje:
        return jsonify({"error": "⚠️ Pitanje ne može biti prazno."}), 400

    relevant_text = extract_relevant_data(pitanje)

    if not relevant_text:
        return jsonify({"answer": "⚠️ Nema relevantnih podataka za ovo pitanje."})

    odgovor = ask_gemini(json.dumps(relevant_text, ensure_ascii=False, indent=4), pitanje)
    return jsonify({"answer": odgovor})


if __name__ == "__main__":
    app.run(debug=True)
