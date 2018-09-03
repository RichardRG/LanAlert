'''COPYRIGHT 2018 RATEGENIUS LOAN SERVICES INC. '''

import json
import requests
with open('config.cfg','r') as configimport:
    config = json.load(configimport)

slacktoken = config['slacktoken']
def userlookup(search,token):
    output = []
    out2 = []
    payload = {
        'token': token,
    }
    r = requests.get('https://slack.com/api/users.list', payload)
    for x in r.json()['members']:
        output.append([x['id'], x['profile']['real_name'], x['name'], x['profile']['display_name_normalized']])
    for x in output:
        if search.lower() in x[1].lower() or search.lower() in x[2].lower() or search.lower() in x[3].lower():
            out2.append(x)
    return out2

while True:
    lookupname = raw_input('Enter search term: ')
    print userlookup(lookupname,slacktoken)