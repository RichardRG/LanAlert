'''COPYRIGHT 2018 RATEGENIUS LOAN SERVICES INC. '''

import _mssql
import uuid
import decimal
import requests
import pymssql
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import json

def sqlquery(query,username,password,server,database='lansweeperdb'):
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

with open('config.cfg','r') as configimport:
    config = json.load(configimport)

logfile = open('lanalert.log','a')

print config['logo']['mainlogo']

username = config['database']['username']
password = config['database']['password']
server = config['database']['server']

slacktoken = config['slacktoken']
ticketchannel = config['channel']
slackusername = config['slackbotusername']

url = config['webaddress']

startctcnquery = '''SELECT  
        ( SELECT TOP 1 MAX(htblticket.ticketid) as "Col 1"  
        FROM [lansweeperdb].[dbo].[htblticket]) AS col1,  
        (SELECT TOP 1 MAX(htblnotes.noteid) as "Col 2"  
        FROM [lansweeperdb].[dbo].[htblnotes]) as col2'''

ticketquery = '''SELECT TOP %s  
          htblticket.ticketid, 
          htblticket.subject, 
          htblusers.name, 
          htblnotes.note,  
          htblnotes.noteid  
          FROM [lansweeperdb].[dbo].[htblticket]  
          inner join lansweeperdb.dbo.htblnotes On htblticket.ticketid = htblnotes.ticketid  
          inner Join lansweeperdb.dbo.htblusers On htblticket.fromuserid = htblusers.userid  
          WHERE notetype=3 ORDER BY ticketid DESC'''

notequery = '''SELECT TOP %s  
          htblticket.ticketid, 
          htblticket.subject,  
          htblusers.name, 
          htblnotes.note,  
          htblticket.agentid,  
          htblnotes.userid,  
          htblnotes.noteid,  
          htblnotes.notetype  
          FROM [lansweeperdb].[dbo].[htblticket]  
          inner join lansweeperdb.dbo.htblnotes On htblticket.ticketid = htblnotes.ticketid  
          inner Join lansweeperdb.dbo.htblusers On htblticket.fromuserid = htblusers.userid  
          ORDER BY noteid DESC'''

agentquery = '''SELECT  
            htblagents.agentid, 
            htblagents.userid, 
            tblADusers.Info  
            FROM [lansweeperdb].[dbo].[htblagents]  
            LEFT JOIN htblusers on htblusers.userid = htblagents.userid  
            LEFT JOIN tblADusers on htblusers.username = tblADusers.Username  
            WHERE active = 1'''
slackid = {}
agenttouser = {}

#Sets agents slack id from agent config and user config in lansweeper, slack ID comes from
try:
    for agent in sqlquery(agentquery,username,password,server):
        slackid[str(agent[0])] = agent[2]
        agenttouser[str(agent[0])] = str(agent[1])
except Exception as e:
    logfile.write('Config - Error setting slack and agent table ' + str(e) + '\n')
    
currentticket,currentnote = sqlquery(startctcnquery, username, password, server)[0]
try:
    while True:
        date = datetime.now().date().strftime("%Y-%m-%d")
        time = datetime.now().time().strftime("%H:%M:%S")
        try:
            outputticket = []
            newticket = sqlquery(startctcnquery, username, password, server)[0][0]
            #Check for new ticket
            if newticket > currentticket:
                #Queries all new tickets
                tickets = sqlquery(ticketquery % str(int(newticket) - int(currentticket)), username, password, server)
                currentticket = newticket
                for ticket in tickets:
                    # Strips HTML and signature from emails and returns clean body
                    body = soup(ticket[3])
                    # Formats clickable link for slack
                    ticketlink = '<'+ url + '%s | Ticket %s %s>' % (ticket[0],ticket[0],ticket[1])
                    # formats subject
                    subject = '*%s* \n *From: %s --* \n' % (ticketlink,ticket[2])
                    outputticket.append(subject + body)
            else:
                print date + ' - ' + time + ' - Pass Ticket'
            for messages in outputticket:
                #Sends all new tickets to the main channel
                response = posttoslack(messages, slacktoken, ticketchannel, slackusername, server)
                if str(response['ok']).lower() != 'true':
                    logfile.write(date + ' - ' + time + ' - Tickets - ' + str(response) + '\n')
        except Exception as e:
            logfile.write(date + ' - ' + time + ' - Tickets Error - ' + str(e) + '\n')
        try:
            outputnote = []
            #Queries the latest note
            newnote = sqlquery(startctcnquery, username, password, server)[0][1]
            #Checks if there is a new note
            if newnote > currentnote:
                notes = sqlquery(notequery % str(int(newnote) - int(currentnote)), username, password, server)
                currentnote = newnote
                for note in notes:
                    # Adds all notes that are not from agents to the outputnote var
                    if str(note[5]) not in agenttouser.values():
                        #Strips HTML and signature from emails and returns clean body
                        body = soup(note[3])
                        #Formats clickable link for slack
                        notelink = '<'+ url + '%s | Update on Ticket %s %s>' % (note[0], note[0], note[1])
                        #formats subject
                        subject = '*%s* \n *From: %s --* \n' % (notelink, note[2])
                        outputnote.append([subject+body,note[4]])

            else:
                print date + ' - ' + time + ' - Pass Note'
            #Digests outputnote
            if outputnote:
                for message in outputnote:
                    #Determines if an agent has been assigned, if not updates go to the main channel
                    if message[1]:
                        channelid = openslackchannel(slackid[str(message[1])],slacktoken)
                    else:
                        channelid = {"ok":"true", "channel":{"id":ticketchannel}}
                    #Sends formatted note to the agent or main channel
                    if str(channelid['ok']).lower() == 'true':
                        response = posttoslack(message[0],slacktoken,channelid['channel']['id'],slackusername)
                        if str(response['ok']).lower() != 'true':
                            logfile.write(date + ' - ' + time + ' -  Notes - ' + str(response) + '\n')
                    else:
                        logfile.write(date + ' - ' + time + ' -  Notes - ' + str(channelid) + '\n')
        except Exception as e:
            logfile.write(date + ' - ' + time + ' - Notes Error - ' + str(e) + '\n')
        sleep(40)
finally:
    logfile.close()
