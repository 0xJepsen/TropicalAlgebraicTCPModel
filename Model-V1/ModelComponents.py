from random import expovariate
from MatrixMath import Matrix
from scipy.stats import poisson


def constArrival(MU):  # Constant arrival distribution for generator 1
    return int(
        poisson.rvs(MU)
    )  # using Poisson interarrival time to model bursty traffic


def distSize(LAMBDA):
    return expovariate(LAMBDA)  # packet size distribution


def delay(data, src, dst, n):
    try:
        return (
            data[n]["arivals"][dst + 1] - data[n]["arivals"][src + 1]
        )  # time delay between router i and router j
    except e:
        print("Packet not in data, must have been dropped")


def sigma(
    data, i, n
):  # note that the switch rate has to be less then the link rate for this to be positive
    return (
        data[n]["departures"][i + 1] - data[n]["arivals"][i + 1]
    )  # agrigated service time of packet n at router i


def Y(data, n):
    dimension = len(data[n]["departures"].keys())
    M = Matrix(dims=(dimension, 1), fill=0.0)
    for i in range(1, dimension + 1):
        M[i - 1, 0] = data[n]["departures"][i]
    return M


def Z(data):
    M = []
    for n in data.keys():
        M.append(Y(data, n))
    return M


def makeM(data, n):
    dimension = data[n]["departures"].keys()
    M = Matrix(dims=(len(dimension), len(dimension)), fill=0.0)
    for i in range(len(dimension)):
        for j in range(len(dimension)):
            if i >= j:
                for k in range(j, i + 1):
                    M[i, j] += sigma(data, k, n)
                for h in range(j, i):
                    M[i, j] += delay(
                        data, h, h + 1, n
                    )  # this k+1 might go out of bounds
            if i < j:
                M[i, j] = float("-inf")  # < for -inf
    return M


def makeMprime(data, n):
    dimension = data[n]["departures"].keys()
    n_routers = len(dimension) - 1
    print(len(dimension))
    Mprime = Matrix(dims=(len(dimension), len(dimension)), fill=0.0)
    for i in range(len(dimension)):
        for j in range(len(dimension)):
            if j == n_routers:
                for k in range(1, i + 1):
                    Mprime[i, j] += delay(data, k - 1, k, n)
                    Mprime[i, j] += sigma(data, k, n)
                Mprime[i, j] += delay(data, 0, n_routers, n)
            if j < n_routers:
                Mprime[i, j] = float("-inf")
    return Mprime


def make_A(data, n):
    Mprime = makeMprime(data, n)
    M = makeM(data, n)
    return M + Mprime
