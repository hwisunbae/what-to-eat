from pathlib import Path
from dotenv import dotenv_values

# config = { "SLACK_TOKEN": "XXXXX" }
# dotenv_values returns a dictionary
# loads env variables to config dictionary e.g. SLACK_TOKEN
path_to_env = Path('.') / '.env'
config = dotenv_values(path_to_env)  

path_to_cred = Path('.') / config['CRED_FILENAME']
# adds path_to_cred to config dictionary e.g. CRED_PATH
config['CRED_PATH'] = path_to_cred
