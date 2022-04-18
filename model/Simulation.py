"""
    An Abstraction for simulation configurations to scale the model
"""


class SimulationConfig(object):

    def __init__(self, id: str, max_window, number_routers):

        self.max_window = max_window
        self.number_of_routers = number_routers
        self.id = id
        self.vn = []
        self.switch_rate = 10
        self.link_rate = 10
        self.dist_sise = 10
        self.simtime = 50
        self.switch_que_size = 50

        vn = []
        for i in range(1, self.max_window + 1):
            for _ in range(0, i + 1):
                vn.append(i)
                if i == self.max_window:
                    break
        self.vn = vn
