from pprint import pprint
from MatrixMath import Matrix


def delay(src, dst, link_rate, pkt_size):
    number_of_links = abs(dst - src)
    time = pkt_size / link_rate
    return number_of_links * time


def sigma(rate, size):
    return size / rate


def Make_Y(number_of_packets, configuration):
    """ This generates the vectors Y(n) for each packet n consisting of the departure times
        of packet n from router i for 0<=i<=k where k is the number of routers.
        y_o(n) = Y_K(n - v_n-1) + d_(K,0)
        y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)] + sigma_i(n)
        Parameters
        ----------
        number_of_packets : int
            The number of packets you want to generate data for
        configuration: object with properties:
            max_window : int
                The maximum window size the model achieves
            number_of_routers : int
                Number of routers in the model.
        """
    sent = 0
    running_window = 1
    init = {}
    for j in range(0, number_of_packets + 1):  # loop through packets
        for i in range(0, configuration.number_of_routers):  # loop through routers
            if i == 0:  # first router
                if j == 0:  # first packet
                    init[j] = {'departures': {0: 0}, 'V_n': 1}
                    """first packet depart time"""
                    sent += 1
                else:
                    """y_o(n) = Y_K(n - v_n-1) + d_(K,0)"""
                    init[j] = {'departures': {
                        0: max(init[j - init[j - 1]['V_n']]['departures'][configuration.number_of_routers - 1] +
                            delay(configuration.number_of_routers - 1, 0, configuration.link_rate, configuration.packet_to_size[j]),
                               init[j - 1]['departures'][0] + sigma(configuration.switch_rate, configuration.packet_to_size[j]))}}
                    sent += 1
                    init[j]['V_n'] = running_window
            else:
                if j - 1 == -1:
                    # print("Delay: ",  delay(i - 1, i, configuration.link_rate, configuration.packet_to_size[j]))
                    # print("Packet number {} size {}, Sigma {}, and  link rate {}".format(j, configuration.packet_to_size[j], sigma(configuration.switch_rate, configuration.packet_to_size[j]), configuration.link_rate))
                    the_max = max(init[j]['departures'][i - 1] + delay(i - 1, i, configuration.link_rate, configuration.packet_to_size[j]), 0)
                    """Edge case for packet 0"""
                else:
                    the_max = max(init[j]['departures'][i - 1] + delay(i - 1, i, configuration.link_rate, configuration.packet_to_size[j]), init[j - 1]['departures'][i])
                    """y_i(n) = [max(y_i-1(n) + d_(i-1,i), y_i(n-1)]"""
                init[j]['departures'][i] = int(the_max + sigma(configuration.switch_rate, configuration.packet_to_size[j]))
        if running_window == configuration.max_window and sent > 0:
            running_window = 1
            sent = 0
        if sent == running_window + 1:
            running_window += 1
            sent = 0
    return init


def Z_init(packet_number, configuration):
    """ This generates the data vector for a specified packet number.
        The Z(n) data vector can be thought of as a number network traces
        equal to the max window size.
        Z(n) = {Y(n), Y(n-1),..., Y(n - w* +1)}
        Parameters
        ----------
        packet_number : int
            The packet number for which you want the network trace for
        configuration: object with properties:
            max_window : int
                The maximum window size the model achieves
            number_of_routers : int
                Number of routers in the model.
        """

    new = Matrix(dims=(configuration.number_of_routers * configuration.max_window, 1), fill=0)
    trace_components = Make_Y(packet_number, configuration)
    bound = packet_number - configuration.max_window
    count = 0
    flag = True
    for packet in range(packet_number, bound, -1):
        if flag:
            flag = False
        if count < (configuration.number_of_routers * configuration.max_window):
            if packet < 0:
                for _ in range(0, configuration.number_of_routers):
                    new[count, 0] = 0
                    count += 1
            else:
                for dep in (list(trace_components[packet]['departures'].values())):
                    new[count, 0] = dep
                    count += 1
    return new


