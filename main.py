# import asyncio
# config contains .env file attributes
from config import config

# from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response, json 
from random import sample
# Initialize flask app
# flask run in terminal to run app, have ngrok running alongside it
app = Flask(__name__)

# Initialize slack client using slack bot token
client = WebClient(token=config['SLACK_TOKEN'])
toggleThumbUp = False
yesThumb = ":thumbsup:"
toggleThumbDown = False
noThumb = ":thumbsdown:"
buttonStates = {} # Stores states for every single button behavior that exists

# icon imgur links
# https://imgur.com/a/140IUPz

# ****************************************************************************************
# * WARNING: Ensure ngrok endpoint is correct for global and slash command redirect URLs.*
# ****************************************************************************************

# test route for the default root endpoint using ngrok url
@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/eatery', methods=['GET,POST'])
def bruh():

    # print('hey')
    return Response(), 200




# Call lunch bot using global shortcut
@app.route('/slack/interactions', methods=['POST'])
def interactions():
    # data = request.form
    # d = (data.getlist('payload'))
    # print(type(d[0]))

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
        if payload['actions'][0]['action_id'] == 'LMVoteYes' or payload['actions'][0]['action_id'] == 'LMVoteNo':

            msg_timestamp = (payload['container']['message_ts']) # timestamp of specific message that the clicked button is from
            channel_id = (payload['container']['channel_id']) # channel id of message posted in
            
            modifiedAttachments = (payload['message']['attachments']) # grab attachment from payload to modify
            # list of buttons in the message
            buttonElements = ((modifiedAttachments)[0]['blocks'][2]['elements'])

            clickedButtonId = payload['actions'][0]['action_id'] # ID of thumb button clicked
            clickedButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == clickedButtonId), None)  # Returns none, if not found
            # print(buttonIndex) 
            # thumbup and thumnddown button indices
            yesButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == 'LMVoteYes'), None)
            noButtonIndex = next((i for i, item in enumerate(buttonElements) if item["action_id"] == 'LMVoteNo'), None)

            # Tokenizes button text to fetch thumb emoji
            # clickedButtonText = modifiedAttachments[0]['blocks'][2]['elements'][clickedButtonIndex]['text']['text'].split()
            # thumb = clickedButtonText[0]  # THUMB EMOJI
            # numVotes = int(clickedButtonText[1]) # number of votes 

            # IF Thumb UP was clicked
            if clickedButtonId == 'LMVoteYes':
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
                            'id': 'LMVoteYes',
                            'index': yesButtonIndex,
                            'toggle': toggleThumbUp,
                            'emoji': yesThumb,
                            'votes': yesVotes
                        },
                        'noThumb': {
                            'id': 'LMVoteNo',
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
            elif clickedButtonId == 'LMVoteNo':
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
                            'id': 'LMVoteYes',
                            'index': yesButtonIndex,
                            'toggle': toggleThumbUp,
                            'emoji': yesThumb,
                            'votes': yesVotes
                        },
                        'noThumb': {
                            'id': 'LMVoteNo',
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

            # non existant button state, make new record and add to dictionary  
            # if buttonStates.get(msg_timestamp) == None:
            #     buttonStates[msg_timestamp] = {
            #         'msgID': msg_timestamp,
            #         'yesThumb': {
            #             'id': 'LMVoteYes',
            #             'index': yesButtonIndex,
            #             'toggle': toggleThumbUp,
            #             'emoji': yesThumb,
            #             'votes': yesThumbVotes
            #         },
            #         'noThumb': {
            #             'id': 'LMVoteNo',
            #             'index': noButtonIndex,
            #             'toggle': toggleThumbDown,
            #             'emoji': noThumb,
            #             'votes': yesThumbVotes
            #         }
            #     }






            # modifiedAttachments[0]['blocks'][2]['elements'][clickedButtonIndex]['text']['text'] = updatedThumb # MODIFY BUTTON
            # modify other button

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


# Call lunch bot using SLASH command /eat
@app.route('/slack/eat', methods=['POST'])
def eat():
    try:
        # attachments colours
        COLOURS = ['#36a64f', '#eefc54', '#ef8432', '#d72e1f']
        # food picture icons
        ICONS = [
            'https://i.imgur.com/A6ZYjqa.png',
            'https://i.imgur.com/1GzdmiO.png',
            'https://i.imgur.com/ZZQAnxz.png',
            'https://i.imgur.com/DL9JQcp.png'
            'https://i.imgur.com/VM77DCC.png',
            'https://i.imgur.com/f9vvWf9.png',
            'https://i.imgur.com/hUYozGq.png',
            'https://i.imgur.com/VSnegZ8.png',
            'https://i.imgur.com/IopeEpq.png',
            'https://i.imgur.com/j4dRNI9.png',
            'https://i.imgur.com/NmSvpSS.png',
            'https://i.imgur.com/iGy03d0.png',
            'https://i.imgur.com/gGEcGQi.png',
            'https://i.imgur.com/fuYAK7b.png'
        ]

        # print(type(request.form))
        data = request.form
        # print(data)
        user_id = data.get('user_id')
        channel_id = data.get('channel_id')
        print(f'CHANNEL ID {channel_id}')
        # Send msg in user's DMs when user executed the /eat command
        # result = client.chat_postMessage(
        #     channel=user_id,
        #     text="yooo"
        # )

        # col = sample(COLOURS, len(COLOURS))
        pics = sample(ICONS, len(ICONS))

        client.chat_postMessage(
            channel=channel_id,
            user=user_id,
            text=":stew:----------*LUNCH BOT:* *TIME TO EAT!!!* ----------:stew:",
        )

        # Send msg in any channel privately to user that executed the /eat command
        for i in range(len(COLOURS)):
            # print(len(COLOURS))
            result = client.chat_postMessage(
                channel=channel_id,
                user=user_id,
                # text="test",
                attachments=[{
                    # 'text': 'optional attach text', DO NOT PUT
                    # "title": 'MyTitle', DO NOT PUT
                    # "title_link": 'https://www.google.ca', DO NOT PUT
                    'fallback': 'this is a fallback message if things fail',
                    "color": COLOURS[i],
                    # "thumb_url": "https://i.imgur.com/j4dRNI9.png", DO NOT PUT
                    # "fields": [

                    # ],
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "<https://www.google.com|Ox and Finch>"
                            },
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*Menu Recommended*"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "*Price*"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "701 Nigri Box"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "$542"
                                }
                            ],
                            "accessory": {
                                "type": "image",
                                "image_url": pics[i],
                                "alt_text": pics[i]
                            }
                        },

                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": ":pencil: *Vote*"
                                }
                            ]
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": ":thumbsup:\t0",
                                        "emoji": True
                                    },
                                    "value": "yes",
                                    "action_id": "LMVoteYes"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": ":thumbsdown:\t0",
                                        "emoji": True
                                    },
                                    "value": "no",
                                    "action_id": "LMVoteNo"
                                }
                            ]
                        }
                    ]


                }]
            )

        return Response(), 200

        # The server responded with: {'ok': False, 'error': 'internal_error'}
        # {
        #     "title": "Thumb Signal",
        #     "value": ":thumbsup: " + '0' + '       :thumbsdown: ' + '0',
        #     'short': True
        # }

   

        # ],
        # 'fields': [
        #     {
        #         "title": "Menu Recommended",
        #         "value":  'FoodName' + ' ' + '$70.00',
        #         "mrkdwn_in": ["text"],
        #         'short': True
        #     },

        # token = config['SLACK_TOKEN']
        # headers={
        #             'Content-type': 'application/json',
        #             'Authorization': f"Bearer {token}"
        #         }
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        return Response(), 500