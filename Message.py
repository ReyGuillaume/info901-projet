import uuid

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


class MessageToSync(MessageTo):
    def __init__(self, estampille, payload, sender, to_id):
        super().__init__(estampille, payload, sender, to_id)
        # identifiant unique pour le suivi de l'ack
        self.msg_id = str(uuid.uuid4())

    def getId(self):
        return self.msg_id


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

class Token():
    def __init__(self, owner):
        self.owner = owner
    
    def getOwner(self):
        return self.owner
