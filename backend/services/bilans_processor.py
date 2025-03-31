import requests
from bs4 import BeautifulSoup

def clean_number(text):
    if not text:
        return 0.0
    text = text.replace("\xa0", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(text)
    except ValueError:
        return 0.0


def fetch_bilansi(code: str, years: list[int]):
    type_names = {
        1: "Bilans_stanja",
        2: "Bilans_uspjeha",
        3: "Bilans_tokova_gotovine"
    }

    result = {}

    for year in years:
        result[str(year)] = {}

        for type_id in range(1, 4):
            url = f"https://www.blberza.com/Pages/FinRepBalance.aspx?code={code}&type={type_id}&year={year}&semiannual=0"
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find(id="ctl00_ctl00_Content_SideContent_dgBilans")

            if not table:
                continue

            rows = table.find_all("tr")
            parsed = []

            for row in rows:
                cols = row.find_all("td")
                if type_id == 1 and len(cols) >= 5:
                    parsed.append({
                        "AOP": cols[0].text.strip(),
                        "Opis": cols[1].text.strip(),
                        "Bruto_tekuca": clean_number(cols[2].text),
                        "Ispravka_vrijednosti": clean_number(cols[3].text),
                        "Neto_tekuca": clean_number(cols[4].text),
                    })
                elif type_id in [2, 3] and len(cols) >= 3:
                    parsed.append({
                        "AOP": cols[0].text.strip(),
                        "Opis": cols[1].text.strip(),
                        "Bruto_tekuca": clean_number(cols[2].text)
                    })

            result[str(year)][type_names[type_id]] = parsed

    return result
