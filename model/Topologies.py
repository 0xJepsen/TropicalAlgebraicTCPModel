from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
import simpy
import pandas as pd
from random import expovariate
from Config import SimulationConfig, ModelConfig


def const10():
    while True:
        yield 10


def const20():
    while True:
        yield 20


def alternating_gen():
    for i in range(0, 100000):
        if i % 2 == 0:
            yield 3 / 12
        if i % 2 == 1:
            yield 8 / 12


def expSize():
    while True:
        yield round(expovariate(0.06), 2)


def simple_branch(packet_size_dist=None):
    sim_conf = SimulationConfig("sim1", 4, 4, 2)
    env = simpy.Environment()  # Create the SimPy environment

    if packet_size_dist is None:
        pg1 = PacketGenerator(
            env, "Generator", const10(), sim_conf.switch_rate, sim_conf.max_window, flow_id=0
        )
        pg2 = PacketGenerator(
            env, "Generator", const10(), sim_conf.switch_rate, sim_conf.max_window, flow_id=1
        )
    if packet_size_dist == "alpha=2beta":
        pg1 = PacketGenerator(
            env, "Generator", const10(), sim_conf.switch_rate, sim_conf.max_window, flow_id=0
        )
        pg2 = PacketGenerator(
            env, "Generator", const20(), sim_conf.switch_rate, sim_conf.max_window, flow_id=1
        )
    if packet_size_dist == "rational_alt":
        pg1 = PacketGenerator(
            env, "Generator", const10(), sim_conf.switch_rate, sim_conf.max_window, flow_id=0
        )
        pg2 = PacketGenerator(
            env, "Generator", alternating_gen(), sim_conf.switch_rate, sim_conf.max_window, flow_id=1
        )
    if packet_size_dist == "rand":
        pg1 = PacketGenerator(
            env, "Generator", expSize(), sim_conf.switch_rate, sim_conf.max_window, flow_id=0
        )
        pg2 = PacketGenerator(
            env, "Generator", expSize(), sim_conf.switch_rate, sim_conf.max_window, flow_id=1
        )
    # flow ID 0 goes to packet sink 3, and flow ID 1 goings to packet sink 4

    ps1 = PacketSink(3, env, rate=sim_conf.switch_rate, qlimit=sim_conf.switch_que_size)
    ps2 = PacketSink(4, env, rate=sim_conf.switch_rate, qlimit=sim_conf.switch_que_size)

    s1 = SwitchPort(1, env, sim_conf.switch_rate, [ps1.id, ps2.id], qlimit=sim_conf.switch_que_size)
    s2 = SwitchPort(2, env, sim_conf.switch_rate, [ps1.id, ps2.id], qlimit=sim_conf.switch_que_size)

    l1 = Link(env, sim_conf.link_rate)
    l2 = Link(env, sim_conf.link_rate)
    l3 = Link(env, sim_conf.link_rate)
    l4 = Link(env, sim_conf.link_rate)
    l5 = Link(env, sim_conf.link_rate)

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

    env.run(until=sim_conf.sim_time)

    print(
        "received by PS1: {}, received by PS2: {}s1 dropped {}, s2 dropped {}, sent by PG1 {}, sent by PG2 {}".format(
            ps1.packets_rec, ps2.packets_rec, s1.packets_drop, s2.packets_drop, pg1.packets_sent, pg2.packets_sent
        )
    )
    df_1 = pd.DataFrame.from_dict(ps1.data)
    df_2 = pd.DataFrame.from_dict(ps2.data)
    df1_simulated = df_1.transpose()
    df2_simulated = df_2.transpose()
    dict1 = df1_simulated.to_dict()
    dict2 = df2_simulated.to_dict()
    model_config1 = ModelConfig(sim_conf, dict1)
    model_config2 = ModelConfig(sim_conf, dict2)

    return (df1_simulated, df2_simulated), (ps1, ps2), (model_config1, model_config2)


def linear():
    sim_conf = SimulationConfig("sim1", 4, 4, 1)
    env = simpy.Environment()  # Create the SimPy environment
    pg = PacketGenerator(
        env, "Generator", const10(), sim_conf.switch_rate, sim_conf.max_window
    )

    ps = PacketSink(3, env, rate=sim_conf.switch_rate, qlimit=sim_conf.switch_que_size)
    s1 = SwitchPort(1, env, sim_conf.switch_rate, ps.id, qlimit=sim_conf.switch_que_size)
    s2 = SwitchPort(2, env, sim_conf.switch_rate, ps.id, qlimit=sim_conf.switch_que_size)

    l1 = Link(env, sim_conf.link_rate)
    l2 = Link(env, sim_conf.link_rate)
    l3 = Link(env, sim_conf.link_rate)

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
    env.run(until=sim_conf.sim_time)

    print(
        "received: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
            ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
        )
    )
    df = pd.DataFrame.from_dict(ps.data)
    df_simulated = df.transpose()
    dict = df.to_dict('index')
    model_config = ModelConfig(sim_conf, dict)

    # print("Model Config Link Rate:", model_config.link_rate)
    return df_simulated, ps, model_config
