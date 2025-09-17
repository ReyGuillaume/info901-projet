class Message():
    def __init__(self, sender, message):
        self.sender = sender
        self.message = message

    def getMessage(self):
        return self.message

    def getSender(self):
        return self.sender