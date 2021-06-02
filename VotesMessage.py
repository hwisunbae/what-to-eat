class VotesMessage:

	COLOURS = ['#EE82EE']
	PHOTOS = ['https://i.imgur.com/Ynmyz2n.png']

	def __init__(self, channel, user, worksheet):
            self.channel = channel
            self.user = user
            self.icon_emoji = ':pizza:'
            self.timestamp = ''
            self.worksheet = worksheet
            self.fields = []

	def get_message(self, selected_items, votes):

            # i is 0 - 4 for each lunch entry
            for i, lunchIdx in enumerate(selected_items):
                row = self.worksheet.row_values(lunchIdx)
                lunchVoteResult = [
                    {
                        "type": "mrkdwn",
                        "text": f"<{row[2]}|{row[1]}>" if row[2] else row[1] 
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Votes*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{row[4]} {row[5]}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f":thumbsup: {votes[i][0]}\t\t:thumbsdown: {votes[i][1]}" 
                        #     0               1 
                        # [['new data1', 'new data2'], ['new data3', 'new data4'], ['new data5', 'new data6'], ['new data7', 'new data8']]
                    }
                ]
                self.fields.extend(lunchVoteResult)

                # row = self.worksheet.row_values(item)
                #receive selected_items ['5', '7', '6', '3']
                # row ['5', 'Baffo Pizza And Birra', 'https://www.baffo.co.uk', '1377 Argyle St, Glasgow G3 8AF', 'Magherita Pizza', '£8.0', '230M', '8']
                # fields push into list 4 times
                # "text": f"<{row[2]}|{row[1]}>" if row[2] else row[1]   will be title of food
                # "<https://www.google.com|Mora Bar and Kitchen>" 
            
		return {
			'ts':self.timestamp,
			'channel': self.user, # Direct Message
			'username': 'Welcome user!',
			'icon_emoji': self.icon_emoji,
			'attachments': [{
                'fallback': 'this is a fallback message if things fail',
                "color": self.COLOURS[0],
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":ballot_box_with_ballot: Votes for selected menus"
                        },
                        "fields": self.fields,
                        "accessory": {
                            "type": "image",
                            "image_url": self.PHOTOS[0],
                            "alt_text": self.PHOTOS[0]
                        }
                    }
                ]
            }]   
		}
			
        # 'blocks': [
        # 	self.START_TEXT,
        # 	self.DIVIDER,
        # 	self._get_reaction_task()
        # ]

	# def _get_reaction_task(self):
	# 	checkmark = ':white_check_mark:'
	# 	if not self.completed:
	# 		checkmark = ':white_large_square:'
	# 	text = f'{checkmark} *React to this message'
	# 	return {'type': 'section', 'text': {'type':'mrkdwn', 'text':text}}
