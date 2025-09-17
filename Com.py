from Mailbox import Mailbox

class Com():
    NB_PROCESS = 0

    def __init__(self):
        Com.NB_PROCESS += 1
        
        self.lamport = 0
        self.mailbox = Mailbox()

    # Utils

    def inc_clock(self):
        self.lamport += 1
    
    def getNbProcess():
        return Com.NB_PROCESS

    def getMyId():
        return 0

    # Cast

    def broadcast(message):
        pass

    def sendTo(message, dest):
        pass

    def sendToSync(message, dest):
        pass

    def recevFromSync(source):
        pass

    def synchronize():
        pass

    # Section Critique

    def requestSC():
        pass

    def releaseSC():
        pass
