from Message import Message

class Mailbox():
    def __init__(self):
        self.fifo = []
        self.nbMessage = 0

    def isEmpty(self):
        return self.nbMessage == 0

    def getMessage(self):
        if self.nbMessage == 0:
            raise Exception('Empty fifo in mailbox')
        
        self.nbMessage -= 1
        return self.fifo.pop(0)
    
    def addMessage(self, message):
        self.fifo.append(message)
        self.nbMessage += 1
