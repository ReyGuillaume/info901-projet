class Message():
    def __init__(self, estampille, payload, sender):
        self.estampille = estampille
        self.payload = payload
        self.sender = sender

    def getEstampille(self):
        return self.estampille
    
    def getPayload(self):
        return self.payload
    
    def getSender(self):
        return self.sender

class BroadcastMessage(Message):
    def __init__(self, estampille, payload, sender):
        Message.__init__(self, estampille, payload, sender)

class MessageTo(Message):
    def __init__(self, estampille, payload, sender, to_id):
        Message.__init__(self, estampille, payload, sender)
        self.to_id = to_id
    
    def getDestId(self):
        return self.to_id

class MessageToSync(Message):
    def __init__(self, estampille, payload):
        Message.__init__(self, estampille, payload)

class Token():
    def __init__(self, owner):
        self.owner = owner
    
    def getOwner(self):
        return self.owner
