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

        self.pending_send = {}
        self.pending_recv = {}
        self.received_sync_msgs = {}


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
        msg = BroadcastMessage(self.lamport, message, self.getMyId())
        PyBus.Instance().post(msg)

    def sendTo(self, payload, dest):
        msg = MessageTo(self.lamport, payload, self.getMyId(), dest)
        PyBus.Instance().post(msg)

    def sendToSync(self, payload, dest, timeout=5):
        msg = MessageToSync(self.lamport, payload, self.myId, dest)
        event = Event()
        self.pending_send[msg.getId()] = event

        print(f"P{self.myId} sendToSync P{dest}: {payload} (msg_id={msg.getId()})")
        PyBus.Instance().post(msg)

        ok = event.wait(timeout=timeout)
        if ok:
            print(f"P{self.myId} sendToSync -> ACK received for msg_id={msg.getId()}")
        else:
            print(f"P{self.myId} sendToSync -> TIMEOUT for msg_id={msg.getId()}")

        self.pending_send.pop(msg.getId(), None)
        return ok

    def recvFromSync(self, payload, source, timeout=10):
        ev = self.pending_recv.get(source)
        if ev is None:
            ev = Event()
            self.pending_recv[source] = ev

        ok = ev.wait(timeout=timeout)
        msg = self.received_sync_msgs.pop(source, None)
        self.pending_recv.pop(source, None)

        if ok:
            print(f"P{self.myId} recvFromSync -> received from P{source}: {msg.getPayload()}")
        else:
            print(f"P{self.myId} recvFromSync -> TIMEOUT waiting for P{source}")

        return msg



    # Event Handlers

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, message):
        if self.getMyId() != message.getSender():
            self.mailbox.addMessage(message)

    @subscribe(threadMode = Mode.PARALLEL, onEvent=MessageTo)
    def receiveFrom(self, message):
        if self.getMyId() == message.getDestId():
            self.mailbox.addMessage(message)
        
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageToSync)
    def onSyncMsg(self, msg):
        if msg.getDestId() == self.myId:
            self.received_sync_msgs[msg.getSender()] = msg
            # Déclenche le Event de recvFromSync
            ev = self.pending_recv.get(msg.getSender())
            if ev:
                ev.set()
            # Répond avec un ACK pour le sender
            ack = AckMessage(self.myId, msg.getSender(), msg.getId())
            PyBus.Instance().post(ack)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=AckMessage)
    def onAck(self, ack):
        if ack.getDestId() == self.myId:
            ev = self.pending_send.get(ack.getId())
            if ev:
                ev.set()

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        pass

    def releaseSC(self):
        pass
