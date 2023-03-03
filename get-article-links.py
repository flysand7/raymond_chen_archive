
import requests
from bs4 import BeautifulSoup
import json
import time
import sys
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

article_refs = []

# Switching user agents is enough to trick msdn bot detection
software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
ua = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
user_agents = ua.get_user_agents()

# Figure out the number of pages
page = requests.get("https://devblogs.microsoft.com/oldnewthing/author/oldnewthing")
soup = BeautifulSoup(page.content, "html.parser")
npages = int(list(soup.find(class_='page-numbers').children)[-4].a.text.strip())

# Find the article links on this page
for p in range(1, npages+1):
    headers = HEADERS = {
        'User-Agent': ua.get_random_user_agent(),
        "Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8",
        "Accept-Language": "en",
    }
    url = "https://devblogs.microsoft.com/oldnewthing/author/oldnewthing/page/" + str(p)
    print("checking out: " + url)
    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        print('ERROR: ' + url)
        print('CODE: ' + str(page.status_code))
        sys.exit(1)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find_all(class_='entry-content')
    for result in results:
        title = result.header.h2.a.text.strip()
        link = result.header.h2.a.attrs['href']
        category = 'none'
        if len(list(result.footer.div.div.div.children)) > 1:
            category = result.footer.div.div.div.span.span.a.text.strip().lower()
        article_refs.append({'page': p, 'title': title, 'link': link, 'cat': category})
    time.sleep(1)

print(article_refs)

with open("article-links.json", "w") as file:
    json.dump(article_refs, file)

# Find the next page and go to that


#print(article_refs)

