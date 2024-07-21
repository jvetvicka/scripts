import feedparser
import json
import os
import time
from datetime import datetime
from bs4 import BeautifulSoup
from source import rss_sources

# Název výstupního JSON souboru
output_file = "feeds.json"

# Funkce pro načtení existujících dat z JSON souboru
def load_existing_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                if content.strip():  # Kontrola, zda soubor není prázdný
                    return json.loads(content)
                return {}
        except json.JSONDecodeError as e:
            print(f"Error loading JSON data: {e}")
            return {}
    return {}

# Funkce pro uložení dat do JSON souboru
def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Funkce pro převod data na formát DD.MM.YYYY
def format_date(date_str):
    try:
        parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return parsed_date.strftime('%d.%m.%Y')
    except ValueError:
        return date_str

# Funkce pro odstranění specifických HTML tagů a všech <br>, a konkrétního sousloví
def clean_html_content(html_content):
    soup = BeautifulSoup(html_content, 'lxml')

    # Odstranění tagů <html> a <body> pouze pokud jsou na začátku nebo konci dokumentu
    for tag in ['html', 'body']:
        for element in soup.find_all(tag):
            if element == soup.html or element == soup.body:
                element.unwrap()
            else:
                element.decompose()

    # Odstranění obrázků
    for img in soup.find_all('img'):
        img.decompose()  # Odstraní obrázek

    # Odstranění všech <br> tagů
    for br in soup.find_all('br'):
        br.decompose()

    # Odstranění <video> tagů a veškerého jejich obsahu
    for video in soup.find_all('video'):
        video.decompose()

    # Odstranění obalujících <p> tagů, ale ne jejich obsahu
    for p in soup.find_all('p'):
        if not p.contents:
            p.decompose()
        else:
            p.unwrap()  # Pokud <p> tag obsahuje nějaký obsah, odstraníme pouze tag, obsah zůstane

    # Odstranění prázdných <a> tagů
    for a in soup.find_all('a'):
        if not a.get('href') or not a.contents:
            a.decompose()  # Odstraní prázdné <a> tagy

    # Odstranění konkrétního sousloví
    unwanted_phrase = ('Sledujte a zdieľajte<a href="https://t.me/casusbellilive" rel="noopener" '
                       'target="_blank">https://t.me/casusbellilive</a>| <a href="https://youtube.com/@casusbellilivenew" '
                       'rel="noopener" target="_blank">YOUTUBE</a> | <a href="https://odysee.com/@casusbelli:6" '
                       'rel="noopener" target="_blank">ODYSEE</a> | <a href="https://t.me/casusbellichat" rel="noopener" '
                       'target="_blank">CB CHAT</a> | <a href="https://t.me/CasusBellihistory" rel="noopener" '
                       'target="_blank">CB HISTORY</a> | <a href="https://matrix.casusbelli.live/" rel="noopener" '
                       'target="_blank">CB Matrix</a> | <a href="http://t.me/CasusBelliLiveBot" rel="noopener" '
                       'target="_blank">CONTACT</a> | <a href="https://t.me/casusbelliarchiv" rel="noopener" '
                       'target="_blank">CB ARCHIV</a> | <a href="https://www.resistance.sk/shop/sk/2-domov" '
                       'rel="noopener" target="_blank">SHOP</a>')

    html_content = str(soup).replace(unwanted_phrase, '')

    return html_content

# Funkce pro zpracování jednoho RSS zdroje
def process_rss(url):
    print(f"Processing source: {url}")
    feed = feedparser.parse(url)
    entries = []
    for entry in feed.entries:
        print(f"Processing entry with ID: {entry.id}")
        entry_data = {
            "source": url,  # Přidáme URL zdroje, abychom věděli, odkud položka pochází
            "id": entry.get('id', entry.get('link', 'N/A')),
            "author": {
                "name": entry.get('author', 'Unknown')
            },
            "published": format_date(entry.get('published', 'N/A')),
            "url": entry.get('link', 'N/A'),
            "content_html": clean_html_content(entry.get('content', [{'value': entry.get('summary', 'No content available')}])[0].get('value', 'No content available'))
        }
        entries.append(entry_data)
    return entries

# Funkce pro seřazení položek podle data publikace
def sort_entries_by_date(entries):
    try:
        return sorted(entries, key=lambda x: datetime.strptime(x['published'], '%d.%m.%Y'), reverse=True)
    except ValueError:
        return entries

# Hlavní část skriptu pro stahování a ukládání dat
if __name__ == "__main__":
    existing_data = load_existing_data(output_file)
    
    if not isinstance(existing_data, dict):
        existing_data = {}

    all_entries = []
    for index, source in enumerate(rss_sources):
        new_entries = process_rss(source)
        all_entries.extend(new_entries)
        
        # Pauza 10 sekund mezi zpracováním jednotlivých zdrojů
        if index < len(rss_sources) - 1:  # Vyhnout se pauze po posledním zdroji
            print("Waiting for 10 seconds before processing the next source...")
            time.sleep(10)

    sorted_entries = sort_entries_by_date(all_entries)
    
    # Rozdělení seřazených položek zpět podle kanálů pro JSON
    for entry in sorted_entries:
        source = entry["source"]
        if source not in existing_data:
            existing_data[source] = {"items": []}
        existing_data[source]["items"].append(entry)
    
    save_data(output_file, existing_data)
    
    print("Data successfully saved to JSON.")
