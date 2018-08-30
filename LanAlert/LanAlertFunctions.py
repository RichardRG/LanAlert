'''COPYRIGHT 2018 RATEGENIUS LOAN SERVICES INC. '''

import _mssql
import uuid
import decimal
import requests
import pymssql
from bs4 import BeautifulSoup

def sqlquery(query,username,password,server='Your SQL Server',database='lansweeperdb'):
    data = []
    conn = pymssql.connect(server, username, password, database)
    cursor = conn.cursor()
    cursor.execute(query)
    for row in cursor:
        data.append(row)
    conn.close()
    return data

def soup(htmlstring):
    #Cleans out signatures from notes.
    presoup = htmlstring.split("<div><div><div>")[0]
    presoup = presoup.split("<br><div>On")[0]
    presoup = presoup.split('--')[0]
    presoup = presoup.replace('<br style="">','\n').replace('<div','\n<div').replace('<p','\n<p')
    soup = BeautifulSoup(presoup, "html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("   "))
    # drop blank lines"""
    text = '\n'.join(chunk for chunk in chunks if chunk)
	return text

def posttoslack(body,token,channel,username,icon='',unfurl='true'):
    payload = {
        'token': token,
        'channel': channel,
        'unfurl_links': unfurl,
        'username': username,
        'icon_url': icon,
        'text': body
    }
    r = requests.post('https://slack.com/api/chat.postMessage', payload)
    return r.json()
def openslackchannel(user,token):
    payload = {
        'token':token,
        'user':user
    }
    r = requests.post('https://slack.com/api/im.open', payload)
    return r.json()
