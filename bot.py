# Need to run -> ngrok http 5000

import os
import random
import json

# config contains .env file attributes
from config import config
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
# from slackeventsapi import SlackEventAdapter
from slack_sdk.errors import SlackApiError
from flask import Flask, Response, make_response, request
from datetime import datetime, timedelta, date

from WelcomeMessage import *
from ActionMessage import *

# Authorize google spread sheet
import gspread
# gc = gspread.service_account(filename=config[CRED_FILENAME])
gc = gspread.service_account(filename='./service_account.json')
sh = gc.open("lunchbot")
worksheet = sh.worksheet('Sheet1')

# Keep variables safe
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Slack App credentials for OAuth
# SLACK_CLIENT_ID = os.environ["SLACK_CLIENT_ID"]
# SLACK_CLIENT_SECRET = os.environ["SLACK_CLIENT_SECRET"]
# SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
# SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
# SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
# slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events", app)

client = WebClient(token=config['SLACK_TOKEN'])
BOT_ID = client.api_call('auth.test')['user_id']

# DEBUG
# CHANNEL_NAME = 'test2'
# client.chat_postMessage(channel=CHANNEL_NAME, text='App started')

# TODO: further dev
message_counts = {}
welcome_messages = {}
SCHEDULED_MESSAGES = [
	{'text': 'first one', 'post_at': (
	    datetime.now() + timedelta(seconds=40)).timestamp(), 'channel': 'C023502CL2D'},
	{'text': 'second one', 'post_at': (
	    datetime.now() + timedelta(seconds=50)).timestamp(), 'channel': 'C023502CL2D'}
]

# An example of one of your Flask app's routes
@app.route("/")
def hello():
    return "You are connected!"


@app.route('/slack/eat', methods=['POST'])
def handle_eat():
    try:
        data = request.form
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')

        actionMessage = ActionMessage(channel_id, user_id, worksheet)

        # Rander 4 out of the lists
        lists = worksheet.col_values(1)[1::]
        num_to_select = len(ActionMessage.COLOURS)
        global selected_items
        selected_items = random.sample(lists, num_to_select)
        print(selected_items)  # ['6', '9', '5', '7']

        for index, item in enumerate(selected_items):
            client.chat_postMessage(**actionMessage.get_message(index, item))

        return Response(), 200
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        return Response(), 500


global selections
selections = {}


@app.route('/slack/message_actions', methods=['POST'])
def message_actions():
    data = json.loads(request.form.get('payload'))
    channel_id = data.get('container').get('channel_id')
    user_id = data.get('user').get('id')
    msg_timestamp = data.get('container').get('message_ts')
    btn_eles = data.get('message').get('attachments')[0]['blocks'][1]['elements']

    selection = data['actions'][0]['value']
    # print(selection)

    category = selection[:2] #up
    index = selection[-1:] # 0-2
    # print(f'category: {category} index: {index}')

    if index not in selections:
        selections[index] = {}
        selections[index][category] = 1
    elif category not in selections[index]: # up != dn
        selections[index] = {}
        selections[index][category] = 1
    elif selections[index][category] == 1:
        # if ON, turn off
        selections[index][category] = 0
    elif selections[index][category] == 0:
        # if OFF, turn on
        selections[index][category] = 1
    # print(selections) #{'2': {'up': 1}, '3': {'dn': 0}, '1': {'dn': 0}}

    # print(btn_eles)
    up_ele = btn_eles[0]
    dn_ele = btn_eles[1]

    if 'up' in selections[up_ele.get('value')[-1:]]:   # e.g. {'up': 1} 
        print('upvote!')
        text = f':thumbsup:\t{selections[index][category]}'
        up_ele['text']['text'] = text
        if 'dn' not in selections[index]:
            dn_ele['text']['text'] = f':thumbsdown:\t{0}'
    else:
        print('downvote!')
        text = f':thumbsdown:\t{selections[index][category]}'
        dn_ele['text']['text'] = text
        if 'up' not in selections[index]:
            up_ele['text']['text'] = f':thumbsup:\t{0}'

    # print(type(**data.get('message').get('attachments')[0]))
    # print(data.get('message').get('attachments'))
    
    # print((data.get('message').get('attachments')))
    updated_message = client.chat_update(
        attachments=(data.get('message').get('attachments')),
        channel=channel_id,
        ts=msg_timestamp,
        as_user=True
    )

    return Response(), 200


@app.route('/slack/check', methods=['POST'])
def handle_check():
    data = request.form
    channel_id = data.get('channel_id')
    today = date.today().strftime('%b-%d-%Y')
    worksheet = sh.worksheet('Sheet2')

    # Make selections in the right form in worksheet
    # print(selections) # {'3': {'up': 1}, '1': {'up': 1}, '2': {'up': 1}}
    formatted_items = {}
    for index, sel in enumerate(selections):
        item = f'{list(selections[sel].keys())[0]}_{sel}'
        formatted_items[item] = list(selections[sel].values())[0]
    print(formatted_items) # {'up_0': 1, 'dn_1': 1, 'dn_2': 1, 'dn_3': 0}

    append_row = [0]*len(ActionMessage.COLOURS)*2
    rows = worksheet.row_values(1)
    for index, row in enumerate(rows):
        for item in formatted_items.keys():
            if item == row:
                print(item, row, index, formatted_items[item])
                append_row[index-1] = formatted_items[item]
    print(append_row)
    worksheet.append_row([today, *append_row], table_range='A2')


    # # TODO: emoji thumbsup and down, connect them to responding menus
    # # fields = [{'title': title, 'value': vote, 'short': True} for title, vote in selections.items()]

    # print(fields)
    # client.chat_postMessage(
	# 	channel = channel_id, 
	# 	attachments = [{
	# 		"title": ':ballot_box_with_ballot: Votes for selected menus',
    #         "fallback": "Upgrade your Slack client to use messages like these.",
    # 		"callback_id": 'check votes',
	# 		'fields': [ # Template
    #                     {
    #                         "title": "thumbs_down1",
    #                         "value": "1",
    #                         'short': True
    #                     },
    #                     {
    #                         "title": "thumbs_down2",
    #                         "value": "2",
    #                         'short': True
    #                     }
	#                     ],
	# 		"color": '#EE82EE',
	# 		"thumb_url":'https://i.imgur.com/Ynmyz2n.png'
	# 	}]
	# )
    
    return Response(), 200
