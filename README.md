
# What To Eat

# 💡 Topic

- **A slack bot that picks lunch for your team**
- Integration with google spread sheet that has a list of several nearby restaurants

# 📝 Summary

While working for CaseWare International Inc., my team went out for lunch rather than packing their lunch every Friday. The team had to talk about where to go and what to eat for lunch 30 mins before lunch time. So, I came up with an idea of a slack lunch bot which displays a list of nearby restaurants with main menu. This lunch bot randomly picks up 4 places from a linked google sheet, counts votes and displays which one get the most votes.



# PIPENV PACKAGE MANAGER 
```
# installs package python pipenv package manager
pip3 install pipenv 

# to install all required dependencies for project
pipenv install

# to enter pipenv virtual env subshell, has all packages installed from Pipfile in this environment (separate from main shell environment)
# type exit in terminal if want to exit pipenv shell
pipenv shell

# to add new packages to Pipfile
pipenv install package1 package2 
```

# GOOGLE SERVICE ACCOUNT CREDENTIALS
```
# credentials are loaded in loadCredentials.py
# should be in local project directory root level
```
# ngrok (local web server) https://ngrok.com/download
```
# To run local web server for development
# WARNING: ngrok url will change everytime you restart webserver
#          change redirect URL in the lunch bot's app everytime
./ngrok http (any available port #) e.g. ./ngrok http 6767
```
![image](https://user-images.githubusercontent.com/31826240/117553049-2c609780-b01d-11eb-8dae-808420bf9918.png)


# Configure request URL 
To run the local development.. you need to configure request URL in Slash Commands, Interactivity & Shortcuts, Event Subscription.

e.g 
Event Subscriptions > Enable Events
Request URL : https://request_url.io/slack/events

Slash Commands > /what_to_eat
Request URL : https://request_url.io/whattoeat

Interactivity & Shortcuts
Request URL : https://request_url.io/slack/message_actions




# Further Development
1. Schedule  message before lunch using schcdule_messages
