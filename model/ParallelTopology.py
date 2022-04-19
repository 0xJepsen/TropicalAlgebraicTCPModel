from SimComponents import PacketGenerator, PacketSink, SwitchPort, Link
from Modelingfncs import Make_Y, delay, A_from_components, Z_continuous, Z_init
import simpy
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt
from Simulation import SimulationConfig

config = SimulationConfig("sim1", 4, 6)
distSize = 10


def simple_branch(conf):
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

    env.run(until=conf.sim_time)

    print(
        "received: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
            ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
        )
    )
    df = pd.DataFrame.from_dict(ps.data)
    df_simulated = df.transpose()
    return df_simulated, ps


df, ps = simple_branch(config)
pprint(df)
# def Parallel(conf):
#     env = simpy.Environment()  # Create the SimPy environment
#     pg1 = PacketGenerator(
#         env, "PG1", distSize, LINK_BANDWIDTH, conf.max_window
#     )
#     pg2 = PacketGenerator(
#         env, "PG2", distSize, LINK_BANDWIDTH, conf.max_window
#     )
#     s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
#     s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
#     s3 = SwitchPort(3, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
#     ps1 = PacketSink('PS1', env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
#     ps2 = PacketSink('PS2', env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
#
#     l1 = Link(0, env, LINK_BANDWIDTH)
#     l2 = Link(1, env, LINK_BANDWIDTH)
#     l3 = Link(2, env, LINK_BANDWIDTH)
#     l4 = Link(3, env, LINK_BANDWIDTH)
#     l5 = Link(4, env, LINK_BANDWIDTH)
#     l6 = Link(5, env, LINK_BANDWIDTH)
#
#     # Wire packet generators and sink together
#
#     # Set Flow
#     pg1.dst = ps1.id
#     pg2.dst = ps2.id
#
#     # >0
#     pg1.out = l1
#     l1.front = s1
#     pg2.out = l2
#     l2.front = s1
#
#     # 0-0-0
#     s1.front = l3
#     l3.front = s2
#     s2.front = l4
#     l4.front = s3
#
#     # 0<
#     s3.front = l5
#     l5.front = ps1
#     s3.front = l6
#     l6.front = ps2
#
#     # wire back for acknowledgments
#     ps1.out = l3
#     l3.back = s2
#     s2.back = l2
#     l2.back = s1
#     s1.back = l1
#     l1.back = pg
#     env.run(until=SIM_TIME)
#
#     print(
#         "received: {}, s1 dropped {}, s2 dropped {}, sent {}".format(
#             ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent
#         )
#     )
#     df = pd.DataFrame.from_dict(ps.data)
#     df_simulated = df.transpose()
#     return df_simulated, ps
