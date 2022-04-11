from pprint import pprint
from MatrixMath import Matrix


def delay(src, dst):
    return abs(dst - src)  # for link rate of 1


def sigma():
    return 1


def Make_Y(number_of_packets, number_of_routers, max_window):
    """ This generates the vectors Y(n) for each packet n consisting of the departure times
        of packet n from router i for 0<=i<=k where k is the number of routers.
        y_o(n) = Y_K(n - v_n-1) + d_(K,0)
        y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)] + sigma_i(n)
        Parameters
        ----------
        number_of_packets : int
            The number of packets you want to generate data for
        number_of_routers : int
            The number of routers in the model
        max_window: int
            The maximum window size in the model
        """
    sent = 0
    running_window = 1
    init = {}
    for j in range(0, number_of_packets + 1):
        for i in range(0, number_of_routers + 1):
            if i == 0:
                if j == 0:
                    init[j] = {'departures': {0: 0}, 'V_n': 1}
                    """first packet depart time"""
                else:
                    """y_o(n) = Y_K(n - v_n-1) + d_(K,0)"""
                    init[j] = {'departures': {
                        0: init[j - running_window]['departures'][number_of_routers] + delay(number_of_routers, 0)}}
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


def Z_init(packet_number, max_window, number_of_routers):
    """ This generates the data vector for a specified packet number.
        The Z(n) data vector can be thought of as a number network traces
        equal to the max window size.
        Z(n) = {Y(n), Y(n-1),..., Y(n - w* +1)}
        Parameters
        ----------
        packet_number : int
            The packet number for which you want the network trace for
        max_window : int
            The maximum window size the model achieves
        number_of_routers : int
            Number of routers in the model.
        """
    z = []
    trace_components = Make_Y(packet_number, number_of_routers, max_window)
    bound = packet_number - max_window
    print("bound: ", bound)
    for i in range(packet_number, bound, -1):
        pprint(i)
        if i < 0:
            z.append([0, 0, 0, 0])
        else:
            z.append(list(trace_components[i]['departures'].values()))
    return z


def M_init(packet_number, number_of_routers):
    """ This generates Matrix M for a given packet number and routers in the model
        M_i,j = Sum (from k = j to i of sigma_k(n)) + sum from k=j to i-1 of d_(k,k-1) if i>= j
        and M_i,j = -inf if i<j.
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        packet_number : int
            The packet number for which you want the network trace for
        number_of_routers : int
            Number of routers in the model.
        """
    M = Matrix(dims=(number_of_routers, number_of_routers), fill=0)
    for i in range(number_of_routers):
        for j in range(number_of_routers):
            if i >= j:
                for _ in range(j, i + 1):
                    M[i, j] += sigma()
                for h in range(j, i):
                    M[i, j] += delay(h, h - 1)
            else:
                M[i, j] = float("-inf")
    return M


Z_test = Z_init(0, 4, 3)
pprint(Z_test)

M_test = M_init(50, 4)
print(M_test)
