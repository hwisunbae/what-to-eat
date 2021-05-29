def send_welcome_message(channel, user):
	welcome = WelcomeMessage(channel, user)
	message = welcome.get_message()
	response = client.chat_postMessage(**message)
	welcome.timestamp = response['ts']

	if channel not in welcome_messages:
		welcome_messages[channel] = {}
	welcome_messages[channel][user] = welcome

# TODO: develop the bot to send the msg in lunch time
def schcdule_messages(messages):
	ids = []
	for msg in messages:
		response = client.chat_scheduleMessage(
			channel=msg['channel'], 
			text=msg['text'], 
			post_at=(datetime.now() + timedelta(seconds=50)).strftime('%s'))
		id_ = response.get('id')
		ids.append(id_)
	return ids

# Create an event listener for "message"
@slack_events_adapter.on("message")
def handle_message(payload):
	message = payload.get('event')
	channel_id = message.get('channel')
	text  = message.get('text')
	user_id = message.get('user')

	if user_id != None and BOT_ID != user_id:
		if user_id in message_counts:
			message_counts[user_id] += 1
		else:
			message_counts[user_id] = 1

		if text.lower() == 'start':
			send_welcome_message(channel_id, user_id)

# Welcome message reaction - NOT IN USE 
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