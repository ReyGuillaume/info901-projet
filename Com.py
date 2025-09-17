from Mailbox import Mailbox

class Com():
    def __init__(self):
        self.lamport = 0
        self.mailbox = Mailbox()

    # Utils

    def inc_clock():
        pass
    
    def getNbProcess():
        return 1

    def getMyId():
        pass

    # Cast

    def broadcast(message):
        pass

    def sendTo(message, dest):
        pass

    def sendToSync(message, dest):
        pass

    def recevFromSync():
        pass

    def synchronize():
        pass

    # Section Critique

    def requestSC():
        pass

    def releaseSC():
        pass
