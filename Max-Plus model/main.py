from random import expovariate
from scipy.stats import poisson
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort

MU = 0.6 # Arrival distributed parameter mu for poisson inter arival time
BANDWIDTH = 1000000 # 1mb/s
QSIZE = 500000 # in bytes
LAMBDA = 0.3 # e^(-0.3)x

def constArrival():  # Constant arrival distribution for generator 1
    return int(poisson.rvs(MU)) # using Poisson interarrival time to model bursty traffic

def distSize():
    return expovariate(LAMBDA) # packet size distribution

env = simpy.Environment()  
# Create the SimPy environment
# Create the packet generators and sink
ps = PacketSink(env, debug=True)  # debugging enable for simple output
pg = PacketGenerator(env, "Generator", constArrival, distSize)
s1 = SwitchPort(env, rate=BANDWIDTH, qlimit=QSIZE)
s2 = SwitchPort(env, rate=BANDWIDTH, qlimit=QSIZE)
# Wire packet generators and sink together
pg.out = s1
s1.out = s2
s2.out = ps
env.run(until=20)
#print("waits: {}".format(ps.waits))
print("s1 Sigma = {}".format(s1.sigma)) ## collection sigma's in packets, need to verify this
print("recieved: {}, s1 dropped {}, s2 dropped {}, sent {}".format(ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent))
