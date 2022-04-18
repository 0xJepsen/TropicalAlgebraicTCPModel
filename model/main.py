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
SIM_TIME = 100

WINDOW_SIZE = 4
NUMBER_OF_SWITCHES = 4


# TODO: abstract these to be defined when the network initializes

def simulate(conf):
    env = simpy.Environment()  # Create the SimPy environment
    pg = PacketGenerator(
        env, "Generator", distSize, LINK_BANDWIDTH, conf.max_window
    )
    s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    ps = PacketSink(3, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)

    l1 = Link(0, env, LINK_BANDWIDTH)
    l2 = Link(1, env, LINK_BANDWIDTH)
    l3 = Link(2, env, LINK_BANDWIDTH)

    # Wire packet generators and sink together
    pg.out = l1
    l1.front = s1
    s1.front = l2
    l2.front = s2
    s2.front = l3
    l3.front = ps

    ps.out = l3
    l3.back = s2
    s2.back = l2
    l2.back = s1
    s1.back = l1
    l1.back = pg
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
def validate_Y(conf):
    # TODO: ABSTRACT parameters
    df_simulated, ps = simulate(conf)
    """Logic for error extraction of Y_n"""
    df_simulated_departures = df_simulated.loc[:, ["departures"]]
    print("---------- Simulated Departure Data ----------")
    pprint(df_simulated_departures.head())

    generated_departures = Make_Y(ps.packets_rec - 1, conf)
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
    pprint(df_errors)
    df_errors["sum"] = df_errors.sum(axis=1)

    print("---------- Error In Departure Times ----------")
    ax = df_errors.plot()
    ax.set_ylabel('Quantity of Error')
    ax.set_xlabel('Packet Number')
    plt.title("Error Between Y(n) and Simulated Traffic")
    plt.show()


def validate_Z(conf, flag=False):
    df_simulated, ps = simulate(conf)
    if flag:
        generated_departures = Make_Y(ps.packets_rec - 1, conf)
        data = pd.DataFrame.from_dict(generated_departures, orient='index')
    else:
        print("---------- Simulated Departure Data ----------")
        data = df_simulated.loc[:, ["departures", "V_n"]]

    current_packet = 0
    errors_by_z = {}

    zeee = Z_continuous(current_packet, ps.packets_rec - 1, conf)
    for m in zeee.keys():
        z = zeee[m].transpose()
        current_index_packet = m
        errors = {current_index_packet: {}}
        breakpoint = 0
        total_pkts = 0
        for j in range(0, z.cols):
            if current_index_packet < 0:
                errors[current_index_packet]['Router {}'.format(j % conf.number_of_routers)] = 0
                errors[current_index_packet]['packet'] = current_index_packet
            else:
                errors[current_index_packet]['Router {}'.format(j % conf.number_of_routers)] = \
                    abs((z[0, j]) - data["departures"][current_index_packet][j % conf.number_of_routers])
                breakpoint += 1
                errors[current_index_packet]['packet'] = current_index_packet
            if j % conf.number_of_routers == conf.number_of_routers - 1:
                current_index_packet -= 1
                total_pkts += 1
                if total_pkts < conf.number_of_routers:
                    errors[current_index_packet] = {}

            errors_by_z[m] = errors
    df = pd.DataFrame()
    for key in errors_by_z.keys():
        df_errors = pd.DataFrame.from_dict(errors_by_z[key], orient='index')
        df_errors["sum"] = df_errors[["Router 0", "Router 1", "Router 2", "Router 3"]].sum(axis=1)
        df = pd.concat([df, df_errors]).drop_duplicates(subset=['packet'])

    pprint(df.head())
    print("---------- Error In Departure Times ----------")
    new = df.drop(columns=["packet"], axis=1)
    pprint(new)
    ax = new.plot()
    ax.set_ylabel('Quantity of Error')
    ax.set_xlabel('Packet Number')
    plt.title("Error Between Z(n) and Simulated Traffic")
    plt.show()


def validate_z_against_y(conf):
    df_simulated, ps = simulate(conf)
    print("---------- Simulated Departure Data ----------")
    simulated_departures = df_simulated.loc[:, ["departures", "V_n"]]
    pprint(simulated_departures.head())
    generated_departures = Make_Y(ps.packets_rec - 1, conf)
    df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    print("---------- Generated Departure Data ----------")
    pprint(df_generated.head())


def main():
    # validate_Y(config)
    # sim, ps = simulate(config)
    # print(sim)
    # validate_z_against_y(config)
    # generated_departures = Make_Y(10, config)
    # df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    # print("---------- Generated Departure Data ----------")
    # pprint(df_generated)

    validate_Z(config)
    # df_simulated, ps = simulate(config)
    # pprint(df_simulated)


if __name__ == '__main__':
    main()
