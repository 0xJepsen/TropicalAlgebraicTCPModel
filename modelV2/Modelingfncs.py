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
    # number_of_routers = number_of_routers - 1
    sent = 0
    running_window = 1
    init = {}
    for j in range(0, number_of_packets + 1):
        # loop through packets
        print("Packet: ", j)
        for i in range(0, number_of_routers):
            # loop through routers
            if i == 0:
                # first router
                if j == 0:
                    # first packet
                    init[j] = {'departures': {0: 0}, 'V_n': 1}
                    """first packet depart time"""
                    sent += 1
                else:
                    """y_o(n) = Y_K(n - v_n-1) + d_(K,0)"""
                    init[j] = {'departures': {
                        0: init[j - init[j-1]['V_n']]['departures'][number_of_routers - 1] + delay(number_of_routers - 1,
                                                                                                 0)}}
                    # print("V_N -1 =", init[j-1]['V_n'])
                    # print("Running Window", running_window)
                    # # init[j - init[j-1]['V_n']]
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
        if running_window == max_window and sent >0:
            running_window = 1
            sent = 0
        if sent == running_window + 1:
            running_window += 1
            sent = 0
    return init


def Z_init(packet_number, number_of_routers, max_window):
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

    new = Matrix(dims=(number_of_routers * max_window, 1), fill=0)
    trace_components = Make_Y(packet_number, number_of_routers, max_window)
    bound = packet_number - max_window
    count = 0
    # print("Dims", number_of_routers*max_window)
    flag = True
    current_v_n = "test"
    for packet in range(packet_number, bound, -1):
        if flag:
            current_v_n = trace_components[packet]['V_n']
            flag = False
        if count < (number_of_routers * max_window):
            # print("count", count)
            if packet < 0:
                for _ in range(0, number_of_routers):
                    new[count, 0] = 0
                    count += 1
            else:
                for dep in (list(trace_components[packet]['departures'].values())):
                    new[count, 0] = dep
                    count += 1
    return new, current_v_n


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


def MPrime_init(packet_number, number_of_routers):
    """ This generates Matrix M' for a given packet number and routers in the model
        M_i,j = Sum (from k = 1 to i of sigma_k(n) + d(k-1,1)) + d(K,0) if j=K
        and M_i,j = -inf if j<K.
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        packet_number : int
            The packet number for which you want the network trace for
        number_of_routers : int
            Number of routers in the model.
        """
    Mprime = Matrix(dims=(number_of_routers, number_of_routers), fill=0)
    for i in range(number_of_routers):
        for j in range(number_of_routers):
            if j == number_of_routers - 1:
                for k in range(1, i + 1):
                    Mprime[i, j] += delay(k - 1, k)
                    Mprime[i, j] += sigma()
                Mprime[i, j] += delay(number_of_routers - 1, 0)  # index from zero on routers
            if j < number_of_routers - 1:
                Mprime[i, j] = float("-inf")
    return Mprime


def D_init(number_of_routers, max_window):
    """ This generates Matrix D given a max window size w* and number of routers in the model K.
        D is a matrix of dimension Kw* with all its indices equal to -inf except those of the form
        D_(K+i, i), i = 1,..., K(w* -1) which are all equal to 0
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        max_window : int
            The maximum window size the model achieves
        number_of_routers : int
            Number of routers in the model.
        """
    kw = max_window * number_of_routers
    d = Matrix(dims=(kw, kw), fill=float("-inf"))
    for i in range(kw - number_of_routers):
        d[number_of_routers + i, i] = 0
    return d


def A_from_components(packet_number, number_of_routers, max_window, packet_v_n):
    """ This generates Matrix D given a max window size w* and number of routers in the model K.
        D is a matrix of dimension Kw* with all its indices equal to -inf except those of the form
        D_(K+i, i), i = 1,..., K(w* -1) which are all equal to 0
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        packet_number : int
            the packet number you want to compute the network trace of
        max_window : int
            The maximum window size the model achieves
        number_of_routers : int
            Number of routers in the model.
        """
    product = M_init(packet_number, number_of_routers)  # initialize to M
    # print("M: \n", product)

    mprime = MPrime_init(packet_number, number_of_routers)
    # print("Mprime: \n", mprime)

    k_epsilon = Matrix(dims=(number_of_routers, number_of_routers), fill=float("-inf"))
    # print("KxK Epsilon: \n", k_epsilon)

    D = D_init(number_of_routers, max_window)

    Next_block = 0
    put_m = True
    block_for_mprime = packet_v_n - 1

    if block_for_mprime < 0:
        raise Exception("v_n-1 needs to be greater than -1")
    if block_for_mprime == 0:
        product = product + mprime
        # print("product after plus \n", product)
        put_m = False
    while Next_block != num_routers - 1:
        if put_m and block_for_mprime - 1 == Next_block:
            # print("product \n:", product)
            product = product.concatenate_h(mprime)
            Next_block += 1
        else:
            product = product.concatenate_h(k_epsilon)
            Next_block += 1
    product = product.square_epsilon()
    final = D + product
    return final


def Z_gen(packet_number, number_of_routers, max_window):
    z_initial, current_v_n = Z_init(packet_number, number_of_routers, max_window)
    a_n = A_from_components(packet_number, number_of_routers, max_window, current_v_n)
    z_next = a_n @ z_initial
    return z_next


pkt = 9

v_n = 1
m_window = 4
num_routers = 4
#
AVBADY = A_from_components(pkt, num_routers, m_window, v_n)
print(AVBADY)
#

Z_test = Z_gen(pkt, num_routers, m_window)
result = Z_test.transpose()
print(result)

# y = Make_Y(pkt+1, m_window, m_window)
# pprint(y)

# Z_test, v_n = Z_init(pkt, num_routers, m_window)
# print(Z_test)
# print(v_n)
#


# M_test = M_init(50, 4)
# print(M_test)
#
# Mprime_test = MPrime_init(0, 4)
# print(Mprime_test)
#
# D_test = D_init(4, 4)
# print(D_test)
