
import requests
from bs4 import BeautifulSoup
import json
import time
import sys
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import codecs
from slugify import slugify
import os
import re

file = codecs.open("article-links.json", "r", "utf_8_sig")
article_refs = json.load(file)
file.close()

# Switching user agents is enough to trick msdn bot detection
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
ua = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agents = ua.get_user_agents()

def get_filename_for(article):
    cat = article['cat']
    return cat + '/' + slugify(article['title'])

articles_downloaded = 0
articles_total = len(article_refs)

# Download the contents of each article
for article in article_refs:
    # Create the folder for the article
    article_folder = get_filename_for(article)
    if not os.path.exists(article_folder):
        os.mkdir(article_folder)
    if os.path.exists(article_folder + '/index.html'):
        articles_downloaded += 1
        continue
    # Download the article content
    headers = HEADERS = {
        'User-Agent': ua.get_random_user_agent(),
        "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8",
        "Accept-Language": "en",
    }
    url = article['link']
    print("Downloading: " + url + ' (' + str(100 * articles_downloaded/articles_total) + '%)')
    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        print('ERROR: ' + url)
        print('CODE: ' + str(page.status_code))
        sys.exit(1)
    # Find the body of the article and clear it up
    soup = BeautifulSoup(page.content, "html.parser")
    content = soup.find('article').div.div
    [x.decompose() for x in content.findAll('div')]
    # Download the images from the article
    # ...
    # Replace the links to the same blog
    links = content.findAll('a')
    for link in links:
        try:
            if link['href'].startswith('https://devblogs.microsoft.com/oldnewthing/'):
                matched = False
                matched_a = None
                for a in article_refs:
                    to_match = a['link']
                    if link['href'] == to_match:
                        matched = True
                        matched_a = a
                        break
                if matched:
                    link['href'] = '/' + get_filename_for(matched_a)
            break
        except:
            continue
    # Wrap the article in <body> tag with a style so doesn't look as bad
    content = content.encode_contents().decode('utf-8')
    content = '<body style=max-width:80ch;margin:auto>' + content + '</body>'
    # Save the article
    f = codecs.open(article_folder + '/index.html', "w", "utf_8_sig")
    f.write(content)
    f.close()
    articles_downloaded += 1
