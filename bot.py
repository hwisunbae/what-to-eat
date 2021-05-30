# Need to run -> ngrok http 5000 

import os
import random
import json

# config contains .env file attributes
from config import config
from pathlib import Path
from dotenv import load_dotenv
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter
from slack_sdk.errors import SlackApiError
from flask import Flask, Response, make_response, request
from datetime import datetime, timedelta

from WelcomeMessage import *

# Authorize google spread sheet 
import gspread
# gc = gspread.service_account(filename=config[CRED_FILENAME])
gc = gspread.service_account(filename='./service_account.json')
sh = gc.open("lunchbot")
worksheet = sh.sheet1

# Keep variables safe
env_path = Path('.')  / '.env'
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

toggleThumbUp = False
yesThumb = ":thumbsup:"
toggleThumbDown = False
noThumb = ":thumbsdown:"
buttonStates = {} # Stores states for every single button behavior that exists

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
@app.route('/slack/eat', methods=['POST'])
def handle_eat():
	try:
		data = request.form
		channel_id = data.get('channel_id')
		user_id = data.get('user_id')

		# Rander 4 out of the lists
		lists = worksheet.col_values(1)[1::]
		num_to_select = len(COLOURS)
		global selected_items
		selected_items = random.sample(lists, num_to_select)
		print(selected_items) #['6', '9', '5', '7']

		for index, item in enumerate(selected_items):
			row = worksheet.row_values(item)
			client.chat_postMessage(
				channel = user_id, 
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
							"text": ":thumbsup:\t0",
							"type": "button",
							"value": f"thumbs_up_{index}",
							"style": "primary",
							"action_id": "up_vote"
						},
						{
							"name": f"thumbs_down_{index}",
							"text": ":thumbsdown:\t0",
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
	except SlackApiError as e:
		print(f"Error posting message: {e}")
		return Response(), 500



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
@app.route('/slack/check', methods=['POST'])
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


# Call lunch bot using global shortcut
@app.route('/slack/interactions', methods=['POST'])
def interactions():

    # print(request.form)
    # request.form is an immutableMultiDict
    json_string = request.form.get('payload')   # returns a json string
    # convert json string to python Dictionary
    payload = json.loads(json_string)

    # print(payload)
    global toggleThumbUp 
    global toggleThumbDown
    global buttonStates
    global yesThumb
    global noThumb

    # For block message interactions
    if payload['type'] == 'block_actions':
        if payload['actions'][0]['action_id'] == 'up_vote' or payload['actions'][0]['action_id'] == 'down_vote':

            msg_timestamp = (payload['container']['message_ts']) # timestamp of specific message that the clicked button is from
            channel_id = (payload['container']['channel_id']) # channel id of message posted in
            
            modifiedAttachments = (payload['message']['attachments']) # grab attachment from payload to modify
            # list of buttons in the message
            buttonElements = ((modifiedAttachments)[0]['blocks'][2]['elements'])

            clickedButtonId = payload['actions'][0]['action_id'] # ID of thumb button clicked
            clickedButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == clickedButtonId), None)  # Returns none, if not found

            # up_vote and down_vote button indices
            yesButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == 'up_vote'), None)
            noButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == 'down_vote'), None)

            # IF Thumb UP was clicked
            if clickedButtonId == 'up_vote':
                print(f'THUMB UP CLICKED = {msg_timestamp}')
                # no buttonState, create one, 
                # Result: turn on thumbup, save state for thumbup + thumbdown
                if buttonStates.get(msg_timestamp) == None:
                    print(f'NO STATE FOR = {msg_timestamp}')
                    toggleThumbDown = False
                    noButtonText = modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'].split()
                    noVotes = int(noButtonText[1])
                    
                
                    toggleThumbUp = True
                    yesButtonText = modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'].split()
                    yesVotes = int(yesButtonText[1])
                    yesVotes += 1
                    # color -> green
                    # "style": "primary",
                    modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['style'] = 'primary'
                    updateVote = f'{yesThumb} {yesVotes}'

                    buttonStates[msg_timestamp] = {
                        'msgID': msg_timestamp,
                        'yesThumb': {
                            'id': 'up_vote',
                            'index': yesButtonIndex,
                            'toggle': toggleThumbUp,
                            'emoji': yesThumb,
                            'votes': yesVotes
                        },
                        'noThumb': {
                            'id': 'down_vote',
                            'index': noButtonIndex,
                            'toggle': toggleThumbDown,
                            'emoji': noThumb,
                            'votes': noVotes
                        }
                    } 

                    modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'] =  updateVote 

                else: # use buttonState
                    # thumbdown toggled on, thumbup toggled off
                    # Result: Turn on thumbup
                    print(f'HAS STATE FOR = {msg_timestamp}')
                    if buttonStates[msg_timestamp]['noThumb']['toggle'] == True and buttonStates[msg_timestamp]['yesThumb']['toggle'] == False:
                        print(f'Turn off DOWN, turn on UP = {msg_timestamp}')
                        toggleThumbDown = False
                        buttonStates[msg_timestamp]['noThumb']['toggle'] = toggleThumbDown
                        noVotes = int(buttonStates[msg_timestamp]['noThumb']['votes'])
                        if noVotes > 0:
                            noVotes -= 1

                        buttonStates[msg_timestamp]['noThumb']['votes'] = noVotes
                        updateNoVote = f'{noThumb} {noVotes}'
                        # change color -> neutral  
                        # removing key will set style to default gray color
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex].pop('style', None)
                        # no Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'] = updateNoVote
                        # -------------------------------
                        toggleThumbUp = True
                        buttonStates[msg_timestamp]['yesThumb']['toggle'] = toggleThumbUp
                        yesVotes = int(buttonStates[msg_timestamp]['yesThumb']['votes'])
                        yesVotes += 1
                        buttonStates[msg_timestamp]['yesThumb']['votes'] = yesVotes
                        updateYesVote = f'{yesThumb} {yesVotes}'
                        # change color
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['style'] = 'primary'
                        # yes Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'] = updateYesVote

                    # thumbdown toggled off, thumbup toggled on
                    # Result: Turn off thumbup
                    elif buttonStates[msg_timestamp]['noThumb']['toggle'] == False and buttonStates[msg_timestamp]['yesThumb']['toggle'] == True:
                        print(f'Turn off UP only = {msg_timestamp}')
                        toggleThumbUp = False
                        buttonStates[msg_timestamp]['yesThumb']['toggle'] = toggleThumbUp
                        yesVotes = int(buttonStates[msg_timestamp]['yesThumb']['votes'])
                        if yesVotes > 0:
                            yesVotes -= 1
                            
                        buttonStates[msg_timestamp]['yesThumb']['votes'] = yesVotes
                        updateYesVote = f'{yesThumb} {yesVotes}'
                        # change color -> neutral
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex].pop('style', None)
                        # yes Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'] = updateYesVote

                    # thumbdown toggled off, thumbup toggled off
                    # Result: Turn on thumbup
                    elif buttonStates[msg_timestamp]['noThumb']['toggle'] == False and buttonStates[msg_timestamp]['yesThumb']['toggle'] == False:
                        print(f'Turn on UP only = {msg_timestamp}') 
                        toggleThumbUp = True
                        buttonStates[msg_timestamp]['yesThumb']['toggle'] = toggleThumbUp
                        yesVotes = int(buttonStates[msg_timestamp]['yesThumb']['votes'])
                        yesVotes += 1
                        buttonStates[msg_timestamp]['yesThumb']['votes'] = yesVotes
                        updateYesVote = f'{yesThumb} {yesVotes}'
                        # change color -> green
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['style'] = 'primary'
                        # yes Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'] = updateYesVote
            #--------------------------------------------------------------------------------------------------------------
            # IF thumb down was clicked
            elif clickedButtonId == 'down_vote':
                print(f'THUMB DOWN CLICKED = {msg_timestamp}')
                # no buttonState, create one, 
                # Result: turn on thumbdown, save state for thumbup + thumbdown
                if buttonStates.get(msg_timestamp) == None:
                    print(f'NO STATE FOR = {msg_timestamp}')
                    toggleThumbUp = False
                    yesButtonText = modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'].split()
                    yesVotes = int(yesButtonText[1])

                    toggleThumbDown = True
                    noButtonText = modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'].split()
                    noVotes = int(noButtonText[1])
                    noVotes += 1
                    # color -> red
                    # "style": "danger" 
                    modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['style'] = 'danger'
                    updateVote = f'{noThumb} {noVotes}' 
                    
                    buttonStates[msg_timestamp] = {
                        'msgID': msg_timestamp,
                        'yesThumb': {
                            'id': 'up_vote',
                            'index': yesButtonIndex,
                            'toggle': toggleThumbUp,
                            'emoji': yesThumb,
                            'votes': yesVotes
                        },
                        'noThumb': {
                            'id': 'down_vote',
                            'index': noButtonIndex,
                            'toggle': toggleThumbDown,
                            'emoji': noThumb,
                            'votes': noVotes
                        }
                    } 

                    modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'] = updateVote 

                else: # use buttonState
                    # Thumbup toggled on, Thumbdown is toggled off
                    # Result: turn of thumbup, turn on thumbdown
                    print(f'HAS STATE FOR = {msg_timestamp}')
                    if buttonStates[msg_timestamp]['yesThumb']['toggle'] == True and buttonStates[msg_timestamp]['noThumb']['toggle'] == False:
                        print(f'Turn off UP, turn on DOWN = {msg_timestamp}')
                        toggleThumbUp = False
                        buttonStates[msg_timestamp]['yesThumb']['toggle'] = toggleThumbUp
                        yesVotes = int(buttonStates[msg_timestamp]['yesThumb']['votes'])
                        if yesVotes > 0:
                            yesVotes -= 1

                        buttonStates[msg_timestamp]['yesThumb']['votes'] = yesVotes
                        updateYesVote = f'{yesThumb} {yesVotes}'
                        # change color -> neutral  
                        # removing key will set style to default gray color
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex].pop('style', None)
                        # yes Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][yesButtonIndex]['text']['text'] = updateYesVote
                        # -------------------------------

                        toggleThumbDown = True
                        buttonStates[msg_timestamp]['noThumb']['toggle'] = toggleThumbDown
                        noVotes = int(buttonStates[msg_timestamp]['noThumb']['votes'])
                        noVotes += 1
                        buttonStates[msg_timestamp]['noThumb']['votes'] = noVotes
                        updateNoVote = f'{noThumb} {noVotes}'
                        # change color to RED
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['style'] = 'danger'
                        # no Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'] = updateNoVote

                    # Thumbup toggled off, Thumbdown is toggled on
                    # Result: Turn off thumbdown
                    elif buttonStates[msg_timestamp]['yesThumb']['toggle'] == False and buttonStates[msg_timestamp]['noThumb']['toggle'] == True: 
                        print(f'Turn off DOWN only = {msg_timestamp}')
                        toggleThumbDown = False
                        buttonStates[msg_timestamp]['noThumb']['toggle'] = toggleThumbDown
                        noVotes = int(buttonStates[msg_timestamp]['noThumb']['votes'])
                        if noVotes > 0:
                            noVotes -= 1
                        
                        buttonStates[msg_timestamp]['noThumb']['votes'] = noVotes
                        updateNoVote = f'{noThumb} {noVotes}'
                        # change color -> neutral
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex].pop('style', None)
                        # no Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'] = updateNoVote

                    # Thumbup toggled off, Thumbdown is toggled off
                    # Result: Turn on thumbdown
                    elif buttonStates[msg_timestamp]['yesThumb']['toggle'] == False and buttonStates[msg_timestamp]['noThumb']['toggle'] == False:
                        print(f'Turn on DOWN only = {msg_timestamp}') 
                        toggleThumbDown = True
                        buttonStates[msg_timestamp]['noThumb']['toggle'] = toggleThumbDown
                        noVotes = int(buttonStates[msg_timestamp]['noThumb']['votes'])
                        noVotes += 1
                        buttonStates[msg_timestamp]['noThumb']['votes'] = noVotes
                        updateNoVote = f'{noThumb} {noVotes}'
                        # change color -> RED
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['style'] = 'danger'
                        # no Thumb update
                        modifiedAttachments[0]['blocks'][2]['elements'][noButtonIndex]['text']['text'] = updateNoVote

            # print(modifiedAttachments)

            # UPDATE MSG WITH NEW MODIFIED ATTACHMENT
            client.chat_update(
                channel=channel_id,
                ts=msg_timestamp,
                as_user=True,
                attachments=modifiedAttachments
            )

    # for message or global shortcut interactions
    elif payload['type'] == 'shortcut':
        print('shortcuct pressed')
    # for modal interactions
    elif payload['type'] == 'view_submission':
        print('modal submitted')

    return Response(), 200


# if __name__ == '__main__':
# 	# schcdule_messages(SCHEDULED_MESSAGES)
# 	app.run(port=5000, debug=True)