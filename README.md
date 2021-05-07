# lunchbot

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
./ngrok http (any available port #) e.g. ./ngrok http 80
```
![image](https://user-images.githubusercontent.com/31826240/117517669-b7cd2080-af6a-11eb-83b4-609a29c9e1d2.png)
