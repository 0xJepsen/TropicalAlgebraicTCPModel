"""
    An Abstraction for simulation configurations to scale the model
"""


class SimulationConfig(object):

    def __init__(self, id: str, max_window, number_routers, number_of_connections):

        self.max_window = max_window
        self.number_of_routers = number_routers
        self.id = id
        self.vn = []
        self.switch_rate = 10
        self.link_rate = 10
        self.sim_time = 150
        self.switch_que_size = 10
        self.tcp_connections = number_of_connections

        vn = []
        for i in range(1, self.max_window + 1):
            for _ in range(0, i + 1):
                vn.append(i)
                if i == self.max_window:
                    break
        self.vn = vn


class ModelConfig(object):

    def __init__(self, conf, data):

        self.max_window = conf.max_window
        self.number_of_routers = conf.number_of_routers
        self.packet_to_size = data['Size']
        self.vn = []
        self.switch_rate = conf.switch_rate
        self.link_rate = conf.link_rate
        self.switch_que_size = conf.switch_que_size

        vn = []
        for i in range(1, self.max_window + 1):
            for _ in range(0, i + 1):
                vn.append(i)
                if i == self.max_window:
                    break
        self.vn = vn
