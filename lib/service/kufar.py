import requests
import time
import sqlite3

api_url = 'https://api.kufar.by/search-api/v2/search/rendered-paginated'
params = {
    'cat': '1010',
    'cur': 'USD',
    'gtsy': 'country-belarus~province-minsk~locality-minsk',
    'lang': 'ru',
    'prc': 'r:150,600',
    'rms': 'v.or:1,2,3',
    'size': '30',
    'typ': 'let'
}
flat_link = 'https://re.kufar.by/vi/'

database = 'flats.db'

def create_table():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kufar (
            id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def fetch_ads():
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        ads = data.get('ads', [])
        extracted_ids = [ad['ad_id'] for ad in ads]
        return extracted_ids
    except requests.RequestException as e:
        print(f"Error fetching ads: {e}")
        return []

def filter_new_ads(ids):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Получаем все существующие ad_id из базы данных
    cursor.execute('SELECT id FROM kufar')
    existing_ad_ids = {str(row[0]) for row in cursor.fetchall()}  # Приведение к строковому типу

    new_ids = [ad_id for ad_id in ids if str(ad_id) not in existing_ad_ids]
    conn.close()
    return new_ids

def add_ads_to_db(ids):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    for ad_id in ids:
        cursor.execute('INSERT INTO kufar (id) VALUES (?)', (ad_id,))
    conn.commit()
    conn.close()

def get_new_flats():
    ids = fetch_ads()
    new_ids = []
    if ids:
            new_ids = filter_new_ads(ids)
            if new_ids:
                add_ads_to_db(new_ids)
    return make_links(new_ids)

def make_links(ids):
    return [flat_link + str(id) for id in ids]

def main():
    create_table()
    while True:
        ids = fetch_ads()
        if ids:
            new_ids = filter_new_ads(ids)
            if new_ids:
                add_ads_to_db(new_ids)
                print("Новые объявления:", new_ids)
            else :
                print("нет новых")
        time.sleep(60)

if __name__ == '__main__':
    main()
