from random import expovariate
import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
from Modelingfncs import Make_Y, delay, A_from_components, Z_continuous, Z_init
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from Simulation import SimulationConfig


# def distSize():
#     return expovariate(0.01)
config = SimulationConfig("sim1", 4, 4)
config.make_Vn()

distSize = 10
SWITCH_BANDWIDTH = 10
LINK_BANDWIDTH = 10
SWITCH_QSIZE = 50
SIM_TIME = 30

WINDOW_SIZE = 4
NUMBER_OF_SWITCHES = 4


# TODO: abstract these to be defined when the network initializes

def simulate():
    env = simpy.Environment()  # Create the SimPy environment
    pg = PacketGenerator(
        env, "Generator", distSize, LINK_BANDWIDTH
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
    return df_simulated, ps


# Create the packet generators and sink
def validate_Y():
    # TODO: ABSTRACT parameters
    df_simulated, ps = simulate()
    """Logic for error extraction of Y_n"""
    df_simulated_departures = df_simulated.loc[:, ["departures"]]
    print("---------- Simulated Departure Data ----------")
    pprint(df_simulated_departures.head())

    generated_departures = Make_Y(ps.packets_rec - 1, config)
    df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    print("---------- Generated Departure Data ----------")
    pprint(df_generated.head())
    errors = {}
    for i in range(0, ps.packets_rec):
        errors[i] = {}
        for j in range(0, 4):
            errors[i]['Router {}'.format(j)] = abs(
                df_generated.values[i][0][j] - df_simulated_departures.values[i][0][j])

    df_errors = pd.DataFrame.from_dict(errors, orient='index')
    df_errors["sum"] = df_errors.sum(axis=1)

    print("---------- Error In Departure Times ----------")
    ax = df_errors.plot()
    ax.set_ylabel('Quantity of Error')
    ax.set_xlabel('Packet Number')
    # plt.show()


def validate_Z(conf):
    df_simulated, ps = simulate()
    print("---------- Simulated Departure Data ----------")
    simulated_departures = df_simulated.loc[:, ["departures", "V_n"]]
    pprint(simulated_departures)


    # generated_departures = Make_Y(ps.packets_rec - 1, 4, 4)
    # df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    # print("---------- Generated Departure Data ----------")
    current_packet = 0

    # while current_packet < ps.packets_rec -1:
    #     current_z = Z_gen(current_packet, NUMBER_OF_SWITCHES, WINDOW_SIZE)

    errors_by_z = {}
    print(simulated_departures.head())

    zeee = Z_continuous(current_packet, ps.packets_rec-1, conf)
    for m in zeee.keys():
        print("N=", m)
        z = zeee[m].transpose()
        print(z)
        print(z.cols)

    #     current_packet += 1
    #     errors = {current_packet: {}}
    #     current_index_packet = current_packet
    #     breakpoint = 0
    #     total_pkts = 0
    #     for j in range(0, z.cols):
    #         if current_index_packet < 0:
    #             errors[current_index_packet]['Router {}'.format(j % number_of_routers)] = 0
    #         else:
    #             errors[current_index_packet]['Router {}'.format(j % number_of_routers)] = \
    #                 abs((current_z[j, 0]) - simulated_departures["departures"][current_index_packet][j % number_of_routers])
    #             breakpoint += 1
    #         if j%number_of_routers == number_of_routers - 1 and breakpoint >= number_of_routers -1:
    #             current_index_packet -=1
    #             total_pkts +=1
    #             if total_pkts < number_of_routers:
    #                 errors[current_index_packet] = {}
    #
    #         errors_by_z[current_packet] = errors

    # pprint(errors)



def main():
    # validate_Y()
    validate_Z(config)


if __name__ == '__main__':
    main()
