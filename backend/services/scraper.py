import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_emitenti():
    url = 'https://www.blberza.com/Pages/IssuerList.aspx'
    session = requests.Session()

    # Generisanje timestamp-a
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Dobavljanje početne stranice za VIEWSTATE podatke
    response = session.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
    viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
    eventvalidation = soup.find('input', {'id': '__EVENTVALIDATION'})['value']

    # Parametri za POST zahtjev
    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
        'ctl00$ctl00$Content$MainContent$ddlIssuersPageSize': '10000',
    }

    # POST zahtjev za dohvaćanje svih podataka
    response = session.post(url, data=payload)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'id': 'ctl00_ctl00_Content_MainContent_gvIssuers'})
    rows = table.find_all('tr')[1:]  # preskoči zaglavlje

    # Izdvajanje podataka
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 4:
            record = {
                'oznaka': cells[0].get_text(strip=True),
                'naziv': cells[1].get_text(strip=True),
                'adresa': cells[2].get_text(strip=True),
                'grad': cells[3].get_text(strip=True)
            }
            data.append(record)

    return {
        'timestamp': timestamp,
        'emittenti': data
    }
