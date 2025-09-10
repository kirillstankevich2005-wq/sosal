import requests
import time
import sqlite3
from bs4 import BeautifulSoup
import asyncio
import logging
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(filename='domovita_flats_log.txt', level=logging.INFO, 
                    format='%(asctime)s %(levelname)s:%(message)s')


url = 'https://domovita.by/minsk/flats/rent?rooms=%2C%2C%3E3&price%5Bmin%5D=550&price%5Bmax%5D=900&price_type=all_usd&ajax='

database = 'flats.db'

def fetch_html_selenium(url):
    try:
        # Настройка Chrome опций
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Запуск в фоновом режиме
        chrome_options.add_argument("--disable-gpu")
        proxy_ext_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'proxy_chrome_ext')

        chrome_options.add_argument(f"--load-extension={proxy_ext_path}")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('log-level=3')

        # Укажите путь к вашему драйверу
        # service = Service('path/to/chromedriver')
        
        # Создание браузерного драйвера
        driver = webdriver.Chrome(options=chrome_options)
        
        # Переход на нужную страницу
        driver.get(url)
        
        # Ожидание завершения выполнения JavaScript
        time.sleep(5)  # Это время может потребоваться подстроить в зависимости от скорости загрузки страницы
        
        # Получение HTML-кода страницы
        html = driver.page_source
        
        # Закрытие браузера
        driver.quit()
        
        return html
    except Exception as e:
        logging.error(f"Selenium error: {e}")
        return ""

async def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
     
    except requests.RequestException as e:
        print(f"Error fetching ads: {e}")
        return []

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    flats = set()

    # Ищем div с классом 'list_mode'
    list_mode_div = soup.find('div', class_='found_content')
    if list_mode_div:
        # Ищем все <a> теги внутри этого div
        for a_tag in list_mode_div.find_all('a'):
            if 'href' in a_tag.attrs:
                link = a_tag['href']
                if 'domovita.by/minsk/flats/rent/' in link:
                    flats.add(link)
    
    return flats

def create_table():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domovita (
            link TEXT PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()

def fetch_ads():
    html = fetch_html_selenium(url)
    return parse_html(html)

def filter_new_ads(links):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()

    # Получаем все существующие ad_link из базы данных
    cursor.execute('SELECT link FROM domovita')
    existing_ad_links = {str(row[0]) for row in cursor.fetchall()}  # Приведение к строковому типу

    new_links = [ad_link for ad_link in links if str(ad_link) not in existing_ad_links]
    conn.close()
    return new_links

def add_ads_to_db(links):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    #https://domovita.by/minsk/flats/rent/
    for ad_link in links:
        cursor.execute('INSERT INTO domovita (link) VALUES (?)', (ad_link,))
    conn.commit()
    conn.close()

def get_new_flats():
    links = fetch_ads()
    new_links = []
    logging.info('Fetched links: %s', links)
    if links:
        new_links = filter_new_ads(links)
        logging.info('New links to be added: %s', new_links)
        if new_links:
            add_ads_to_db(new_links)
    return new_links

async def main():
    create_table()
    while True:
        links = fetch_ads()
        print ('got links')

        if links:
            new_links = filter_new_ads(links)
            if new_links:
                print ('got new  links')

                add_ads_to_db(new_links)
                
                print("Новые объявления:", new_links)
            else:
                print("нет новых")
        time.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())