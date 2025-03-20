import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS

# --- Web Scraper --- #

# Lista kompanija za koje želimo podatke
codes = ["AERD"]

def clean_number(number_text):
    """Funkcija za formatiranje brojeva u float format."""
    if number_text:
        number_text = number_text.replace(".", "").replace(",", ".")
        try:
            return float(number_text)
        except ValueError:
            return 0.0
    return 0.0

# Struktura podataka za različite izvještaje
type_data = {1: [], 2: [], 3: []}

# Petlja kroz kompanije, tipove izvještaja i godine
for code in codes:
    for type_id in range(1, 4):
        for year in range(2022, 2025):
            url = f'https://www.blberza.com/Pages/FinRepBalance.aspx?code={code}&type={type_id}&year={year}&semiannual=0'

            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ Greška pri učitavanju {code}, {year}, tip {type_id}. Status: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find(id="ctl00_ctl00_Content_SideContent_dgBilans")

            if not table:
                print(f"⚠️ Nema podataka za {code}, {year}, tip {type_id}.")
                continue

            print(f"✅ Učitani podaci za {code}, {year}, tip {type_id}!")

            # Ekstrakcija podataka iz tabele
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

# Kreiramo timestamp za nazive fajlova
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
        print(f"✅ Podaci za {type_names[type_id]} sačuvani u {filename}")


# --- AI Chat Backend --- #

# Konfigurisanje Gemini AI ključa (ovde treba staviti ispravan API ključ!)
genai.configure(api_key="xxx")

app = Flask(__name__)
CORS(app)

# Funkcija za pretragu teksta u JSON fajlovima
def search_text_in_json(query):
    folder_path = "."  # Folder sa JSON fajlovima
    results = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)

                for record in data:
                    combined_text = " ".join(str(value) for value in record.values())
                    if query.lower() in combined_text.lower():
                        results.append(combined_text)

    return "\n".join(results) if results else None


# Funkcija za slanje podataka AI modelu
def ask_gemini(context_text, query):
    prompt = f"Koristi sljedeće podatke iz finansijskih izvještaja da odgovoriš na pitanje:\n\n{context_text}\n\nPitanje: {query}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


# API ruta za primanje upita
@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    pitanje = data.get("question", "").strip()

    if not pitanje:
        return jsonify({"error": "⚠️ Pitanje ne može biti prazno."}), 400

    relevant_text = search_text_in_json(pitanje)

    if not relevant_text:
        return jsonify({"answer": "⚠️ Nema relevantnih podataka za ovo pitanje."})

    odgovor = ask_gemini(relevant_text, pitanje)
    return jsonify({"answer": odgovor})


if __name__ == "__main__":
    app.run(debug=True)
