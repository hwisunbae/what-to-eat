# Need to run -> ngrok http 5000 

import os
import random

from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, Request, Response

# ------ Authorize google spread sheet 
import gspread
gc = gspread.service_account(filename='./.config/gspread/service_account.json')
sh = gc.open("lunchbot")
worksheet = sh.sheet1

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

CHANNEL_NAME = 'test2'
# DEBUG
client.chat_postMessage(channel=CHANNEL_NAME, text='App started')

# attachments colours
COLOURS = ['#36a64f', '#eefc54', '#ef8432', '#d72e1f']
PHOTOS = ['https://i.imgur.com/ZrZLmZa.png','https://imgur.com/TYNURtM.png',
		  'https://i.imgur.com/Sxjrtso.png', 'https://imgur.com/1nFZsc7.png',
		  'https://i.imgur.com/aUELdkg.png', 'https://imgur.com/co2D9cl.png',
		  '','',
		  '','',
		  '','',
		  '','']

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
@app.route('/eat', methods=['POST'])
def message_count():

	# Rander 4 out of the lists
	lists = worksheet.col_values(1)[1::]
	num_to_select = len(COLOURS)
	selected_items = random.sample(lists, num_to_select)
	print(selected_items)

	for index, item in enumerate(selected_items):
		row = worksheet.row_values(item)
		client.chat_postMessage(channel=CHANNEL_NAME, 
			attachments=[{
				"title": row[1],
	            "title_link": row[2],
				'fields': [
					{
						"title": "Menu Recommended", 
						"value": row[4] + ' ' + row[5], 
						"mrkdwn_in":["text"],
						'short': True
					}, {
						"title": "Thumb Signal", 
						"value": ":thumbsup: " + '0' + '       :thumbsdown: ' + '0', 
						'short': True
					}
				],
				"color": COLOURS[index],
				"thumb_url": PHOTOS[int(row[6])],
			}]
		)

	return Response(), 200

if __name__ == '__main__':
	app.run(debug=True)