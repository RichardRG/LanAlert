# LanAlert
Integration for ticket notifications between Lansweeper and Slack.

### Setup

To use this program edit config.cfg with your information (you will need a slack bot configured).

A packaged .exe is provided under the executable folder, configure and run!

For more advanced users, if you are getting signatures passed through to slack, edit the source for the "soup" function and add identifiable features for your companies signature line. 

REQUIRED LIBRARIES:

requests

pymssql

bs4
