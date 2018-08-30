# LanAlert
Integration for ticket notifications between Lansweeper and Slack.

### Setup

To use this program edit config.cfg with your information (you will need a slack bot configured)

It is recommended to use pyinstaller to create an EXE and run it on your Lansweeper server. 

You may also want to add more filtering to the soup function in LanAlertFunctions.py this is a very dirty function to clear signatures off tickets.

REQUIRED LIBRARIES:

requests
pymssql
bs4