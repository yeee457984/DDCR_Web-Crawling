# %%
import requests
from bs4 import BeautifulSoup
import re
import sys

# %%
api_url = "https://www.ddcar.com.tw/api/web/news/categories/articles/list/?cateId=0&page="
headers = {
    "sec-ch-ua-platform": '"Windows"',
    "X-CSRF-TOKEN": "GkITq3dxsBaQv5SHTXWDlAV2YBSfIFkS45zTrnf9",
    "X-XSRF-TOKEN": "eyJpdiI6Imd5NmR3RURLczBTTFNSYnl1YndRdVE9PSIsInZhbHVlIjoiUkw3dXdRT2NVTldhWHZWTUxLMEgxS0lXL2FqNXhwZUJGUnB1d3pvNGp0U3o4SmVSSDNwOVp0cXJBY2d1NU5aUEpORXBITFo2QXlKUDBtWTZOUGpKNTRKUGJORG5hRzZVaWtJdVBwYjBQRG91TzQzWTVHM2ZkTUhGa092SXNjUm8iLCJtYWMiOiJjOGFmOTMwYzI1MjMyZTA2M2I4MDc5M2YwNzYwNjk5ZTEwOWE5NjI0MDljNTU2ZTRhNWVmMzM1MmFkZDY2ZTY4In0=",
    "Referer": "https://www.ddcar.com.tw/news/categories/0/%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E/list/",
    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

# %%
articles_dict = []
# %%
def extract_id_from_url(url):
    match = re.search(r'/detail/(\d+)', url)
    if match:
        return match.group(1)
    return None

def fetch_article_list(page):
    resp = requests.get(api_url+page, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data['res']

def fetch_article_content(article_url):
    id = extract_id_from_url(article_url)
    resp = requests.get('https://www.ddcar.com.tw/api/web/blogs/articles/detail?id={}&a=false'.format(id), headers=headers)
    resp.raise_for_status()
    data = resp.json()
    # Content
    html_content = data['res']['htmlContent']
    soup = BeautifulSoup(html_content, 'html.parser')
    content =  soup.get_text(separator='\n', strip=True)
    # Title
    title = data['res'].get('title', '')
    # Forum
    forum = data['res']['thisForum']['txtTitle']

    articles_dict.append({
        'title': title,
        'content': content, 
        'forum': forum
    })
    return articles_dict

# %%
def fetch(page):
    page = str(page)
    articles_dict = []
    article_list = fetch_article_list(page)
    for article in article_list:
        url =  article['url']
        all_articles = fetch_article_content(url)
    return all_articles
    


