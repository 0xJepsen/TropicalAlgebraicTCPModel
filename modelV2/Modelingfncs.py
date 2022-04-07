from pprint import pprint


def delay(src, dst):
    return abs(dst - src)  # for link rate of 1


def sigma():
    return 1


def initialize(number_of_packers, number_of_routers):
    return


def Y_i(init, n, k):
    # if i-1 == -1:
    for j in range(0, n + 1):
        # print("j: ", j)
        for i in range(0, k + 1):
            if i == 0:
                if j == 0:
                    init[j] = [0]
                else:
                    init[j] = [init[j - 1][k] + delay(k, 0)]
            else:
                # print("i: ", i)
                # # print(init[i])
                # print("init[n][i-1]: ", init[j][i-1])
                init[j].append(init[j][i - 1] + delay(i - 1, i) + sigma())
    return init
    # print("n: ", n)
    # if n == -1:
    #     return 0
    # print(y_i_minus_1 + 1)
    # return max((y_i_minus_1 + 1), Y_i(y_i_minus_1, n - 1)) + 1


vector = {}

test_2_1 = [[0, 2, 4, 6], [9, 11, 13, 15], [9, 11, 13, 15]]

result = Y_i(vector, 7, 3)
pprint(result)
