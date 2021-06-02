class VotesMessage:

	COLOURS = ['#EE82EE']
	PHOTOS = ['https://i.imgur.com/Ynmyz2n.png']

	def __init__(self, channel, user, lunchWorksheet):
            self.channel = channel
            self.user = user
            self.icon_emoji = ':pizza:'
            self.timestamp = ''
            self.lunchWorksheet = lunchWorksheet
            self.fields = []

	def get_message(self, selected_items, votes):
            #received selected_items ['5', '7', '6', '3']
            # self.fields = []
            
            # fields: push into list 4 times
            # i is 0 - 4 for each lunch entry
            for i, selected_value in enumerate(selected_items):
                lunchRow = self.lunchWorksheet.row_values(int(selected_value))
                # lunchRow ['5', 'Baffo Pizza And Birra', 'https://www.baffo.co.uk', '1377 Argyle St, Glasgow G3 8AF', 'Magherita Pizza', '£8.0', '230M', '8']
                lunchVoteResult = [
                    # "<https://www.google.com|Mora Bar and Kitchen>" 
                    {
                        "type": "mrkdwn",
                        "text": f"*<{lunchRow[2]}|{lunchRow[1]}>*\n{lunchRow[4]} *{lunchRow[5]}*" if lunchRow[2] else f"*{lunchRow[1]}*\n{lunchRow[4]} *{lunchRow[5]}*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Votes*\n:thumbsup: {votes[i][0]}\t\t:thumbsdown: {votes[i][1]}" # e.g. votes[i]: [up,dn]
                    } 
                ]
                self.fields.extend(lunchVoteResult) # appends to fields by adding 4 dicts to list everytime

            if len(selected_items) > 0:
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
            else:
                return {
                    'channel': self.channel,
                    'text': "No votes to show"
                }