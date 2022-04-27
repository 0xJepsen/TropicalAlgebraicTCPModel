"""
    A restructure of simulation components from Greg M. Bernstein
    Most is all original work from Waylon Jepsen, as the initial sim components
    didn't fit my needs.
"""
import simpy


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
    """ A very simple class that represents a packet acknowledgement.
        This ack will run through a queue at a switch output port.
        We use a float to represent the size of the packet in bytes so that
        we can compare to ideal M/M/1 queues.

        Parameters
        ----------
        pkt : a packet object
            the packet that this is an ack for
        src, dst : int
            identifiers for source and destination
        flow_id : int
            small integer that can be used to identify a flow
    """

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
        id : int
            id
        size : function
            a no parameter generator function that yields the successive sizes of the packets
        rate : int
            rate at which to process packets
        initial_delay : number
            Starts generation after an initial delay. Default = 0
        finish : number
            Stops generation at the finish time. Default is infinite
        flow_id : number
            distinguishes unique tcp connections
    """

    def __init__(self, env, id, size, rate, max_window, initial_delay=0, finish=float("inf"), flow_id=0):
        self.id = id
        self.env = env
        self.size = size
        self.processing_time = rate
        self.initial_delay = initial_delay
        self.finish = finish
        self.received = simpy.Store(env)
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
        """The generator function used in simulations.
        """
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
        p = Packet(self.env.now, next(self.size), self.packets_sent, src=self.id, dst=self.dst, flow_id=self.flow_id)
        p.dst = self.dst
        self.packets_sent += 1
        self.sent_per_window += 1
        self.last_sent = p.id
        self.out.send(p)
        p.departure[0] = self.env.now
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
        id : int
            packet sink id
        rate : int
            rate at which the packet sink can process packets.
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
            msg.arrival[self.out.back.id + 1] = self.env.now
            yield self.env.timeout(msg.size / self.rate)  # processing time
            msg.departure[self.out.back.id + 1] = self.env.now
            self.packets_rec += 1
            self.data[msg.id] = {
                "arrivals": msg.arrival,
                "departures": msg.departure,
                "link time": msg.size / self.rate,
                "V_n": msg.v_n,
                "Size": msg.size
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
        while True:
            with self.buf1.get() as re:
                msg = yield re
                yield self.env.timeout(msg.size / self.rate)
                self.front.send(msg)

    def run_buffer_2(self):

        while True:
            with self.buf2.get() as re:
                msg = yield re
                yield self.env.timeout(msg.size / self.rate)
                self.back.receive(msg)

    def send(self, pkt):
        self.buf1.put(pkt)

    def receive(self, pkt):
        self.buf2.put(pkt)


class SwitchPort(object):
    """ Receives packets and collects delay information into the
        waits list. You can then use this list to look at delay statistics.

        Parameters
        ----------
        env : simpy.Environment
            the simulation environment
        id : int
            packet sink id
        rate : int
            rate at which the packet sink can process packets.
    """

    def __init__(self, id, env, rate, qlimit=None, limit_bytes=True, debug=False):
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
        self.routing_rules = {}
        self.time_last_sent = 0
        self.packets_rec = 0
        self.packets_drop = 0
        self.qlimit = qlimit
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent

    def run_buffer_1(self):
        while True:
            with self.buf1.get() as request:
                msg = yield request
                msg.arrival[self.id] = self.env.now
                yield self.env.timeout(msg.size / self.rate)  # processing time
                msg.departure[self.id] = self.env.now
                if len(self.out) == 1:
                    self.front = self.out[0]
                else:
                    self.front = self.out[msg.flow_id]
                self.front.send(msg)

    def run_buffer_2(self):
        while True:
            with self.buf2.get() as request:
                msg = yield request
                if len(self.outback) == 1:
                    self.back = self.outback[0]
                else:
                    self.back = self.outback[msg.flow_id]
                self.back.receive(msg)

    def send(self, pkt):
        self.buf1.put(pkt)

    def receive(self, pkt):
        self.buf2.put(pkt)
