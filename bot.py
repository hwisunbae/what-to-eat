# Need to run -> ngrok http 5000 

import os

from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, Request, Response

# ------ Authorize google spread sheet 
import gspread
gc = gspread.service_account(filename='./.config/gspread/service_account.json')
sh = gc.open("lunchbot")

# Keep variables safe
env_path = Path('.')  / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Slack App credentials for OAuth
SLACK_CLIENT_ID = os.environ["SLACK_CLIENT_ID"]
SLACK_CLIENT_SECRET = os.environ["SLACK_CLIENT_SECRET"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)


client = WebClient(SLACK_BOT_TOKEN)
BOT_ID = client.api_call('auth.test')['user_id']



# DEBUG
client.chat_postMessage(channel='test2', text='App started')

# An example of one of your Flask app's routes
@app.route("/")
def hello():
  return "Hello there!"

# Create an event listener for "message"
@slack_events_adapter.on("message")
def handle_message(event_data):
	message = event_data.get('event')
	team_id = message.get('channel')
	text  = message.get('text')
	user_id = message.get('user')

	print(team_id, text, user_id)

	if BOT_ID != user_id:
		client.chat_postMessage(channel=team_id, text=text)

# TODO: lunch-vote should take data from a google sheet and list all items and let the user to vote
@app.route('/lunch-vote', methods=['POST'])
def message_count():
	print(sh.sheet1.get('A1'))
	return Response(), 200

if __name__ == '__main__':
	app.run(debug=True)