from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
from Modelingfncs import Make_Y, delay, A_from_components, Z_continuous, Z_init
import simpy
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from Simulation import SimulationConfig


def simple_branch():
    conf = SimulationConfig("sim1", 4, 6)
    env = simpy.Environment()  # Create the SimPy environment
    pg1 = PacketGenerator(
        env, "Generator", conf.dist_size, conf.switch_rate, conf.max_window, flow_id=0
    )
    pg2 = PacketGenerator(
        env, "Generator", conf.dist_size, conf.switch_rate, conf.max_window, flow_id=1
    )

    # flow ID 0 goes to packet sink 3, and flow ID 1 goings to packet sink 4

    ps1 = PacketSink(3, env, rate=conf.switch_rate, qlimit=conf.switch_que_size)
    ps2 = PacketSink(4, env, rate=conf.switch_rate, qlimit=conf.switch_que_size)

    s1 = SwitchPort(1, env, conf.switch_rate, [ps1.id, ps2.id], qlimit=conf.switch_que_size)
    s2 = SwitchPort(2, env, conf.switch_rate, [ps1.id, ps2.id], qlimit=conf.switch_que_size)

    l1 = Link(env, conf.link_rate)
    l2 = Link(env, conf.link_rate)
    l3 = Link(env, conf.link_rate)
    l4 = Link(env, conf.link_rate)
    l5 = Link(env, conf.link_rate)

    # Set Destination for packets from pg

    pg1.dst = ps1.id
    pg2.dst = ps2.id

    # Wire packet generators and sink together

    pg1.out = l1
    l1.front = s1
    pg2.out = l2
    l2.front = s1

    s1.out.append(l3)
    l3.front = s2

    s2.out.append(l4)
    s2.out.append(l5)

    l4.front = ps1
    l5.front = ps2

    # wire back

    ps1.out = l4
    ps2.out = l5

    l4.back = s2
    l5.back = s2

    s2.outback.append(l3)
    l3.back = s1
    s1.outback.append(l1)
    s1.outback.append(l2)
    l2.back = pg2
    l1.back = pg1

    env.run(until=conf.sim_time)

    print(
        "received by PS1: {}, received by PS2: {}s1 dropped {}, s2 dropped {}, sent by PG1 {}, sent by PG2 {}".format(
            ps1.packets_rec, ps2.packets_rec, s1.packets_drop, s2.packets_drop, pg1.packets_sent, pg2.packets_sent
        )
    )
    df_1 = pd.DataFrame.from_dict(ps1.data)
    df_2 = pd.DataFrame.from_dict(ps2.data)
    df1_simulated = df_1.transpose()
    df2_simulated = df_2.transpose()
    return (df1_simulated, df2_simulated), (ps1, ps2)


def linear():
    conf = SimulationConfig("sim1", 4, 4)

    distSize = 10
    SWITCH_BANDWIDTH = 10
    LINK_BANDWIDTH = 10
    SWITCH_QSIZE = 50
    SIM_TIME = 100

    env = simpy.Environment()  # Create the SimPy environment
    pg = PacketGenerator(
        env, "Generator", distSize, LINK_BANDWIDTH, conf.max_window
    )

    ps = PacketSink(3, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
    s1 = SwitchPort(1, env, SWITCH_BANDWIDTH, [ps.id], qlimit=SWITCH_QSIZE)
    s2 = SwitchPort(2, env, SWITCH_BANDWIDTH, [ps.id], qlimit=SWITCH_QSIZE)

    l1 = Link(env, LINK_BANDWIDTH)
    l2 = Link(env, LINK_BANDWIDTH)
    l3 = Link(env, LINK_BANDWIDTH)

    # Set Destination for packets from pg

    pg.dst = ps.id

    # Wire packet generators and sink together

    pg.out = l1
    l1.front = s1
    s1.out.append(l2)
    l2.front = s2
    s2.out.append(l3)
    l3.front = ps

    ps.out = l3
    l3.back = s2
    s2.outback.append(l2)
    l2.back = s1
    s1.outback.append(l1)
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