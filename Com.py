from Mailbox import Mailbox
from MessageTo import Message
from Message import Message

from pyeventbus3.pyeventbus3 import *

class Com():
    NB_PROCESS = 0

    def __init__(self):
        self.myId = Com.NB_PROCESS
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
        return self.myId

    # Cast

    def broadcast(self, message):
        msg = Message(self.getMyId(), message)
        PyBus.Instance().post(msg)

    def sendTo(self, message, dest):
        pass

    def sendToSync(self, message, dest):
        pass

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def receive(self, message):
        self.mailbox.addMessage(message)
        
    def recevFromSync(self, source):
        pass

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        pass

    def releaseSC(self):
        pass
