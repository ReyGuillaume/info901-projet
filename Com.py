from Mailbox import Mailbox
from enum import Enum
import random
from pyeventbus3.pyeventbus3 import *
from threading import Event, Thread
from Message import *
import time
from time import sleep

M = 10000 

class Com():
    NB_PROCESS = 0

    def __init__(self):

        self.stateSC = StateSC.NULL
        self.lamport = 0
        self.nbSynchronize = 0
        self.synchronizeEvent = Event()
        self.nbSynchronizeBroadcastAck = 0
        self.synchronizeBroadcastEvent = Event()
        self.mailbox = Mailbox()

        self.pending_send = {}
        self.pending_recv = {}
        self.received_sync_msgs = {}

        self.my_value = None
        self.tmp_id = str(uuid.uuid4())

        self.random_draws = {}
        self.rand_event = Event()
        self.myId = None

        PyBus.Instance().register(self, self)                                            

        self.last_heartbeat = {}
        self.alive = True

        self.heartbeat_thread = Thread(target=self.heartbeat_loop, daemon=True)
        self.monitor_thread = Thread(target=self.monitor_loop, daemon=True)
                                        
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

    def elect_id(self, timeout=2.0):
        while True:
            if self.my_value is None:
                self.my_value = random.randint(0, M)

            PyBus.Instance().post(RandDrawMessage(self.tmp_id, self.my_value))

            start = time.time()
            while time.time() - start < timeout:
                self.rand_event.wait(timeout=0.1)
                self.rand_event.clear()

            all_values = list(self.random_draws.values()) + [self.my_value]

            duplicates = [v for v in all_values if all_values.count(v) > 1]

            if not duplicates:
                sorted_values = sorted(all_values)
                self.myId = sorted_values.index(self.my_value)
                Com.NB_PROCESS = len(all_values)

                self.heartbeat_thread.start()
                self.monitor_thread.start()
                self.last_heartbeat[self.myId] = time.time()

                return self.myId
            else:
                if self.my_value in duplicates:
                    while True:
                        new_value = random.randint(0, M)
                        if new_value not in all_values:
                            self.my_value = new_value
                            break
                            

    def heartbeat_loop(self):
        while self.alive:
            hb = HeartbeatMessage(self.myId, time.time())
            PyBus.Instance().post(hb)
            time.sleep(2)

    def monitor_loop(self):
        while self.alive:
            now = time.time()
            dead = []
            for pid, ts in list(self.last_heartbeat.items()):
                if pid != self.myId and now - ts > 5:
                    dead.append(pid)

            for pid in dead:
                print(f"P{self.myId} detected that P{pid} is dead")
                self.handle_process_death(pid)

            time.sleep(1)

    def handle_process_death(self, dead_id):
        if dead_id in self.last_heartbeat:
            del self.last_heartbeat[dead_id]

        Com.NB_PROCESS -= 1

        if self.myId > dead_id:
            self.myId -= 1
            print(f"P{self.myId} updated its ID after death of P{dead_id}")

    
    def broadcast(self, message):
        msg = BroadcastMessage(self.lamport, message, self.getMyId())
        PyBus.Instance().post(msg)

    def broadcastSync(self, message):
        msg = BroadcastSyncMessage(self.lamport, message, self.getMyId())
        PyBus.Instance().post(msg)
        self.synchronizeBroadcastEvent.wait()

    def sendTo(self, payload, dest):
        msg = MessageTo(self.lamport, payload, self.getMyId(), dest)
        print(str(self.getMyId()) + " sendTo P" + str(dest) +
              ": " + str(payload) )
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
        ev = self.pending_recv.setdefault(source, Event())

        ok = ev.wait(timeout=timeout)
        msg = self.received_sync_msgs.pop(source, None)
        self.pending_recv.pop(source, None)

        if ok and msg:
            print(f"P{self.myId} recvFromSync -> received from P{source}: {payload}")
        else:
            print(f"P{self.myId} recvFromSync -> TIMEOUT waiting for P{source}")

        return msg



    # Event Handlers

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastMessage)
    def onBroadcast(self, message):
        if self.getMyId() != message.getSender():
            self.mailbox.addMessage(message)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastSyncMessage)
    def onBroadcastSynchronize(self, message):
        if self.getMyId() != message.getSender():
            self.mailbox.addMessage(message)
            
            ack = BroadcastSyncAckMessage(self.myId, message.getSender())
            PyBus.Instance().post(ack)

    @subscribe(threadMode=Mode.PARALLEL, onEvent=SynchronizeMessage)
    def onSynchronize(self, _):
        self.nbSynchronize += 1

        if self.nbSynchronize == Com.NB_PROCESS:
            self.synchronizeEvent.set()
            self.nbSynchronize = 0

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
    
    @subscribe(threadMode=Mode.PARALLEL, onEvent=BroadcastSyncAckMessage)
    def onAck(self, ack):
        if ack.getDestId() == self.myId:
            self.nbSynchronizeBroadcastAck += 1
            
            if self.nbSynchronizeBroadcastAck == Com.NB_PROCESS - 1:
                self.synchronizeBroadcastEvent.set()
                self.nbSynchronizeBroadcastAck = 0

    @subscribe(threadMode=Mode.PARALLEL, onEvent=RandDrawMessage)
    def onRandDraw(self, msg):
        if msg.sender != self.tmp_id:
            self.random_draws[msg.sender] = msg.value
            self.rand_event.set()

    @subscribe(threadMode=Mode.PARALLEL, onEvent=HeartbeatMessage)
    def onHeartbeat(self, msg):
        self.last_heartbeat[msg.sender] = msg.timestamp


    def synchronize(self):
        msg = SynchronizeMessage()
        PyBus.Instance().post(msg)
        self.synchronizeEvent.wait()

        if self.nbSynchronize == Com.NB_PROCESS:
            self.synchronizeEvent.set()
            self.nbSynchronize = 0

    # Section Critique

    def requestSC(self):
        self.stateSC = StateSC.REQUEST
        while self.stateSC != StateSC.SC:
            continue

    def releaseSC(self):
        if self.stateSC != StateSC.SC:
            return
        
        self.stateSC = StateSC.RELEASE

    @subscribe(threadMode = Mode.PARALLEL, onEvent=Token)
    def onToken(self, token):
        if token.getOwner() == self.getMyId():
            if self.stateSC == StateSC.REQUEST:
                self.stateSC = StateSC.SC
            while self.stateSC == StateSC.SC:
                continue
            self.sendTokenToNextProcess()
            self.stateSC = StateSC.NULL

    def sendTokenToNextProcess(self):
        PyBus.Instance().post(Token(self.nextProcess()))

    def nextProcess(self):
        return (self.getMyId() + 1) % Com.NB_PROCESS




class StateSC(Enum):
    NULL = 0
    REQUEST = 1
    SC = 2
    RELEASE = 3
