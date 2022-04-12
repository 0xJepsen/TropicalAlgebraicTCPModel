from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
from Modelingfncs import Make_Y, delay, A_from_components
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt


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
SIM_TIME = 200

# V_n = {1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 1, 1, 2, 2, 2, 3, 3, 3, 3}

env = simpy.Environment()  # Create the SimPy environment


# Create the packet generators and sink
def main():
    pg = PacketGenerator(
        env, "Generator", constArrival, distSize, LINK_BANDWIDTH
    )
    s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    ps = PacketSink(3, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)

    l1 = Link(0, env, LINK_BANDWIDTH)
    l2 = Link(1, env, LINK_BANDWIDTH)
    l3 = Link(2, env, LINK_BANDWIDTH)

    # Wire packet generators and sink together
    pg.out = l1
    l1.out = s1
    s1.out = l2
    l2.out = s2
    s2.out = l3
    l3.out = ps
    ps.out = pg
    env.run(until=SIM_TIME)

    print(
        "received: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
            ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
        )
    )
    df = pd.DataFrame.from_dict(ps.data)
    df_simulated = df.transpose()
    pprint(df_simulated.iloc[5:11])

    # pck = 1
    # pprint(df_simulated.iloc[pck])
    # pck_v_n = df_simulated.iloc[pck]['V_n']
    # # def A_from_components(packet_number, max_window, number_of_routers, packet_v_n):
    #
    # test = A_from_components(pck, 4, 4, pck_v_n)

    """Logic for error extraction of Y_n"""
    df_simulated_departures = df_simulated.loc[:, ["departures"]]
    print("---------- Simulated Departure Data ----------")
    pprint(df_simulated_departures.head())

    generated_departures = Make_Y(ps.packets_rec - 1, 3, 4)
    df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    print("---------- Generated Departure Data ----------")
    pprint(df_generated.iloc[0:12])


    errors = {}
    for i in range(0, ps.packets_rec):
        errors[i] = {}
        for j in range(0, 4):
            errors[i]['Router {}'.format(j)] = abs(
                df_generated.values[i][0][j] - df_simulated_departures.values[i][0][j])

    df_errors = pd.DataFrame.from_dict(errors, orient='index')
    df_errors["sum"] = df_errors.sum(axis=1)

    # print("---------- Error In Departure Times ----------")
    # pprint(df_errors.iloc[8:13])
    # ax = df_errors.plot()
    # ax.set_ylabel('Quantity of Error')
    # ax.set_xlabel('Packet Number')
    # plt.show()


if __name__ == '__main__':
    main()
