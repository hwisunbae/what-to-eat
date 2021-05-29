# Need to run -> ngrok http 5000 

import os
import random
import json

from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, Response, make_response, request
from datetime import datetime, timedelta

from WelcomeMessage import *

# Authorize google spread sheet 
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

# DEBUG 
CHANNEL_NAME = 'test2'
client.chat_postMessage(channel=CHANNEL_NAME, text='App started')

# TODO: further dev
message_counts = {}
welcome_messages = {}
SCHEDULED_MESSAGES = [
	{'text': 'first one', 'post_at': (datetime.now() + timedelta(seconds=40)).timestamp(), 'channel': 'C023502CL2D'}, 
	{'text': 'second one', 'post_at': (datetime.now() + timedelta(seconds=50)).timestamp(), 'channel': 'C023502CL2D'}
]

# Resources
COLOURS = ['#36a64f', '#eefc54', '#ef8432', '#d72e1f']
PHOTOS = ['https://i.imgur.com/ZrZLmZa.png','https://i.imgur.com/TYNURtM.png',
		  'https://i.imgur.com/Sxjrtso.png','https://i.imgur.com/1nFZsc7.png',
		  'https://i.imgur.com/aUELdkg.png','https://i.imgur.com/co2D9cl.png',
		  'https://i.imgur.com/Qwo5n0U.png','https://i.imgur.com/mOg1t1r.png',
		  'https://i.imgur.com/Vb0ve9u.png','https://i.imgur.com/95FYmFe.png',
		  'https://i.imgur.com/0jxjDrc.png','https://i.imgur.com/kdyBfuB.png',
		  'https://i.imgur.com/55Pbyvu.png','https://i.imgur.com/YNj8Ikc.png']

# An example of one of your Flask app's routes
@app.route("/")
def hello():
  return "You are connected!"


# TODO: lunch-vote should take data from a google sheet and list all items and let the user to vote
@app.route('/whattoeat', methods=['POST'])
def handle_eat():

	data = request.form
	channel_id = data.get('channel_id')

	# Rander 4 out of the lists
	lists = worksheet.col_values(1)[1::]
	num_to_select = len(COLOURS)
	global selected_items
	selected_items = random.sample(lists, num_to_select)
	print(selected_items) #['6', '9', '5', '7']

	for index, item in enumerate(selected_items):
		row = worksheet.row_values(item)
		client.chat_postMessage(
			channel = channel_id, 
			attachments = [{
				"title": row[1],
	            "title_link": row[2],
                "fallback": "Upgrade your Slack client to use messages like these.",
        		"callback_id": f"menu_{index}",
				'fields': [
					{
						"title": ":fire: Menu Recommended", 
						"value": row[4] + ' ' + row[5],
						'short': True
					}, {
						"title": ":walking: Distance", 
						"value": row[6], 
						'short': True
					}, 
				],
				"actions": [
	                {
	                    "name": f"thumbs_up_{index}",
	                    "text": ":thumbsup:",
	                    "type": "button",
	                    "value": f"thumbs_up_{index}",
	                    "style": "primary",
	                    "data_source": "external",
	                    "action_id": "up_vote"
	                },
	                {
	                    "name": f"thumbs_down_{index}",
	                    "text": ":thumbsdown:",
	                    "type": "button",
	                    "value":  f"thumbs_down_{index}",
	                    "style": "danger",
	                    "action_id": "down_vote"
	                }
	            ],
				"color": COLOURS[index],
				"thumb_url": PHOTOS[int(row[7])-1],
			}]
		)

	return Response(), 200

global selections
selections = {}

@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
	form_json = json.loads(request.form.get('payload'))
	selection = form_json['actions'][0]['value']
	print(selection)

	if selection not in selections:
		selections[selection] = 1
	else:
		selections[selection] += 1
	print(selections)
	return Response(), 200


# https://api.slack.com/best-practices/blueprints/actionable-notifications
@app.route('/check_vote', methods=['POST'])
def handle_check():
	data = request.form	
	channel_id = data.get('channel_id')

	# TODO: emoji thumbsup and down, connect them to responding menus
	fields = [{'title': title, 'value': vote, 'short': True} for title, vote in selections.items()]

	print(fields)
	client.chat_postMessage(
		channel = channel_id, 
		attachments = [{
			"title": ':ballot_box_with_ballot: Votes for selected menus',
            "fallback": "Upgrade your Slack client to use messages like these.",
    		"callback_id": 'check votes',
			'fields': fields,
			"color": '#EE82EE',
			"thumb_url":'https://i.imgur.com/Ynmyz2n.png'
		}]
	)
	return Response(), 200

if __name__ == '__main__':
	# schcdule_messages(SCHEDULED_MESSAGES)
	app.run(port=5000, debug=True)
	