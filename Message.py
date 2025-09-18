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


class MessageToSync:
    def __init__(self, sender, dest, payload, msg_id=None):
        self.sender = sender
        self.dest = dest
        self.payload = payload
        self.msg_id = msg_id   

    def getSender(self):
        return self.sender

    def getDestId(self):
        return self.dest

    def getPayload(self):
        return self.payload

    def getId(self):
        return self.msg_id

# Message d’acknowledgement
class AckMessage:
    def __init__(self, sender, dest, msg_id):
        self.sender = sender
        self.dest = dest
        self.msg_id = msg_id

    def getSender(self):
        return self.sender

    def getDestId(self):
        return self.dest

    def getId(self):
        return self.msg_id
