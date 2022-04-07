from pprint import pprint


def delay(src, dst):
    return abs(dst - src)  # for link rate of 1


def sigma():
    return 1


def initialize(number_of_packers, number_of_routers):
    return


def Y_i(init, number_of_packets, number_of_routers, max_window):
    sent = 0
    running_window = 1
    for j in range(0, number_of_packets + 1):
        print("Top j: ", j)
        for i in range(0, number_of_routers + 1):
            print("Top i: ", i)
            if i == 0:
                if j == 0:
                    init[j] = [0]

                else:
                    print("running Window: ", running_window)
                    print("j: ", j)
                    print("init[j-running window][number_of_routers]: ", init[j - running_window][number_of_routers])
                    init[j] = [init[j - running_window][number_of_routers] + delay(number_of_routers, 0)]
                    print("Sent: ", sent)
                    sent +=1
                    print("Sent after increment: ", sent)
            else:
                # if init[j][0] == init[j-1][0]:
                #     init[j].append(init[j][i - 1] + delay(i - 1, i) + sigma())
                print("i: ", i)
                print("j: ", j)
                print("Time left last router: ", init[j][i - 1])
                print("term one: ", init[j][i - 1] + delay(i - 1, i))
                if j-1 == -1:
                    the_max = max(init[j][i - 1] + delay(i - 1, i), 0)
                else: the_max = max(init[j][i - 1] + delay(i - 1, i), init[j-1][i])
                init[j].append(the_max + sigma())
            print("Sent outside: ", sent)
            if running_window == max_window:
                running_window = 0
            if sent == running_window +1:
                running_window +=1
                sent = 0
    return init


vector = {}

test_2_1 = [[0, 2, 4, 6], [9, 11, 13, 15], [9, 11, 13, 15]]

result = Y_i(vector, 7, 3, 4)
pprint(result)
