import requests
from bs4 import BeautifulSoup
import urllib3
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

# Load RFQ form via LoadItemDetail.do
r2 = s.get('https://www.stockmarket.aero/StockMarket/LoadItemDetail.do', params={
    'sysStmKey': '4690668475',
    'searchKey': '245947',
    'rowId': '0',
    'type': 'rfq'
}, timeout=30)
print('Status:', r2.status_code)
soup2 = BeautifulSoup(r2.text, 'html.parser')

# Find all forms
for f in soup2.find_all('form'):
    act = f.get('action', '')
    met = f.get('method', '')
    fid = f.get('id', '')
    print('Form: action=%s method=%s id=%s' % (act, met, fid))
    for inp in f.find_all('input'):
        n = inp.get('name', '')
        t = inp.get('type', '')
        v = str(inp.get('value', ''))[:80]
        print('  Input: name=%s type=%s value=%s' % (n, t, v))
    for ta in f.find_all('textarea'):
        print('  Textarea: name=%s' % ta.get('name', ''))
    for sel in f.find_all('select'):
        print('  Select: name=%s' % sel.get('name', ''))

# Also print page title/content for debugging
title = soup2.find('title')
if title:
    print('Title:', title.get_text())

# Check for RFQ-related content
text = soup2.get_text()
if 'Reference' in text:
    print('Found Reference field')
if 'Quantity' in text:
    print('Found Quantity field')
if 'Submit' in text:
    print('Found Submit button')
