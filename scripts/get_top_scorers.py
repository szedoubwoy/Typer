import requests
from bs4 import BeautifulSoup
import json

# URL to scrape
url = "https://pl.wikipedia.org/wiki/Mistrzostwa_Europy_w_Pi%C5%82ce_No%C5%BCnej_2024_(sk%C5%82ady)"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

teams = soup.select("table.wikitable")

players = []

for team in teams:
    # Find the caption to get the country
    caption = team.find("caption")
    if caption:
        country = caption.text.strip()
        rows = team.find_all("tr")[1:]  # Pomijamy nagłówek tabeli
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:  # Sprawdza, czy są przynajmniej 2 kolumny
                player_name = cols[0].text.strip()  # Pobiera nazwisko zawodnika
                player_name = player_name.split("\n")[0].strip()  # Usuń dodatkowe linie i spacje
                players.append((player_name, country))

# Zapisz do pliku JSON
with open("scripts/top_scorers.json", "w", encoding="utf-8") as f:
    json.dump(players, f, ensure_ascii=False, indent=4)
