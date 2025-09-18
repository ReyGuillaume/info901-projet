from Mailbox import Mailbox
from enum import Enum

from pyeventbus3.pyeventbus3 import *
from Message import BroadcastMessage, MessageTo, MessageToSync, Token

class Com():
    NB_PROCESS = 0

    def __init__(self):
        self.myId = Com.NB_PROCESS
        Com.NB_PROCESS += 1
        
        self.stateSC = StateSC.NULL
        self.lamport = 0
        self.mailbox = Mailbox()

        PyBus.Instance().register(self, self)

        if self.getMyId() == 2:
            self.sendTokenToNextProcess()

    # Utils

    def inc_clock(self):
        self.lamport += 1
    
    def getNbProcess(self):
        return Com.NB_PROCESS

    def getMyId(self):
        return self.myId

    # Cast

    def broadcast(self, message):
        msg = BroadcastMessage(self.lamport, message, self.getMyId())
        PyBus.Instance().post(msg)

    def sendTo(self, payload, dest):
        msg = MessageTo(self.lamport, payload, self.getMyId(), dest)
        print(str(self.getMyId()) + " sendTo P" + str(dest) +
              ": " + str(payload) )
        PyBus.Instance().post(msg)
        pass

    def sendToSync(self, message, dest):
        pass

    @subscribe(threadMode = Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, message):
        if self.getMyId() != message.getSender():
            self.mailbox.addMessage(message)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def receiveFrom(self, message):
        if self.getMyId() == message.getDestId():
            self.mailbox.addMessage(message)
        
    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageToSync)
    def recvFromSync(self, message, source):
        if self.getMyId() == source:
            self.mailbox.addMessage(message)

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        self.stateSC = StateSC.REQUEST
        while self.stateSC == StateSC.SC:
            continue

    def releaseSC(self):
        if self.stateSC != StateSC.SC:
            return
        
        self.stateSC = StateSC.RELEASE
        self.sendTokenToNextProcess()
        self.stateSC = StateSC.NULL

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, token):
        if token.getOwner() == self.getMyId():
            if self.stateSC == StateSC.REQUEST:
                self.stateSC = StateSC.SC
            else:
                self.sendTokenToNextProcess()

    def sendTokenToNextProcess(self):
        PyBus.Instance().post(Token(self.nextProcess()))

    def nextProcess(self):
        return (self.getMyId() + 1) % Com.NB_PROCESS

class StateSC(Enum):
    NULL = 0
    REQUEST = 1
    SC = 2
    RELEASE = 3
