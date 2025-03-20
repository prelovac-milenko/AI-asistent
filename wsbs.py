import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Lista kompanija 
codes = ["AERD"]

def clean_number(number_text):
    if number_text:
        number_text = number_text.replace(".", "")
        number_text = number_text.replace(",", ".")
        try:
            return float(number_text)
        except ValueError:
            return 0.0
    return 0.0

type_data = {1: [], 2: [], 3: []}

for code in codes:
    for type_id in range(1, 4):
        for year in range(2022, 2025):   # Godine finansijskih izvještaja 
            url = f'https://www.blberza.com/Pages/FinRepBalance.aspx?code={code}&type={type_id}&year={year}&semiannual=0'

            response = requests.get(url)
            if response.status_code != 200:
                print(f"Greška pri učitavanju stranice za {code}, godinu {year}, i tip izvještaja {type_id}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            table = soup.find(id="ctl00_ctl00_Content_SideContent_dgBilans")
            if not table:
                print(f"Podatci nisu učitani za {code}, godinu {year}, i tip izvještaja {type_id}.")
                continue

            print(f"Učitani podatci za {code}, godinu {year}, i tip izvještaja {type_id}!")

            # -----------------Ekstrakcija podataka ------------------------
            rows = table.find_all('tr')

            data = []

            for row in rows:
                cols = row.find_all('td')
                row_data = []

                for i, col in enumerate(cols):
                    text = col.get_text(strip=True)
                    
                    if i == 1:  
                        row_data.append(text)  
                    else:
                        row_data.append(clean_number(text) if text != "" else 0.0)  
                
                if row_data:
                    if type_id == 1:
                        row_data = row_data[:5]
                    elif type_id in [2, 3]:
                        row_data = row_data[:3]
                    
                    row_data.append(code)  
                    row_data.append(year)  

                    data.append(row_data)

            print(f"Dobijeno {len(data)} linija podatak  za kompaniju {code}, {year} godinu i tip {type_id}.")
            
            type_data[type_id].extend(data)

type_names = {
    1: "Bilans_stanja",
    2: "Bilans_uspjeha",
    3: "Bilans_tokova_gotovine"
}

# -------------------Spremanje podataka u JSON fajlove-------------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

for type_id in range(1, 4):
    if type_data[type_id]:
        #dictionaries
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
            elif type_id in [2, 3]:
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
        print(f"Podatci za {type_names[type_id]} su sačuvani u JSON fajl: {filename}")
    else:
        print(f"Nema podataka za {type_names[type_id]}.")
