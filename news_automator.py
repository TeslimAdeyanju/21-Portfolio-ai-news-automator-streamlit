import requests
from sys import argv

import os
from dotenv import load_dotenv

# load the .env file into environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY")


URL = ('https://newsapi.org/v2/top-headlines?')


def get_articles_by_category(category):
    query_parameters = {
        "category": category,
        "country": "us",
        "apiKey": API_KEY
    }
    return _get_articles(query_parameters)


def get_articles_by_query(query):
    query_parameters = {
        "q": query,
        "country": "us",
        "apiKey": API_KEY
    }
    return _get_articles(query_parameters)


def _get_articles(params):
    response = requests.get(URL, params=params)
    
    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code}")
        return
    
    data = response.json()
    
    if data['status'] != 'ok':
        print(f"Error: API returned status '{data['status']}'")
        return
    
    articles = data['articles']
    
    if not articles:
        print("No articles found for this query.")
        return

    results = []
        
    for article in articles:
        results.append({"title": article["title"], "url": article["url"]})

    for result in results:
        print(result['title'])
        print(result['url'])
        print('')


def get_sources_by_category(category):
    url = 'https://newsapi.org/v2/top-headlines/sources'
    query_parameters = {
        "category": category,
        "language": "en",
        "apiKey": API_KEY
    }

    response = requests.get(url, params=query_parameters)

    sources = response.json()['sources']

    for source in sources:
        print(source['name'])
        print(source['url'])


if __name__ == "__main__":
    print(f"Getting news for {argv[1]}...\n")
    get_articles_by_category(argv[1])
    print(f"Successfully retrieved top {argv[1]} headlines")
    # get_articles_by_query("Liz Truss")
    # print_sources_by_category("technology")
