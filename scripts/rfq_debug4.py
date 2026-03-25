import requests
import urllib3, re
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

# Get JS to find submitRfqAjax
jr = s.get('https://www.stockmarket.aero/StockMarket/js/popup_functions.js', timeout=15)
lines = jr.text.split('\n')

# Print submitRfqAjax function
printing = False
brace_count = 0
for line in lines:
    if 'function submitRfqAjax' in line:
        printing = True
        brace_count = 0
    if printing:
        print(line.rstrip())
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0 and '{' in line or (brace_count == 0 and '}' in line):
            if line.strip() == '}':
                printing = False
                print('---END---')
                break

print('\n\n=== submitRFQ ===')
printing = False
for line in lines:
    if 'function submitRFQ' in line:
        printing = True
        brace_count = 0
    if printing:
        print(line.rstrip())
        brace_count += line.count('{') - line.count('}')
        if brace_count <= 0 and line.strip() == '}':
            printing = False
            print('---END---')
            break

# Now try loading the RFQ form
print('\n\n=== Loading RFQ Form ===')
idMap = '{sysStmKey=4690668475, searchKey=245947, rowId=0}'
url = 'https://www.stockmarket.aero/StockMarket/LoadItemDetailAction.do'
r2 = s.get(url, params={'actiontype': 'rfq', 'idMap': idMap}, timeout=30)
print('Status:', r2.status_code)
print('Length:', len(r2.text))

soup2 = BeautifulSoup(r2.text, 'html.parser')
for f in soup2.find_all('form'):
    act = f.get('action', '')
    met = f.get('method', '')
    fid = f.get('id', '')
    print('Form: action=%s method=%s id=%s' % (act, met, fid))
    for inp in f.find_all(['input', 'textarea', 'select']):
        tag = inp.name
        n = inp.get('name', '')
        t = inp.get('type', '')
        v = str(inp.get('value', ''))[:60]
        if tag == 'textarea':
            v = inp.get_text()[:60]
        print('  %s: name=%s type=%s value=%s' % (tag, n, t, v))
