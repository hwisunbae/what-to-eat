class ButtonState:

    
    _buttonStates

    # buttonStates[msg_timestamp] = {
    #     'msgID': msg_timestamp,
    #     'yesThumb': {
    #         'id': 'up_vote',
    #         'index': yesButtonIndex,
    #         'toggle': toggleThumbUp,
    #         'emoji': yesThumb,
    #         'votes': yesVotes
    #     },
    #     'noThumb': {
    #         'id': 'down_vote',
    #         'index': noButtonIndex,
    #         'toggle': toggleThumbDown,
    #         'emoji': noThumb,
    #         'votes': noVotes
    #     }
    # } 
    
    def __init__(self):
        self._buttonStates = {}

    def pushNewState(key):
        self._buttonStates[key] = {

        }

    def updateState():
        pass    