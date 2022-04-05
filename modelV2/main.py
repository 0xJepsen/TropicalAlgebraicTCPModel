from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort
from pprint import pprint
import pandas as pd


def constArrival():  # Constant arrival distribution for generator 1
    return 1.5


def constArrival2():
    return 2.0


# def distSize():
#     return expovariate(0.01)
distSize =10
SWITCH_BANDWIDTH =50
LINK_BANDWIDTH =10
SWITCH_QSIZE =50
SIM_TIME = 25

V_n = {1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 1, 1, 2, 2, 2, 3, 3, 3, 3}


env = simpy.Environment()  # Create the SimPy environment
# Create the packet generators and sink
pg = PacketGenerator(
    env, "Generator", constArrival, distSize, LINK_BANDWIDTH
)
ps = PacketSink(env)  # debugging enable for simple output
s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
# Wire packet generators and sink together
pg.out = s1
s1.out = s2
s2.out = ps
ps.out = pg
env.run(until=SIM_TIME)

# pprint(ps.data)
df = pd.DataFrame.from_dict(ps.data)
print(df.head())
print(
    "recieved: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
        ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
    )
)