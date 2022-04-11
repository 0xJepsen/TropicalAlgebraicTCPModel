"""
    A bit more detailed set of components to use in packet switching
    queueing experiments.
    Copyright 2014 Greg M. Bernstein
    Released under the MIT license
"""
import simpy
import random
import copy
from simpy.core import BoundClass
from simpy.resources import base
from heapq import heappush, heappop
import threading


class Packet(object):
    """ A very simple class that represents a packet.
        This packet will run through a queue at a switch output port.
        We use a float to represent the size of the packet in bytes so that
        we can compare to ideal M/M/1 queues.

        Parameters
        ----------
        time : float
            the time the packet arrives at the output queue.
        size : float
            the size of the packet in bytes
        id : int
            an identifier for the packet
        src, dst : int
            identifiers for source and destination
        flow_id : int
            small integer that can be used to identify a flow
    """

    def __init__(self, time, size, id, src="a", dst="z", flow_id=0):
        self.time = time
        self.size = size
        self.id = id
        self.src = src
        self.dst = dst
        self.flow_id = flow_id
        self.ltime = 0
        self.arrival = {}
        self.departure = {}
        self.v_n = 0

    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}". \
            format(self.id, self.src, self.time, self.size)


class PacketGenerator(object):
    """ Generates packets with given inter-arrival time distribution.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        adist : function
            a no parameter function that returns the successive inter-arrival times of the packets
        sdist : function
            a no parameter function that returns the successive sizes of the packets
        initial_delay : number
            Starts generation after an initial delay. Default = 0
        finish : number
            Stops generation at the finish time. Default is infinite


    """

    def __init__(self, env, id, adist, size, link_rate, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.adist = adist
        self.size = size
        self.link_rate = link_rate
        self.initial_delay = initial_delay
        self.finish = finish
        self.store = simpy.Store(env)
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.flow_id = flow_id
        self.window = 1  # slow start
        self.init = True
        self.acks = 0
        self.last_sent = None
        self.last_received = None
        self.max_window = 4
        self.sent_per_window = 0
        self.next_window = 1
        self.seen_ack = []

    def run(self):
        """The generator function used in simulations.
        """
        # V_n = {1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 1, 1, 2, 2, 2, 3, 3, 3, 3}
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            if self.init:
                p = self.gen_packets()
                print("V_n for packet 0: ", self.window)
                p.v_n = self.window
                self.init = False
                # first ack
                msg = yield self.store.get()
                self.last_received = msg.id
                self.seen_ack.append(msg.id)
                print("Recieved message: ", msg.id)
                print(self.env.now)
                yield self.env.timeout(3)
                print(self.env.now)

                self.acks += 1
            while self.sent_per_window <= self.window:
                if (self.last_sent + 1 - p.v_n) in self.seen_ack:
                    p = self.gen_packets()
                    p.v_n = self.window
                    print("packet V_n: ", p.v_n)
                    print("Sent per window: ", self.sent_per_window)
                else:
                    print("Time before receiveing: ", self.env.now)
                    msg = yield self.store.get()
                    self.last_received = msg.id
                    print("message departure time: ", msg.departure[3])
                    print("Time before delay yield: ", self.env.now)
                    while self.env.now != msg.departure[3] + 3:
                        yield self.env.timeout(1)
                    self.seen_ack.append(msg.id)
                    self.acks += 1
                    print("Recieved msg id: ", self.last_received)
                    print("Current Time: ", self.env.now)
                if self.window == self.max_window and self.sent_per_window > 0:
                    self.window = 1
                    self.sent_per_window = 0
                if self.sent_per_window == self.window + 1:
                    print("increasing next window size")
                    self.window += 1
                    self.next_window += 1
                    self.sent_per_window = 0

                print("end")

    def gen_packets(self):
        p = Packet(self.env.now, self.size, self.packets_sent, src=self.id, flow_id=self.flow_id)
        p.ltime = p.size / self.link_rate
        p.departure[0] = int(self.env.now)
        print(p)
        self.packets_sent += 1
        self.sent_per_window += 1
        self.last_sent = p.id
        self.out.put(p)
        self.env.timeout(p.ltime)
        return p

    def put(self, pkt):
        return pkt


class PacketSink(object):
    """ Receives packets and collects delay information into the
        waits list. You can then use this list to look at delay statistics.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        debug : boolean
            if true then the contents of each packet will be printed as it is received.
        rec_arrivals : boolean
            if true then arrivals will be recorded
        absolute_arrivals : boolean
            if true absolute arrival times will be recorded, otherwise the time between consecutive arrivals
            is recorded.
        rec_waits : boolean
            if true waiting time experienced by each packet is recorded
        selector: a function that takes a packet and returns a boolean
            used for selective statistics. Default none.

    """

    def __init__(self, id, env, rate, qlimit=None, limit_bytes=True, debug=False):
        self.id = id
        self.store = simpy.Store(env)
        self.rate = rate
        self.env = env
        self.out = None
        self.packets_rec = 0
        self.packets_drop = 0
        self.qlimit = qlimit
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent
        self.data = {}
        self.action = env.process(self.run())  # starts the run() method as a SimPy process

    def run(self):
        while True:
            msg = (yield self.store.get())
            self.busy = 1
            self.byte_size -= msg.size
            msg.arrival[self.id] = int(self.env.now)
            yield self.env.timeout(msg.size / self.rate)  # processing time
            msg.departure[self.id] = int(self.env.now)
            self.packets_rec += 1
            self.data[msg.id] = {
                "arrivals": msg.arrival,
                "departures": msg.departure,
                "link time": msg.ltime,
                "V_n": msg.v_n,
            }
            self.out.store.put(msg)
            if self.debug:
                print(msg)

    def set_arrival(self, pkt):
        pkt.arrival[self.id] = round(self.env.now, 3)

    def put(self, pkt):
        return self.store.put(pkt)


class Link(object):

    def __init__(self, id, env, rate):
        self.id = id
        self.rate = rate
        self.store = simpy.Store(env)
        self.env = env
        self.action = env.process(self.run())
        self.out = None

    def run(self):
        while True:
            with self.store.get() as re:
                print("Waiting for pck")
                msg = yield re
                print("received pckt. Processing...")
                yield self.env.timeout(msg.size / self.rate)
                print("Processed pck, sent to switch ...")
                self.out.put(msg)


    def put(self, pkt):
        self.store.put(pkt)

class SwitchPort(object):
    """ Models a switch output port with a given rate and buffer size limit in bytes.
        Set the "out" member variable to the entity to receive the packet.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        rate : float
            the bit rate of the port
        qlimit : integer (or None)
            a buffer size limit in bytes or packets for the queue (including items
            in service).
        limit_bytes : If true, the queue limit will be based on bytes if false the
            queue limit will be based on packets.

    """

    def __init__(self, id, env, rate, qlimit=None, limit_bytes=True, debug=False):
        self.id = id
        self.input = simpy.Store(env)
        # self.output = simpy.Store(env)
        self.rate = rate
        self.env = env
        self.out = None
        self.time_last_sent = 0
        self.packets_rec = 0
        self.packets_drop = 0
        self.qlimit = qlimit
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.input_thread = threading.Event()
        # self.tasks = [([self.input, self.output], [self.process_input(), self.process_output()])]


    def run(self):
        while True:

            with self.input.get() as request:
                print("ROUTER {} Waiting for output".format(self.id))
                msg = yield request
                msg.arrival[self.id] = int(self.env.now)
                print("ROUTER {} output received packet {} at time {}".format(self.id, msg.id, self.env.now))
                print("ROUTER {} output processing link time for packet {}...".format(self.id, msg.id))
                yield self.env.timeout(msg.ltime)  # processing time
                msg.departure[self.id] = int(self.env.now)
                self.out.put(msg)

    # def process_output(self):
    #     with self.output.get() as request:
    #         print("ROUTER {} Waiting for output".format(self.id))
    #         msg = yield request
    #         print("ROUTER {} output received packet {} at time {}".format(self.id, msg.id, self.env.now))
    #         print("ROUTER {} output processing link time for packet {}...".format(self.id, msg.id))
    #         yield self.env.timeout(msg.ltime)  # processing time
    #         msg.departure[self.id] = int(self.env.now)
    #         self.out.put(msg)

    def put(self, pkt):
        self.packets_rec += 1
        tmp_byte_count = self.byte_size + pkt.size

        if self.qlimit is None:
            self.byte_size = tmp_byte_count
            return self.store.put(pkt)
        elif not self.limit_bytes and len(self.store.items) >= self.qlimit - 1:
            self.packets_drop += 1
        else:
            self.byte_size = tmp_byte_count
            return self.input.put(pkt)
