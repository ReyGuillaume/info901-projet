class Message():
    def __init__(self, sender, payload):
        self.sender = sender
        self.payload = payload

    def getPayload(self):
        return self.payload

    def getSender(self):
        return self.sender
    


class MessageTo(Message):

    def __init__(self, sender, to_id, payload):
        Message.__init__(self, sender, payload)
        self.to_id = to_id


