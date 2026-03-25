import requests
import urllib3
urllib3.disable_warnings()

s = requests.Session()
s.verify = False

# Login
r = s.get('https://www.stockmarket.aero/StockMarket/LoadLogin.do', timeout=30)
from bs4 import BeautifulSoup
soup = BeautifulSoup(r.text, 'html.parser')
form = soup.find('form')
action = form.get('action')
data = {'username': 'sale@aeroedgeglobal.com', 'password': 'Aa138222', 'rememberMe': 'on', 'group1': 'signIn'}
s.post('https://www.stockmarket.aero' + action, data=data, timeout=30, allow_redirects=True)

# Get the popup_functions.js to understand the RFQ flow
jr = s.get('https://www.stockmarket.aero/StockMarket/js/popup_functions.js', timeout=15)
# Print relevant sections
lines = jr.text.split('\n')
printing = False
for i, line in enumerate(lines):
    if 'showitemdetailpopup' in line.lower() and 'function' in line.lower():
        printing = True
    if printing:
        print(lines[i])
        if i > 0 and line.strip() == '}' and printing:
            printing = False
            print('---')
    # Also look for URL/ajax/submit
    if any(kw in line.lower() for kw in ['submitrfq', 'sendrfq', 'rfqaction', 'rfq.do', 'ajax']):
        print('>> ', line.strip()[:200])
