from Mailbox import Mailbox
from Message import Message

from pyeventbus3.pyeventbus3 import *
from Message import Message, MessageTo
from threading import Event

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

    def sendTo(self, payload, dest):
        msg = MessageTo(self.getMyId(), dest, payload)
        print(self.name + " sendTo P" + str(dest) +
              ": " + str(payload) )
        PyBus.Instance().post(msg)
        pass



    def sendToSync(self, message, dest):
        # créer un objet Event pour attendre la réponse
        ack_event = Event()
        response_container = {}

        PyBus.Instance().register(handle_ack, handle_ack)

        # envoyer le message
        msg = MessageTo(self.getMyId(), dest, message)
        print(f"{self.getMyId()} sendToSync P{dest}: {message}")
        PyBus.Instance().post(msg)

        # attendre la réponse
        ack_event.wait(timeout=5)

        return response_container.get('msg', None)


    # handler pour réception de l'ack
    @subscribe(threadMode=Mode.PARALLEL, onEvent=MessageTo)
    def handle_ack_sync(msg):
        if msg.getReceiver() == self.getMyId() and msg.getSender() == dest:
            # stocker la réponse
            response_container['msg'] = msg
            # débloquer le wait
            ack_event.set()
            # se désabonner après réception
            PyBus.Instance().unregister(handle_ack)

    def recvFromSync(self, source):
        pass

    def synchronize(self):
        pass

    # Section Critique

    def requestSC(self):
        pass

    def releaseSC(self):
        pass
