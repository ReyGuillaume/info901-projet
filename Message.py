class Message():
    def __init__(self, sender, payload):
        self.sender = sender
        self.payload = payload

    def getPayload(self):
        return self.payload

    def getSender(self):
        return self.sender