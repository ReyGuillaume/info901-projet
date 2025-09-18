from Mailbox import Mailbox
from pyeventbus3.pyeventbus3 import *
from threading import Event
from Message import BroadcastMessage, MessageTo, MessageToSync, AckMessage



class Com():
    NB_PROCESS = 0

    def __init__(self):
        self.myId = Com.NB_PROCESS
        Com.NB_PROCESS += 1

        self.lamport = 0
        self.mailbox = Mailbox()

        self.pending = {}  # msg_id -> Event

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
        msg = BroadcastMessage(self.lamport, self.getMyId(), message)
        PyBus.Instance().post(msg)

    def sendTo(self, payload, dest):
        msg = MessageTo(self.getMyId(), dest, payload)
        print("sendTo P" + str(dest) +
              ": " + str(payload) )
        PyBus.Instance().post(msg)

    def sendToSync(self, payload, dest, timeout=5):
        # Création du message
        msg = MessageToSync(self.getMyId(), dest, payload)
        event = Event()
        self.pending[msg.getId()] = event

        print(f"P{self.myId} sendToSync P{dest}: {payload} (msg_id={msg.getId()})")
        PyBus.Instance().post(msg)

        ok = event.wait(timeout=timeout)
        if not ok:
            print(f"P{self.myId} sendToSync -> TIMEOUT for msg_id={msg.getId()}")
        else:
            print(f"P{self.myId} sendToSync -> ACK received for msg_id={msg.getId()}")

        # Nettoyage
        self.pending.pop(msg.getId(), None)
        return ok

    # Event Handlers

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
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
            # envoyer un ACK
            ack = AckMessage(self.getMyId(), message.getSender(), message.getId())
            PyBus.Instance().post(ack)

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        pass

    def releaseSC(self):
        pass


    @subscribe(threadMode=Mode.PARALLEL, onEvent=AckMessage)
    def onAck(self, ack):
        if self.getMyId() == ack.getDestId():
            if ack.getId() in self.pending:
                self.pending[ack.getId()].set()
