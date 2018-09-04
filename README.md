# LanAlert
Integration for ticket notifications between Lansweeper and Slack.

### Setup

To use this program edit config.ini with your information (you will need a slack bot configured).

Make sure that all Slack users have their email address configured in their profile. 

Your slack bot will need the following permissions. 

![Slack Permissions](https://raw.githubusercontent.com/RichardRG/LanAlert/master/Images/permissions.png)

A packaged .exe is provided under the executable folder, configure and run!

For more advanced users, if you are getting signatures passed through to Slack, edit the source for the "soup" function and add identifiable features for your companies signature line. 

REQUIRED LIBRARIES:

requests

pymssql

bs4
