class Message():
    def __init__(self, estampille, payload):
        self.estampille = estampille
        self.payload = payload

    def getEstampille(self):
        return self.estampille
    
    def getPayload(self):
        return self.payload
    
class BroadcastMessage(Message):
    def __init__(self, estampille, payload, sender):
        Message.__init__(self, estampille, payload)
        self.sender = sender
    
    def getSender(self):
        return self.sender

class MessageTo(Message):
    def __init__(self, estampille, payload, to_id):
        Message.__init__(self, estampille, payload)
        self.to_id = to_id
    
    def getDestId(self):
        return self.to_id
