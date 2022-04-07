from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort
# from Modelingfncs import Y_i, delay
import pandas as pd
from pprint import pprint


def constArrival():  # Constant arrival distribution for generator 1
    return 1.5


def constArrival2():
    return 2.0


# def distSize():
#     return expovariate(0.01)
distSize = 10
SWITCH_BANDWIDTH = 10
LINK_BANDWIDTH = 10
SWITCH_QSIZE = 50
SIM_TIME = 75

V_n = {1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 1, 1, 2, 2, 2, 3, 3, 3, 3}

env = simpy.Environment()  # Create the SimPy environment


# Create the packet generators and sink
def main():
    pg = PacketGenerator(
        env, "Generator", constArrival, distSize, LINK_BANDWIDTH
    )
    s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    ps = PacketSink(3, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)

    # Wire packet generators and sink together
    pg.out = s1
    s1.out = s2
    s2.out = ps
    ps.out = pg
    env.run(until=SIM_TIME)

    # pprint(ps.data)
    df = pd.DataFrame.from_dict(ps.data)
    df = df.transpose()
    print(df)
    print(
        "recieved: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
            ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
        )
    )
    print(df['departures'][0][0])

    # departure = [[df['departures'][0][0]]]
    # print(departure[0][0])
    # for i in range(0, 3):
    #     print("i: ", i)
    #     departure[0].append(Y_i(departure[0][i], 0))
    #
    # pprint(departure)
    #
    # packet_1 = [departure[0][3] + 3]
    # for i in range(0,3):
    #     packet_1.append(Y_i(packet_1[i], 1))
    # pprint(packet_1)

    # for j in range(0, ps.packets_rec -2):
    #     for i in range(0, 3):
    #         print("i: ", i)
    #         departure[j].append(Y_i(departure[j][i], j))
    #         if i == 2:
    #             # print(departure[0][i+1])
    #             departure.append([departure[0][i+1] + 3])
    # print(departure)
    # print(y_1_0)
    # y_2_0 = Y_i(y_1_0, 0)
    # print(y_2_0)
    # y_3_0 = Y_i(y_2_0, 0)
    # print(y_3_0)

    # y_0_1 =

if __name__ == '__main__':
    main()
