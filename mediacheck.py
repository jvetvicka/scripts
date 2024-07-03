import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse
import pytz
import json
import os
from urllib.parse import urlparse

# Funkce pro kontrolu, zda článek obsahuje daná klíčová slova
def contains_keywords(text, keywords):
    for key, full_word in keywords.items():
        if key == 'AI':
            if 'AI' in text:
                return full_word
        else:
            if key.lower() in text.lower():  # Hledání bez ohledu na velikost písmen
                return full_word
    return None

# Funkce pro získání textu z entry summary
def get_summary_text(entry):
    summary_text = entry.summary if 'summary' in entry else ''
    if '<' in summary_text and '>' in summary_text:  # Kontrola, zda obsahuje HTML značky
        return BeautifulSoup(summary_text, 'html.parser').get_text()
    return summary_text

# Funkce pro získání názvu serveru z URL (bez 'www.')
def get_server_name(url):
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc
    if netloc.startswith('www.'):
        netloc = netloc[4:]
    return netloc

# Načtení a filtrování článků z RSS kanálů
def fetch_and_filter_rss(feed_url, start_date, end_date, keywords):
    articles = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        if not hasattr(entry, 'published'):
            continue  # Přeskočit články bez atributu 'published'
        article_date = dateparse(entry.published).replace(tzinfo=pytz.UTC)
        if start_date <= article_date <= end_date:
            summary_text = get_summary_text(entry)
            content = entry.title + " " + summary_text
            keyword_found = contains_keywords(content, keywords)  # Změna: Uložení nalezeného klíčového slova
            link = entry.link
            source = get_server_name(link)           
            if keyword_found:
                articles.append({
                    'title': entry.title,
                    'link': link,
                    'published': entry.published,
                    'content': content,
                    'source': source,  # Přidání serveru do slovníku
                    'keyword': keyword_found  # Přidání klíčového slova do slovníku
                })
    return articles


