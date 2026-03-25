import requests
from bs4 import BeautifulSoup
import urllib3, re
urllib3.disable_warnings()

s = requests.Session()
s.verify = False

# Login
r = s.get('https://www.stockmarket.aero/StockMarket/LoadLogin.do', timeout=30)
soup = BeautifulSoup(r.text, 'html.parser')
form = soup.find('form')
action = form.get('action')
data = {'username': 'sale@aeroedgeglobal.com', 'password': 'Aa138222', 'rememberMe': 'on', 'group1': 'signIn'}
s.post('https://www.stockmarket.aero' + action, data=data, timeout=30, allow_redirects=True)

# Get search page with expand all
r = s.get('https://www.stockmarket.aero/StockMarket/SearchAction.do', params={
    'theAction': 'expandAll', 'partNumber': '822-0990-002', 'partial': 'false'
}, timeout=30)
soup = BeautifulSoup(r.text, 'html.parser')

# Find all JS files and the showitemdetailpopup function
for script in soup.find_all('script', src=True):
    src = script.get('src', '')
    if 'popup' in src.lower() or 'detail' in src.lower() or 'item' in src.lower():
        print('JS file:', src)

# Find inline scripts with showitemdetailpopup
for script in soup.find_all('script'):
    if script.string and 'showitemdetailpopup' in script.string.lower():
        lines = script.string.split('\n')
        for line in lines:
            if 'showitemdetailpopup' in line.lower() or 'loaditemdetail' in line.lower() or 'url' in line.lower():
                print('JS:', line.strip()[:200])

# Search in all JS files
for script in soup.find_all('script', src=True):
    src = script.get('src', '')
    if src.startswith('/') or src.startswith('js/'):
        full_url = 'https://www.stockmarket.aero/StockMarket/' + src.lstrip('/')
        try:
            jr = s.get(full_url, timeout=15)
            if 'showitemdetailpopup' in jr.text.lower():
                print('\nFound in:', src)
                for line in jr.text.split('\n'):
                    if 'showitemdetailpopup' in line.lower():
                        print('  ', line.strip()[:300])
        except:
            pass
