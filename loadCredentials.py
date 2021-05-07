# config.py import config-dictionary
from config import config
import gspread

# credentials to load and authorize gspread w/ the slack-lunch-bot google service account
# json file not placed on repo, but in local project directory
gc = gspread.service_account(filename=config['CRED_PATH'])
sheet = gc.open("slack-bot-test-sheet")
# prints hello text in the first cell
print(sheet.sheet1.get("A1"))