# Uložení obsahu RSS kanálů do souboru
def save_rss_content_to_file(rss_content, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(rss_content, f, ensure_ascii=False, indent=4)

# Načtení obsahu RSS kanálů ze souboru
def load_rss_content_from_file(file_name):
    rss_content = []
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            rss_content = json.load(f)
    return rss_content

# Aktualizace obsahu RSS kanálů ve souboru na základě nových dat
def update_rss_content_file(feeds, file_name, start_date, end_date, keywords):
    # Načtení existujícího obsahu
    rss_content = load_rss_content_from_file(file_name)

    # Získání nových článků a jejich filtrování
    new_articles = []
    for feed_url in feeds:
        new_articles.extend(fetch_and_filter_rss(feed_url, start_date, end_date, keywords))

    # Přidání nových článků k existujícím, pokud ještě nejsou přítomny
    existing_links = {article['link'] for article in rss_content}
    for article in new_articles:
        if article['link'] not in existing_links:
            rss_content.append(article)
            existing_links.add(article['link'])

    # Uložení aktualizovaného obsahu zpět do souboru
    save_rss_content_to_file(rss_content, file_name)

    return rss_content

# Zobrazení filtrovaných článků na obrazovku
def display_articles_to_console(articles):
    for article in articles:
        source = article.get('source', 'unknown')  # Zajištění, že klíč 'source' vždy existuje
        keyword = article.get('keyword', 'N/A')  # Zajištění, že klíč 'keyword' vždy existuje
        published_date = dateparse(article['published']).strftime("%d.%m")
        line = f"- {article['title']} ({source}, {published_date} - {keyword})"
        print(line)
        
# Uložení filtrovaných článků do souboru monitoring.md
def save_articles_to_file(articles, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in articles:
            source = article.get('source', 'unknown')  # Zajištění, že klíč 'source' vždy existuje
            keyword = article.get('keyword', 'N/A')  # Zajištění, že klíč 'keyword' vždy existuje
            published_date = dateparse(article['published']).strftime("%d.%m")
            line = f'<li class="novinka" data-keywords="{keyword}"><a href="{article["link"]}" target="_blank">{article["title"]}</a> <small>({source})</small> <code class="highlighter-rouge">{keyword}</code></li>\n'
            f.write(line)

# Hlavní program
if __name__ == "__main__":
    # Seznam RSS kanálů
    feeds = [
        'https://hlidacipes.org/feed/',
        'https://www.irozhlas.cz/rss/irozhlas/tag/7708693',
        'https://denikn.cz/minuta/feed/',
        'https://dennikn.sk/minuta/feed',
        'https://dennikn.sk/rss/',
        'https://denikn.cz/rss/',
        'https://www.mvcr.cz/chh/SCRIPT/rss.aspx?nid=',
        'https://cedmohub.eu/cs/feed/',
        'https://europeanvalues.cz/cs/feed/',
        #'https://demagog.cz/rss/index.atom', - Zatím vypnu, cedmohub postuje jak AFP, tak Demagog, tak aby nebylo 2x
        'https://www.voxpot.cz/feed/',
        'https://www.aktuality.sk/rss/',
        'https://zpravy.aktualne.cz/rss/',
        'https://www.seznamzpravy.cz/rss',
        'https://www.irozhlas.cz/rss/irozhlas/section/zpravy-domov',
        'https://www.irozhlas.cz/rss/irozhlas/section/zpravy-svet',
        'https://www.lupa.cz/rss/clanky/',
        'https://www.denik.cz/rss/zpravy.html',
        'https://www.novinky.cz/rss',
        'https://euractiv.cz/feed/',
        'https://euractiv.sk/feed/',
        'https://cc.cz/feed/',
        'https://www.ceskenoviny.cz/sluzby/rss/cr.php',
        'https://www.ceskenoviny.cz/sluzby/rss/svet.php',
        'https://www.zive.cz/rss/sc-47/',
        'https://servis.idnes.cz/rss.aspx?c=zpravodaj',
        'https://ct24.ceskatelevize.cz/rss/tema/hlavni-zpravy-84313',
        'https://domaci.hn.cz/?m=rss',
        'https://zahranicni.hn.cz/?m=rss',
        'https://www.investigace.cz/feed/',
        'https://www.sme.sk/rss-title',
        'https://spravy.rtvs.sk/feed/',
        'https://www.respekt.cz/api/rss?type=articles&unlocked=1',    
        'https://refresher.cz/rss',
        'https://refresher.sk/rss',
        'https://www.tyzden.sk/feed/',
        'https://hnonline.sk/feed',
        'http://www.teraz.sk/rss/slovensko.rss',
        'http://www.teraz.sk/rss/zahranicie.rss',
        'https://www.topky.sk/rss/8/topky'
        # Přidejte další RSS kanály podle potřeby
    ]

    # Dictionary pro vyhledávání slov v textu a jejich převod na kategorie.
    keywords = {
        #dezinformace
        'dezinform': 'dezinformace',
        'misinform': 'dezinformace',
        'malinforma': 'dezinformace',
        'hoax': 'dezinformace',
        #mozna zvlast kategorie
        'konspir': 'konspirční teorie',
        'manipulace': 'manipulace',
        'fake news': 'dezinformace',
        'postfakt': 'doba postfaktická',
        'pseudověd': 'dezinformace',

        #strategická komunikace
        'strategická komunik': 'strategická komunikace',
        'stratcom': 'strategická komunikace',

        #propaganda
        'propagand': 'propaganda',
        'sociální inženýrství': 'sociální inženýrství',
        'dragonbridge': 'dragonbridge',
        'storm 1376': 'storm 1376',
        'qanon': 'qanon',
        'infowars': 'infoWars',
        'false flag': 'false flag',
        'hybridní hrozb': 'hybridní hrozba',
        'informační válk': 'informační válka',
        'narativ': 'narativ',
        'mystifika': 'mystifikace',

        #sociální sítě
        'twitter': 'x.com',
        'Meta': 'facebook',
        'musk': 'Elon Musk',
        'tik tok': 'tik tok',
        'sociální sítě': 'sociální sítě',
        'algoritm': 'algoritmus',
        'gaslighting': 'gaslighting',

        #AI
        'umělá inteligence': 'AI',
        'deepfake': 'deepfake',
        'AI': 'AI',

        #Podvodné praktiky
        'podvod': 'podvod',
        'clickbait': 'clickbait',
        'botnet': 'botnet',
        'ddos': 'ddos',
        'troll': 'troll',
        'kyber': 'kyberbezpečnost',
        'spamouflage': 'spamouflage',
        'spam': 'spam',
        'doxx': 'doxxing',
        'doxing': 'doxxing',
        'brigading': 'brigading',
        'phishing': 'phishing',
        'scam': 'scam',
        'smishing': 'smishing',
        'vishing': 'vishing',
        'hack': 'hacking',
        'phreak': 'phreaking',
        'sextortion': 'sextortion',
        'gerrymandering': 'gerrymandering',
        'hijacking': 'hijacking',

        #Mediální gramotnost
        'mediální gramotnost': 'mediální gramotnost',

        #Řetězové zprávy
        'řetězový email': 'řetězáky',
        'řetězové email': 'řetězáky',
        'řetězák': 'řetězáky',

        #Svoboda slova
        'svoboda slova': 'svoboda slova',
        'cenzúr': 'cenzura',
        'cenzur': 'cenzura',
        'newspeak': 'newspeak',

        #Fact-checking
        'fact-checking': 'fact-checking',
        'overovanie faktov': 'fact-checking',
        'ověřování faktů': 'fact-checking',
        'prebunking': 'prebunking',
        'debunking': 'debunking',

        #Radikalizace
        'manosféra': 'manosféra',
        'redpilling': 'redpilling',
        'radikali': 'radikalismus',
        'krajní pravice': 'krajní pravice',
        'overton': 'overtonovo okno',
        'weaponiz': 'weaponizace',

        #Kritické myšlení
        'konfirmačn': 'konfirmační bias',
        'kritické myšlení': 'kritické myšlení',
}

    # Zadání datumového rozmezí
    start_date_str = input("Zadejte počáteční datum (YYYY-MM-DD): ")
    end_date_str = input("Zadejte koncové datum (YYYY-MM-DD): ")

    # Použití aktuálního data, pokud nejsou zadány
    if not start_date_str:
        start_date = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    
    if not end_date_str:
        end_date = datetime.now(pytz.UTC).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").replace(tzinfo=pytz.UTC) + timedelta(days=1, seconds=-1)

    # Název souboru s kompletním obsahem RSS kanálů
    rss_content_file = "rss-obsah.json"

    # Aktualizace obsahu RSS kanálů ve souboru
    updated_rss_content = update_rss_content_file(feeds, rss_content_file, start_date, end_date, keywords)


    # Filtrování článků podle klíčových slov a datumového rozmezí a zdroje
    filtered_articles = [
        article for article in updated_rss_content
        if ((contains_keywords(article['content'], keywords) or article.get('source') == 'cedmohub.eu') and
        start_date <= dateparse(article['published']).replace(tzinfo=pytz.UTC) <= end_date)
    ]
   
    # Kontrola HTTPS pouze pro filtrovane clanky
    for article in filtered_articles:
        if not article['link'].startswith("https://"):
            print("\033[91m" + "Upozornění:" + "\033[0m", f"Odkaz '{article['link']}' nepoužívá HTTPS.")
    
    # Vytvoření názvu souboru pro filtrované články
    file_name_suffix = start_date.strftime("%d-%m") + "-" + end_date.strftime("%d-%m") + ".json"
    filtered_articles_file = "filtered_articles_" + file_name_suffix
    
    # Uložení filtrovaných článků do souboru
    save_articles_to_file(filtered_articles, 'monitoring.md')

    # Zobrazení filtrovaných článků na obrazovku
    display_articles_to_console(filtered_articles)