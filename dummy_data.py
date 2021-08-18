import json
import requests

from random import randrange, choice
from string import ascii_lowercase

BASE_API = 'http://localhost:5000/api/v1/'
NUM_CATEGORIES = 20
NUM_ITEMS = 400
MAX_NAME_LEN = 20
MAX_URL_LEN = 40
MAX_ACCOUNT_LEN = 20
MAX_USERNAME_LEN = 10

# Retrieve JWT access token
headers = {'Content-Type': 'application/json'}
body = {'username':'demo', 'password': 'demo', 'exp_delta': 3600}
r = requests.post(f'{BASE_API}/auth', data=json.dumps(body), headers=headers)
resp = json.loads(r.text)
jwt = resp['access_token']

# Generate categories
body = {'category_names': [f'category{i}' for i in range(NUM_CATEGORIES)]}
headers = {'Content-Type': 'application/json', 'x-opp-jwt': jwt, 'x-opp-phrase': 'phrase'}
r = requests.put(f'{BASE_API}/categories', data=json.dumps(body), headers=headers)
resp = json.loads(r.text)['categories']
categories = [cat['id'] for cat in resp]

# Generate items
items = []
for i in range(NUM_ITEMS):
    cat = categories[randrange(1,NUM_CATEGORIES)]
    name = ''.join(choice(ascii_lowercase) for i in range(MAX_NAME_LEN))
    url = ''.join(choice(ascii_lowercase) for i in range(MAX_URL_LEN))
    account = ''.join(choice(ascii_lowercase) for i in range(MAX_ACCOUNT_LEN))
    username = ''.join(choice(ascii_lowercase) for i in range(MAX_USERNAME_LEN))
    item = {'name': name, 'url': url, 'account': account, 'username': username, 'blob': '', 'category_id': cat}
    items.append(item)
body = {'items': items, 'auto_pass': True, 'unique': True}
headers = {'Content-Type': 'application/json', 'x-opp-jwt': jwt, 'x-opp-phrase': 'phrase'}
r = requests.put(f'{BASE_API}/items', data=json.dumps(body), headers=headers)
resp = json.loads(r.text)['result']
if resp == 'success':
    print('Successfully generated dummy data.')
else:
    print('Unable to generate dummy data!')
