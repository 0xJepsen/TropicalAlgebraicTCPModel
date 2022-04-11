from pprint import pprint


def delay(src, dst):
    return abs(dst - src)  # for link rate of 1


def sigma():
    return 1


def Make_Y(init, number_of_packets, number_of_routers, max_window):
    """ This generates the vectors Y(n) for each packet n consisting of the departure times
        of packet n from router i for 0<=i<=k where k is the number of routers.
        This implements equations
        y_o(n) = Y_K(n - v_n-1) + d_(K,0)
        y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)] + sigma_i(n)
        Parameters
        ----------
        init : float
            the time the packet arrives at the output queue.
        number_of_packets : float
            the size of the packet in bytes
        number_of_routers : int
            an identifier for the packet
        max_window: int
            identifiers for source and destination
        """
    sent = 0
    running_window = 1
    for j in range(0, number_of_packets + 1):
        for i in range(0, number_of_routers + 1):
            if i == 0:
                if j == 0:
                    init[j] = {'departures': {0: 0}, 'V_n': 1}
                    """first packet depart time"""
                else:
                    """y_o(n) = Y_K(n - v_n-1) + d_(K,0)"""
                    init[j] = {'departures': {0: init[j - running_window]['departures'][number_of_routers] + delay(number_of_routers, 0)}}
                    sent += 1
                    init[j]['V_n'] = running_window
            else:
                if j - 1 == -1:
                    the_max = max(init[j]['departures'][i - 1] + delay(i - 1, i), 0)
                    """Edge case for packet 0"""
                else:
                    the_max = max(init[j]['departures'][i - 1] + delay(i - 1, i), init[j - 1]['departures'][i])
                    """y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)]"""
                init[j]['departures'][i] = the_max + sigma()
        if running_window == max_window:
            running_window = 1
            sent = 0
        if sent == running_window + 1:
            running_window += 1
            sent = 0
    return init

# def Make_Y(init, number_of_packets, number_of_routers, max_window):
#     """ This generates the vectors Y(n) for each packet n consisting of the departure times
#         of packet n from router i for 0<=i<=k where k is the number of routers.
#         This implements equations
#         y_o(n) = Y_K(n - v_n-1) + d_(K,0)
#         y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)] + sigma_i(n)
#         Parameters
#         ----------
#         init : float
#             the time the packet arrives at the output queue.
#         number_of_packets : float
#             the size of the packet in bytes
#         number_of_routers : int
#             an identifier for the packet
#         max_window: int
#             identifiers for source and destination

vector = {}
#
# test_2_1 = [[0, 2, 4, 6], [9, 11, 13, 15], [9, 11, 13, 15]]
#
result = Make_Y(vector, 14, 3, 4)

# for i in range (0,13):
#     for j in range(0, 13):
#         vector[j][i] = 1
pprint(result)