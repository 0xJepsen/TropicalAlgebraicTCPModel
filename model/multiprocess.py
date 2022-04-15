import simpy
from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
from Modelingfncs import Make_Y, delay, A_from_components, Z_continuous, Z_init
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from Simulation import SimulationConfig

config = SimulationConfig("sim1", 4, 4)
config.make_Vn()

distSize = 10
SWITCH_BANDWIDTH = 10
LINK_BANDWIDTH = 10
SWITCH_QSIZE = 50
SIM_TIME = 100

WINDOW_SIZE = 4
NUMBER_OF_SWITCHES = 4

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
        "received: {}, sent {}".format(
            ps.packets_rec, pg.packets_sent
        )
    )
    df = pd.DataFrame.from_dict(ps.data)
    df_simulated = df.transpose()
    return df_simulated, ps


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

def run():
    # df_sim, ps = simulate(config)
    # print(df_sim)
    validate_Y(config)

run()

