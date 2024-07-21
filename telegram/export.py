import json
import os
from datetime import datetime

# Název vstupního JSON souboru
input_file = "feeds.json"

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

# Funkce pro konverzi JSON dat do HTML pro konkrétní den a uložení do souboru podle data
def convert_to_html_for_day(entries, target_date):
    html_file = f"telegram-{target_date.replace('.', '-')}.html"
    with open(html_file, "w", encoding="utf-8") as file:
        for item in entries:
            if item.get('published') == target_date:
                author_name = item['author']['name']
                published_date = item.get('published', 'N/A')
                url = item.get('url', 'N/A')
                content_html = item.get('content_html', 'No content available')
                
                file.write(f"<strong>Autor:</strong> {author_name}<br>\n")
                file.write(f"<strong>Datum:</strong> {published_date}<br>\n")
                file.write(f"<strong>URL:</strong> <a href=\"{url}\">{url}</a><br>\n")
                file.write(f"<strong>Obsah:</strong><br>\n")
                file.write(f"<div>{content_html}</div>\n")
                file.write("<hr>\n")

# Hlavní část skriptu pro generování HTML
if __name__ == "__main__":
    existing_data = load_existing_data(input_file)
    
    if not isinstance(existing_data, dict):
        print("No valid data found in the JSON file.")
        exit()

    # Zeptáme se uživatele na konkrétní den
    target_date = input("Zadejte datum ve formátu DD.MM.YYYY: ")
    
    all_entries = []
    for source in existing_data:
        all_entries.extend(existing_data[source]["items"])
    
    convert_to_html_for_day(all_entries, target_date)

    print(f"HTML file for {target_date} successfully created.")
