from Mailbox import Mailbox

from pyeventbus3.pyeventbus3 import *

class Com():
    NB_PROCESS = 0

    def __init__(self):
        Com.NB_PROCESS += 1
        
        self.lamport = 0
        self.mailbox = Mailbox()

        PyBus.Instance().register(self, self)

    # Utils

    def inc_clock(self):
        self.lamport += 1
    
    def getNbProcess(self):
        return Com.NB_PROCESS

    def getMyId(self):
        return 0

    # Cast

    def broadcast(self, message):
        pass

    def sendTo(self, message, dest):
        pass

    def sendToSync(self, message, dest):
        pass

    def recevFromSync(self, source):
        pass

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        pass

    def releaseSC(self):
        pass
