'''COPYRIGHT 2018 RATEGENIUS LOAN SERVICES INC. '''

from LanAlertFunctions import sqlquery,posttoslack,soup,openslackchannel
from time import sleep
from datetime import datetime
import json

config = {}
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

startctcnquery = 'SELECT ' \
        '( SELECT TOP 1 MAX(htblticket.ticketid) as "Col 1" ' \
        'FROM [lansweeperdb].[dbo].[htblticket]) AS col1, ' \
        '(SELECT TOP 1 MAX(htblnotes.noteid) as "Col 2" ' \
        'FROM [lansweeperdb].[dbo].[htblnotes]) as col2'

ticketquery = 'SELECT TOP %s ' \
          'htblticket.ticketid,' \
          'htblticket.subject,' \
          'htblusers.name,' \
          'htblnotes.note, ' \
          'htblnotes.noteid ' \
          'FROM [lansweeperdb].[dbo].[htblticket] ' \
          'inner join lansweeperdb.dbo.htblnotes On htblticket.ticketid = htblnotes.ticketid ' \
          'inner Join lansweeperdb.dbo.htblusers On htblticket.fromuserid = htblusers.userid ' \
          'WHERE notetype=\'3\' ORDER BY ticketid DESC'

notequery = 'SELECT TOP %s ' \
          'htblticket.ticketid,' \
          'htblticket.subject, ' \
          'htblusers.name,' \
          'htblnotes.note, ' \
          'htblticket.agentid, ' \
          'htblnotes.userid, ' \
          'htblnotes.noteid, ' \
          'htblnotes.notetype ' \
          'FROM [lansweeperdb].[dbo].[htblticket] ' \
          'inner join lansweeperdb.dbo.htblnotes On htblticket.ticketid = htblnotes.ticketid ' \
          'inner Join lansweeperdb.dbo.htblusers On htblticket.fromuserid = htblusers.userid ' \
          'ORDER BY noteid DESC'

currentticket,currentnote = sqlquery(startctcnquery, username, password, server)[0]
try:
    while True:
        date = datetime.now().date().strftime("%Y-%m-%d")
        time = datetime.now().time().strftime("%H:%M:%S")
        try:
            outputticket = []
            newticket = sqlquery(startctcnquery, username, password, server)[0][0]
            if newticket > currentticket:
                tickets = sqlquery(ticketquery % str(int(newticket) - int(currentticket)), username, password, server)
                currentticket = newticket
                for ticket in tickets:
                    body = soup(ticket[3])
                    ticketlink = '<'+ url + '%s | Ticket %s %s>' % (ticket[0],ticket[0],ticket[1])
                    subject = '*%s* \n *From: %s --* \n' % (ticketlink,ticket[2])
                    outputticket.append(subject + body)
            else:
                print date + ' - ' + time + ' - Pass Ticket'
            for messages in outputticket:
                response = posttoslack(messages, slacktoken, ticketchannel, slackusername, server)
                if str(response['ok']).lower() != 'true':
                    logfile.write(date + ' - ' + time + ' - Tickets - ' + str(response) + '\n')
        except Exception as e:
            logfile.write(date + ' - ' + time + ' - Tickets Error - ' + str(e) + '\n')
        try:
            outputnote = []
            newnote = sqlquery(startctcnquery, username, password, server)[0][1]
            if newnote > currentnote:
                notes = sqlquery(notequery % str(int(newnote) - int(currentnote)), username, password, server)
                currentnote = newnote
                for note in notes:
                    if str(note[5]) not in config['users']['userid'].values():
                        body = soup(note[3])
                        notelink = '<'+ url + '%s | Update on Ticket %s %s>' % (note[0], note[0], note[1])
                        subject = '*%s* \n *From: %s --* \n' % (notelink, note[2])
                        outputnote.append([subject+body,note[4]])

            else:
                print date + ' - ' + time + ' - Pass Note'
            if outputnote:
                for message in outputnote:
                    channelid = openslackchannel(config['users']['slackid'][str(message[1])],slacktoken)
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
