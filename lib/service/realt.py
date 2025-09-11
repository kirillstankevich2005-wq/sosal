import requests
import time
import sqlite3

api_url = 'https://realt.by/bff/graphql'
flat_link = 'https://realt.by/rent-flat-for-long/object/'

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "x-realt-client": "www@4.23.0"
}

cookies = {
    "consent": '{"analytics":false,"advertising":false,"functionality":true}'
}

database = 'flats.db'

def create_table():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS realt (
            id TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def fetch_ads():
    try:
        payload = {
            "operationName": "searchObjects",
            "variables": {
                "data": {   
                    "where": {
                        "rooms": ["1","2","3"],
                        "priceTo": "600",
                        "priceType": "840",
                        "addressV2": [{"townUuid": "4cb07174-7b00-11eb-8943-0cc47adabd66"}],
                        "allSeparate": "true",
                        "category": 2
                    },
                    "pagination": {"page": 1, "pageSize": 30},
                    "sort": [
                        {"by": "paymentStatus", "order": "DESC"},
                        {"by": "priority", "order": "DESC"},
                        {"by": "raiseDate", "order": "DESC"},
                        {"by": "updatedAt", "order": "DESC"}
                    ],
                    "extraFields": None,
                    "isReactAdaptiveUA": False
                }
            },
            "query": """
            query searchObjects($data: GetObjectsByAddressInput!) {
              searchObjects(data: $data) {
                body {
                  results {
                    code
                  }
                }
              }
            }
            """
        }

        response = requests.post(api_url, headers=headers, cookies=cookies, json=payload)
        response.raise_for_status()
        data = response.json()

        results = (
            data.get('data', {})
            .get('searchObjects', {})
            .get('body', {})
            .get('results', [])
        )

        ids = [str(ad['code']) for ad in results if 'code' in ad]
        return ids

    except requests.RequestException as e:
        print(f"Error fetching ads: {e}")
        return []

def filter_new_ads(ids):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM realt')
    existing_ids = {row[0] for row in cursor.fetchall()}
    new_ids = [ad_id for ad_id in ids if ad_id not in existing_ids]
    conn.close()
    return new_ids

def add_ads_to_db(ids):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    for ad_id in ids:
        cursor.execute('INSERT INTO realt (id) VALUES (?)', (ad_id,))
    conn.commit()
    conn.close()

def make_links(ids):
    return [flat_link + str(id) + '/' for id in ids]

def get_new_flats():
    ids = fetch_ads()
    new_ids = []
    if ids:
        new_ids = filter_new_ads(ids)
        if new_ids:
            add_ads_to_db(new_ids)
    return make_links(new_ids)

def main():
    create_table()
    while True:
        ids = fetch_ads()
        if ids:
            new_ids = filter_new_ads(ids)
            if new_ids:
                add_ads_to_db(new_ids)
                print("Новые объявления:")
                for link in make_links(new_ids):
                    print(link)
            else:
                print("нет новых")
        time.sleep(60)

if __name__ == '__main__':
    main()

