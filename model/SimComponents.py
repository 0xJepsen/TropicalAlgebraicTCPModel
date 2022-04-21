"""
    A restructure of simulation components from Greg M. Bernstein
    Most is all original work from Waylon Jepsen, as the initial sim components
    didn't fit my needs.
"""
import simpy
import random
import copy
from simpy.core import BoundClass
from simpy.resources import base
from simpy.events import AnyOf, AllOf, Event
from heapq import heappush, heappop


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
        self.arrival = {}
        self.departure = {}
        self.v_n = 0

    def __repr__(self):
        return "id: {}, src: {}, time: {}, size: {}". \
            format(self.id, self.src, self.time, self.size)


class Ack(object):

    def __init__(self, pkt: Packet, src, dst, flow_id=0):
        self.size = 0.03 / pkt.size
        self.id = pkt.id
        self.arrival = {}
        self.departure = {}
        self.src = src
        self.dst = dst
        self.flow_id = flow_id

    def __repr__(self):
        return "id: {}, src: {}, dst: {}, size: {}". \
            format(self.id, self.src, self.dst, self.size)


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

    def __init__(self, env, id, size, link_rate, max_window, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.size = size
        self.processing_time = link_rate
        self.initial_delay = initial_delay
        self.finish = finish
        self.received = simpy.Store(env)
        self.buf2 = simpy.Store(env)
        self.front = None
        self.back = None
        self.packets_sent = 0
        self.generate = env.process(self.send_it())
        self.dst = None
        self.flow_id = flow_id
        self.window = 1  # slow start
        self.init = True
        self.acks = 0
        self.last_sent = None
        self.last_received = None
        self.max_window = max_window
        self.sent_per_window = 0
        self.seen_ack = []

    def send_it(self):
        # self.front.back = self
        """The generator function used in simulations.
        """
        # V_n = {1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 1, 1, 2, 2, 2, 3, 3, 3, 3}
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            if self.init:
                p = self.gen_packets()
                p.v_n = self.window
                self.init = False
                # first ack
                msg = yield self.received.get()
                self.last_received = msg.id
                self.seen_ack.append(msg.id)
                # print("Received message: ", msg.id)
                print(self.env.now)

                self.acks += 1
            while self.sent_per_window <= self.window:
                if (self.last_sent + 1 - p.v_n) in self.seen_ack:
                    p = self.gen_packets()
                    yield self.env.timeout(p.size / self.processing_time)  # Sigma_0(p.id)
                    p.v_n = self.window
                else:
                    msg = yield self.received.get()
                    self.last_received = msg.id
                    self.seen_ack.append(msg.id)
                    self.acks += 1
                if self.window == self.max_window and self.sent_per_window > 0:
                    self.window = 1
                    self.sent_per_window = 0
                if self.sent_per_window == self.window + 1:
                    self.window += 1
                    self.sent_per_window = 0

    def receive(self, pkt):
        self.received.put(pkt)

    def gen_packets(self):
        p = Packet(self.env.now, self.size, self.packets_sent, src=self.id, dst=self.dst, flow_id=self.flow_id)
        p.dst = self.dst
        self.packets_sent += 1
        self.sent_per_window += 1
        self.last_sent = p.id
        self.out.send(p)
        p.departure[0] = int(self.env.now)
        return p

    def put(self, pkt):
        self.store.put(pkt)


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
            msg.arrival[self.out.back.id + 1] = int(self.env.now)
            yield self.env.timeout(msg.size / self.rate)  # processing time
            msg.departure[self.out.back.id + 1] = int(self.env.now)
            # print("Time pkt {} leaves Sink: {}".format(msg.id, self.env.now))
            self.packets_rec += 1
            self.data[msg.id] = {
                "arrivals": msg.arrival,
                "departures": msg.departure,
                "link time": msg.size / self.rate,
                "V_n": msg.v_n,
            }
            self.out.receive(msg)
            if self.debug:
                print(msg)

    def generate_Ack(self, pkt: Packet):
        ack = Ack(pkt, self.id, pkt.dst, flow_id=pkt.flow_id)
        return ack

    def set_arrival(self, pkt):
        pkt.arrival[self.id] = round(self.env.now, 3)

    def send(self, pkt):
        return self.store.put(pkt)


class Link(object):
    """ Receives packets, yields a link time and sends them to next resources store.
        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        rate : float
            the bit rate of the link
    """

    def __init__(self, env, rate):
        self.rate = rate
        self.buf1 = simpy.Store(env)
        self.buf2 = simpy.Store(env)
        self.env = env
        self.run_buf1 = env.process(self.run_buffer_1())
        self.run_buf2 = env.process(self.run_buffer_2())
        self.front = None
        self.back = None

    def run_buffer_1(self):
        # self.front.back = self
        while True:
            with self.buf1.get() as re:
                msg = yield re
                yield self.env.timeout(msg.size / self.rate)
                self.front.send(msg)

    def run_buffer_2(self):

        while True:
            with self.buf2.get() as re:
                msg = yield re
                # print("Link recieved msg")
                yield self.env.timeout(msg.size / self.rate)
                self.back.receive(msg)

    def send(self, pkt):
        self.buf1.put(pkt)

    def receive(self, pkt):
        self.buf2.put(pkt)


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

    def __init__(self, id, env, rate, destinations, qlimit=None, limit_bytes=True, debug=False):
        self.id = id
        self.buf1 = simpy.Store(env)
        self.buf2 = simpy.Store(env)
        self.rate = rate
        self.env = env
        self.run_buf1 = env.process(self.run_buffer_1())
        self.run_buf2 = env.process(self.run_buffer_2())
        self.front = None
        self.back = None
        self.out = []
        self.outback = []
        self.destinations = destinations
        self.routing_rules = {}
        self.time_last_sent = 0
        self.packets_rec = 0
        self.packets_drop = 0
        self.qlimit = qlimit
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent

    #     if len(self.out) == 1:
    #         # self.front = self.out[0]
    #         for dst in destinations:
    #             self.routing_rules[dst] = self.out
    #     else:
    #         for out in self.out:
    #             if out.front.id == pkt.dst:
    #
    # def pop_routing_table(self):
    #     for dst in self.destinations:
    #         for out in self.out:
    #             if out.front.id == dst:
    #                 self.routing_rules[dst] = out
    #                 break
    #             else:

    def pop_routing_table(self):  # self.id, self.destination
        for dst in self.destinations:  # find destination for each destination
            for child in self.out:
                if child.front.id == dst:
                    self.routing_rules[dst] = out
                    return True
                for x in child.front.out:  # not sure this recursive part is right
                    if find_dest(x):
                        return true

    def run_buffer_1(self):
        # self.front.back = self
        while True:
            with self.buf1.get() as request:
                msg = yield request
                msg.arrival[self.id] = int(self.env.now)
                # print("Arrival of Pkt {} at Switch {}: {}".format(msg.id, self.id, self.env.now))
                yield self.env.timeout(msg.size / self.rate)  # processing time
                msg.departure[self.id] = int(self.env.now)
                # print("departure of Pkt {} at Switch {}: {}".format(msg.id, self.id, self.env.now))
                # print("packet flow_id: ", msg.flow_id)
                if len(self.out) == 1:
                    self.front = self.out[0]
                else:
                    self.front = self.out[msg.flow_id]
                    # print("out 1 id: ", self.out[0].front.id)
                    # print("type :", self.out[0].front)
                    # print("out 2 id: ", self.out[1].front.id)
                    # print("type :", self.out[1].front)

                # print("front: ", self.front.front.id)
                # self.front
                self.front.send(msg)

    def run_buffer_2(self):
        while True:
            with self.buf2.get() as request:
                msg = yield request
                # yield self.env.timeout(msg.size / self.rate)  # processing time
                # print("msg flow ID", msg.flow_id)
                # print(self.outback)
                if len(self.outback) == 1:
                    self.back = self.outback[0]
                else:
                    self.back = self.outback[msg.flow_id]
                #     print("out 1 id: ", self.outback[0].back.id)
                #     print("type :", self.outback[0].back)
                #     print("out 2 id: ", self.outback[1].back.id)
                #     print("type :", self.outback[1].back)
                #
                # print("front: ", self.front.front.id)
                # self.front
                self.back.receive(msg)

    def send(self, pkt):
        self.buf1.put(pkt)

    def receive(self, pkt):
        self.buf2.put(pkt)
    # def put(self, pkt):
    #     self.packets_rec += 1
    #     tmp_byte_count = self.byte_size + pkt.size
    #
    #     if self.qlimit is None:
    #         self.byte_size = tmp_byte_count
    #         return self.store.put(pkt)
    #     elif not self.limit_bytes and len(self.store.items) >= self.qlimit - 1:
    #         self.packets_drop += 1
    #     else:
    #         self.byte_size = tmp_byte_count
    #         return self.input.put(pkt)