def M_init(packet_number, configuration):
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
    M = Matrix(dims=(configuration.number_of_routers, configuration.number_of_routers), fill=0)
    for i in range(configuration.number_of_routers):
        for j in range(configuration.number_of_routers):
            if i >= j:
                for _ in range(j, i + 1):
                    M[i, j] += sigma(configuration.switch_rate, configuration.packet_to_size[packet_number])
                for h in range(j, i):
                    M[i, j] += delay(h, h - 1, configuration.link_rate, configuration.packet_to_size[j])
            else:
                M[i, j] = float("-inf")
    return M


def MPrime_init(packet_number, configuration):
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
    Mprime = Matrix(dims=(configuration.number_of_routers, configuration.number_of_routers), fill=0)
    for i in range(configuration.number_of_routers):
        for j in range(configuration.number_of_routers):
            if j == configuration.number_of_routers - 1:
                for k in range(1, i + 1):
                    Mprime[i, j] += delay(k - 1, k, configuration.link_rate, configuration.packet_to_size[j])
                    Mprime[i, j] += sigma(configuration.switch_rate, configuration.packet_to_size[packet_number])
                Mprime[i, j] += delay(configuration.number_of_routers - 1, 0, configuration.link_rate, configuration.packet_to_size[j])  # index from zero on routers
            if j < configuration.number_of_routers - 1:
                Mprime[i, j] = float("-inf")
    return Mprime


def D_init(configuration):
    """ This generates Matrix D given a max window size w* and number of routers in the model K.
        D is a matrix of dimension Kw* with all its indices equal to -inf except those of the form
        D_(K+i, i), i = 1,..., K(w* -1) which are all equal to 0
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        configuration: object with properties:
            max_window : int
                The maximum window size the model achieves
            number_of_routers : int
                Number of routers in the model.
        """
    kw = configuration.max_window * configuration.number_of_routers
    d = Matrix(dims=(kw, kw), fill=float("-inf"))
    for i in range(kw - configuration.number_of_routers):
        d[configuration.number_of_routers + i, i] = 0
    return d


def A_from_components(packet_number, configuration):
    """ This generates Matrix D given a max window size w* and number of routers in the model K.
        D is a matrix of dimension Kw* with all its indices equal to -inf except those of the form
        D_(K+i, i), i = 1,..., K(w* -1) which are all equal to 0
        In the current implementation all sigma's are = 1 and all delays from router to router are 1
        Parameters
        ----------
        packet_number : int
            the packet number you want to compute the network trace of
        configuration: object with properties:
            max_window : int
                The maximum window size the model achieves
            number_of_routers : int
                Number of routers in the model.
        """
    product = M_init(packet_number, configuration)  # initialize to M
    # print("M: \n", product)

    mprime = MPrime_init(packet_number, configuration)
    # print("Mprime: \n", mprime)

    k_epsilon = Matrix(dims=(configuration.number_of_routers, configuration.number_of_routers), fill=float("-inf"))
    # print("KxK Epsilon: \n", k_epsilon)

    D = D_init(configuration)

    Next_block = 0
    put_m = True
    block_for_mprime = configuration.vn[packet_number % 10] - 1
    # print(block_for_mprime)

    if block_for_mprime < 0:
        raise Exception("v_n-1 needs to be greater than -1")
    if block_for_mprime == 0:
        product = product + mprime
        # print("product after plus \n", product)
        put_m = False
    while Next_block != configuration.number_of_routers - 1:
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


def Z_continuous(starting_packet_number, ending_packet_number, configuration):
    z_initial = Z_init(starting_packet_number, configuration)
    current_packet = starting_packet_number
    zeees = {current_packet: z_initial}
    while current_packet < ending_packet_number:
        a_n = A_from_components(current_packet, configuration)
        znext = a_n @ z_initial
        zeees[current_packet + 1] = znext
        z_initial = znext
        current_packet += 1
    return zeees
