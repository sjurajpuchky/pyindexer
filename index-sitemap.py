import sys
from datetime import datetime

from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import json
from alive_progress import alive_bar

from usp.tree import sitemap_tree_for_homepage


def parse_sitemap(home_url):
    urls = []
    tree = sitemap_tree_for_homepage(home_url)
    for page in tree.all_pages():
        urls.append(page.url)
    return urls


if len(sys.argv) < 4:
    print("Usage: index-sitemap.py key.json https://www.nekde.cz 0")
    exit(1)

JSON_KEY_FILE = sys.argv[1]

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Authorize credentials
credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

urls = parse_sitemap(sys.argv[2])
urls = list(set(urls))
print('Found ' + str(len(urls)) + ' urls')
counter = 0
with alive_bar(len(urls), force_tty=True) as bar:
    for url in urls:
        if counter >= int(sys.argv[3]):
            content = {}
            content['url'] = url
            content['type'] = 'URL_UPDATED'
            json_content = json.dumps(content)

            response, content = http.request(ENDPOINT, method="POST", body=json_content)
            print(content)
            result = json.loads(content.decode())
        counter += 1
        bar()
