from random import expovariate
from scipy.stats import poisson
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, link

MU = 0.6 # Arrival distributed parameter mu for poisson inter arival time
LINK_BANDWIDTH = 100
SWITCH_BANDWIDTH = 100
SWITCH_QSIZE = 50 # in bytes
LAMBDA = .02 # e^(-0.3)x

def constArrival():  # Constant arrival distribution for generator 1
    return int(poisson.rvs(MU)) # using Poisson interarrival time to model bursty traffic

def distSize():
    return expovariate(LAMBDA) # packet size distribution

def delay(src, dst):
    # TODO:
    return #time delay between router i and router j

def sigma(i, n):
    return # agrigated service time of packet n at router i

def M():
    return # Matrix object

def Mprime():
    return # Matrix object

def make_A(vn, n):
    """ vn is the window size experienced by packet n
        n is the packet number
    """
    return # A_vn 

env = simpy.Environment()  
# Create the SimPy environment
# Create the packet generators and sink
pg = PacketGenerator(env, "Generator", constArrival, distSize)
ps = PacketSink(env, debug=True)  # debugging enable for simple output
l1 = link(env, LINK_BANDWIDTH)
l2 = link(env, LINK_BANDWIDTH)
l3 = link(env, LINK_BANDWIDTH)
s1 = SwitchPort(env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
s2 = SwitchPort(env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
# Wire packet generators and sink together
# pg.out = l1
# l1.out = s1
# s1.out = l2
# l2.out = s2
# s2.out = l3
# l3.out = ps 
pg.out = s1
s1.out = s2
s2.out = ps
env.run(until=20)
#print("waits: {}".format(ps.waits))
print("s1 Sigma = {}".format(s1.sigma)) ## collection sigma's in packets, need to verify this
print("recieved: {}, s1 dropped {}, s2 dropped {}, sent {}".format(ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent))
