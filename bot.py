# Need to run -> ngrok http 5000 

import os
import random

from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask, Request, Response

from WelcomeMessage import *

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

# DEBUG
CHANNEL_NAME = 'test2'
client.chat_postMessage(channel=CHANNEL_NAME, text='App started')

message_counts = {}
welcome_messages = {}

# resources
COLOURS = ['#36a64f', '#eefc54', '#ef8432', '#d72e1f']
PHOTOS = ['https://i.imgur.com/ZrZLmZa.png','https://i.imgur.com/TYNURtM.png',
		  'https://i.imgur.com/Sxjrtso.png','https://i.imgur.com/1nFZsc7.png',
		  'https://i.imgur.com/aUELdkg.png','https://i.imgur.com/co2D9cl.png',
		  'https://i.imgur.com/Qwo5n0U.png','https://i.imgur.com/mOg1t1r.png',
		  'https://i.imgur.com/Vb0ve9u.png','https://i.imgur.com/95FYmFe.png',
		  'https://i.imgur.com/0jxjDrc.png','https://i.imgur.com/kdyBfuB.png',
		  'https://i.imgur.com/55Pbyvu.png','https://i.imgur.com/YNj8Ikc.png']



def send_welcome_message(channel, user):
	welcome = WelcomeMessage(channel, user)
	message = welcome.get_message()
	response = client.chat_postMessage(**message)
	welcome.timestamp = response['ts']

	if channel not in welcome_messages:
		welcome_messages[channel] = {}
	welcome_messages[channel][user] = welcome

# An example of one of your Flask app's routes
@app.route("/")
def hello():
  return "You are connected!"

# Create an event listener for "message"
@slack_events_adapter.on("message")
def handle_message(payload):
	message = payload.get('event')
	channel_id = message.get('channel')
	text  = message.get('text')
	user_id = message.get('user')

	# print(channel_id, text, user_id)

	if user_id != None and BOT_ID != user_id:
		if user_id in message_counts:
			message_counts[user_id] += 1
		else:
			message_counts[user_id] = 1

		if text.lower() == 'start':
			send_welcome_message(channel_id, user_id)


# TODO: lunch-vote should take data from a google sheet and list all items and let the user to vote
@app.route('/whattoeat', methods=['POST'])
def handle_eat():

	# Rander 4 out of the lists
	lists = worksheet.col_values(1)[1::]
	num_to_select = len(COLOURS)
	selected_items = random.sample(lists, num_to_select)
	print(selected_items)

	for index, item in enumerate(selected_items):
		row = worksheet.row_values(item)
		client.chat_postMessage(
			channel = CHANNEL_NAME, 
			attachments = [{
				"title": row[1],
	            "title_link": row[2],
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
	                    "name": "approve_button",
	                    "text": ":thumbsup:",
	                    "type": "button",
	                    "value": "thumbs_up",
	                    "style": "primary"
	                },
	                {
	                    "name": "vote",
	                    "text": ":thumbsdown:",
	                    "type": "button",
	                    "value": "thumb_down",
	                    "style": "danger",
	                    "confirm": {
	                        "title": "Are you sure?",
	                        "text": "Wouldn't you want to go to this place?",
	                        "ok_text": "Yes",
	                        "dismiss_text": "No"
	                    }
	                }
	            ],
				"color": COLOURS[index],
				"thumb_url": PHOTOS[int(row[7])-1],
			}]
		)

	return Response(), 200

@slack_events_adapter.on('reaction_added')
def reaction(payload):
	message = payload.get('event')
	channel_id = message.get('item').get('channel')
	text  = message.get('text')
	user_id = message.get('user')

	print(message, channel_id, text, user_id)

	if channel_id not in welcome_messages:
		return

	welcome = welcome_messages[channel_id][user_id]
	welcome.completed = True
	welcome.channel = channel_id
	message = welcome.get_message()
	updated_message = client.chat_update(**message)
	welcome.timestamp = updated_message['ts']



# https://api.slack.com/best-practices/blueprints/actionable-notifications
@app.route('/vote', methods=['POST'])
def webhook():
	print(Request.data)
	return Response(), 200

if __name__ == '__main__':
	app.run(port=5000, debug=True)