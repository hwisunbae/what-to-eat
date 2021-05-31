class ActionMessage:
	COLOURS = ['#36a64f', '#eefc54', '#ef8432', '#d72e1f']

	PHOTOS = ['https://i.imgur.com/ZrZLmZa.png','https://i.imgur.com/TYNURtM.png',
		  'https://i.imgur.com/Sxjrtso.png','https://i.imgur.com/1nFZsc7.png',
		  'https://i.imgur.com/aUELdkg.png','https://i.imgur.com/co2D9cl.png',
		  'https://i.imgur.com/Qwo5n0U.png','https://i.imgur.com/mOg1t1r.png',
		  'https://i.imgur.com/Vb0ve9u.png','https://i.imgur.com/95FYmFe.png',
		  'https://i.imgur.com/0jxjDrc.png','https://i.imgur.com/kdyBfuB.png',
		  'https://i.imgur.com/55Pbyvu.png','https://i.imgur.com/YNj8Ikc.png']

	def __init__(self, channel, user, worksheet):
		self.channel = channel
		self.user = user
		self.icon_emoji = ':pizza:'
		self.timestamp = ''
		self.completed = False
		self.worksheet = worksheet

	def get_message(self, index, item):
		row = self.worksheet.row_values(item)

		return {
			'ts':self.timestamp,
			'channel': self.user, # Direct Message
			'username': 'Welcome user!',
			'icon_emoji': self.icon_emoji,
			'attachments': [{
                'fallback': 'this is a fallback message if things fail',
                "color": self.COLOURS[index],
				'blocks': [
					{
						"type": "section",
	                    "text": {
	                        "type": "mrkdwn",
							"text": f"<{row[2]}|{row[1]}>" if row[2] else row[1]
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
	                            "text": row[4] 
	                        },
	                        {
	                            "type": "mrkdwn",
	                            "text": row[5]
	                        }
	                    ],
	                    "accessory": {
	                        "type": "image",
	                        "image_url": self.PHOTOS[int(row[7])-1],
	                        "alt_text": self.PHOTOS[int(row[7])-1]
	                    }
					},{
						"type": "actions",
	                    "elements": [
	                        {
	                            "type": "button",
	                            "text": {
	                                "type": "plain_text",
	                                "text": ":thumbsup:\t0",
	                                "emoji": True
	                            },
	                            "value": f"up_{index}",
	                            "style": "primary",
	                            "action_id": "up_vote"
	                        },
	                        {
	                            "type": "button",
	                            "text": {
	                                "type": "plain_text",
	                                "text": ":thumbsdown:\t0",
	                                "emoji": True
	                            },
	                            "value": f"dn_{index}",
	                            "style": "danger",
	                            "action_id": "dn_vote"
	                        }
	                    ]
					}
				]
			}]
			
			# 'blocks': [
			# 	self.START_TEXT,
			# 	self.DIVIDER,
			# 	self._get_reaction_task()
			# ]
		}

	def _get_reaction_task(self):
		checkmark = ':white_check_mark:'
		if not self.completed:
			checkmark = ':white_large_square:'
		text = f'{checkmark} *React to this message'
		return {'type': 'section', 'text': {'type':'mrkdwn', 'text':text}}