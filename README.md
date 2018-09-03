# LanAlert
Integration for ticket notifications between Lansweeper and Slack.

### Setup

To use this program edit config.cfg with your information (you will need a slack bot configured).

You will need to find the Slack ID for each agent you have configured. I have attached a short script to search for them please add the following permissions and fill in the Slackbot oauth token in the config before running . The SlackID needs to be set in the "info" field in AD or the same field in lansweeper for the user.  

Your slack bot will need the following permissions. 

![Slack Permissions](https://raw.githubusercontent.com/RichardRG/LanAlert/master/Images/permissions.png)

A packaged .exe is provided under the executable folder, configure and run!

For more advanced users, if you are getting signatures passed through to Slack, edit the source for the "soup" function and add identifiable features for your companies signature line. 

REQUIRED LIBRARIES:

requests

pymssql

bs4
