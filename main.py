import json

import pymongo
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'}
MONGO_URI = 'localhost'
MONGO_DB = 'GuoKe'
MONGO_TABLE = 'data'

def get_index(offset):
    base_url = 'https://www.guokr.com/apis/minisite/article.json?'
    data = {
        'limit': '20',
        'offset': offset,
        'retrieve_type': 'by_subject'
    }
    url = base_url + urlencode(data)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except ConnectionError as e:
        print('Error:', e)
        return None


def parse_json(text):
    result = json.loads(text)
    if result:
        for item in result.get('result'):
            yield item.get('url')
def get_page(url):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text


def parse_page(text):
    soup = BeautifulSoup(text, 'lxml')
    content = soup.find('div', class_="content")
    title = content.find('h1', id="articleTitle").get_text()
    author = content.find('div', class_="content-th-info").find('a').get_text()
    article_content = content.find('div', class_="document").find_all('p')
    all_p = [i.get_text() for i in article_content if not i.find('img') and not i.find('a')]
    article = '\n'.join(all_p)
    data = {
        'title': title,
        'author': author,
        'article': article
    }
    return data


def save_mango(data):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    table = db[MONGO_TABLE]
    if table.insert(data):
        print('succeeded save to mongo',data)
    else:
        print('failed save to mongo',data)



def main():
    for offset in range(500) :
        text = get_index(18+offset*20)
        all_url = parse_json(text)
        for url in all_url:
            resp = get_page(url)
            data = parse_page(resp)
            save_mango(data)


if __name__ == '__main__':
    main()
