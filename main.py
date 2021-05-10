# import asyncio
# config contains .env file attributes
from config import config

# from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, Response, json

# Initialize flask app
# flask run in terminal to run app, have ngrok running alongside it
app = Flask(__name__)

# Initialize slack client using slack bot token
client = WebClient(token=config['SLACK_TOKEN'])

# ****************************************************************************************
# * WARNING: Ensure ngrok endpoint is correct for global and slash command redirect URLs.* 
# ****************************************************************************************

# test route for the default root endpoint using ngrok url
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Call lunch bot using global shortcut 
@app.route('/slack/shortcuts', methods=['POST'])
def global_shortcut():
    # print(request.form)
    return Response(), 200

# Call lunch bot using SLASH command /lc 
@app.route('/slack/lc', methods=['POST'])
def lc():
    try:
        print(type(request.form))
        data = request.form
        # print(data)
        user_id = data.get('user_id')
        channel_id = data.get('channel_id')

        # Send msg in user's DMs when user executed the /lc command
        # result = client.chat_postMessage(
        #     channel=user_id,
        #     text="yooo"
        # )

        # Send msg in any channel privately to user that executed the /lc command 
        result = client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="test"
        )

        return Response(), 200

        # token = config['SLACK_TOKEN']
        # headers={
        #             'Content-type': 'application/json',
        #             'Authorization': f"Bearer {token}"
        #         }
    except SlackApiError as e:
        print(f"Error posting message: {e}")
        return Response(), 500