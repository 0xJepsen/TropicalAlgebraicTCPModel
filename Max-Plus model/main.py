from random import expovariate
from MatrixMath import Matrix
from scipy.stats import poisson
import simpy
from pprint import pprint
from SimComponents import PacketGenerator, PacketSink, SwitchPort

MU = 0.6 # Arrival distributed parameter mu for poisson inter arival time
LINK_BANDWIDTH = 10000
SWITCH_BANDWIDTH = 5000
SWITCH_QSIZE = 2500 # in bytes
LAMBDA = .02 # e^(-0.3)x

def constArrival():  # Constant arrival distribution for generator 1
    return int(poisson.rvs(MU)) # using Poisson interarrival time to model bursty traffic

def distSize():
    return expovariate(LAMBDA) # packet size distribution

def delay(data, src, dst, n):
    try:
        return data[n]['arivals'][dst+1] - data[n]['arivals'][src+1] #time delay between router i and router j
    except e: 
        print("Packet not in data, must have been dropped")

def sigma(data, i, n): # note that the switch rate has to be less then the link rate for this to be positive
    return data[n]['departures'][i+1] - data[n]['arivals'][i+1] # agrigated service time of packet n at router i

def Y(data, n):
    dimension = len(data[n]['departures'].keys())
    M = Matrix(dims =(dimension, 1), fill = 0.0)
    for i in range(1,dimension +1):
        M[i-1,0] = data[n]['departures'][i]
    return M

def Z(data):
    M = []
    for n in data.keys():
        M.append(Y(data, n))
    return M

def makeM(data, n):
    dimension = data[n]['departures'].keys()
    M = Matrix(dims=(len(dimension),len(dimension)), fill=0.0)
    for i in range(len(dimension)):
        for j in range(len(dimension)):
            if i>= j:
                for k in range(j, i+1):
                    M[i,j] += sigma(data, k, n)
                for h in range(j, i):
                    M[i,j] += delay(data, h, h+1, n) #this k+1 might go out of bounds
            if i < j:
                M[i,j] = float('-inf') # < for -inf
    return M

def makeMprime(data, n):
    dimension = data[n]['departures'].keys()
    n_routers = len(dimension) -1
    print(len(dimension))
    Mprime = Matrix(dims=(len(dimension),len(dimension)), fill=0.0)
    for i in range(len(dimension)):
        for j in range(len(dimension)):
            if j == n_routers:
                for k in range(1,i+1):
                    Mprime[i,j] += delay(data, k-1, k, n)
                    Mprime[i,j] += sigma(data, k, n)
                Mprime[i,j] += delay(data, 0, n_routers, n)
            if j < n_routers:
                Mprime[i,j] = float('-inf')
    return Mprime

def make_A(data, n):
    Mprime = makeMprime(data,n)
    M = makeM(data,n)
    return M + Mprime

env = simpy.Environment()
# Create the SimPy environment
# Create the packet generators and sink
pg = PacketGenerator(env, "Generator", constArrival, distSize, LINK_BANDWIDTH)
ps = PacketSink(env)  # debugging enable for simple output
s1 = SwitchPort(1, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
s2 = SwitchPort(2, env, rate=SWITCH_BANDWIDTH, qlimit=SWITCH_QSIZE)
# Wire packet generators and sink together
pg.out = s1
s1.out = s2
s2.out = ps
env.run(until=20)

print("recieved: {}, s1 dropped {}, s2 dropped {}, sent {}".format(ps.packets_rec, s1.packets_drop, s2.packets_drop, pg.packets_sent))

pprint(ps.data)

## test delay
# pprint(delay(ps.data, 1, 2, 1)) # print the delay from s1 to s2 for pkt 1

## test sigma
# pprint(sigma(ps.data, 1, 1)) # print processing time of packet 1 at s1

## test M
# testM = makeM(ps.data, 0)
# print(testM)

# test makeMprime
# testprime = makeMprime(ps.data, 0)
# print(testprime)

# test for Y(n)
y0 = Y(ps.data, 0)
print(y0)

Z = Z(ps.data)
print(Z[0])

A = make_A(ps.data, 0)
print(A)
g = Z[1]
print("Cols: ",g.cols)
print("rows: ",g.rows)
def validation(A_v_n, z_n):
    return A@z_n
#print(len(ps.data.keys()))
new = []
for n in ps.data.keys():
    print("n is: ", n)
    new.append(validation(A, Z[n]))

print(new[1])
print(len(new))
print(len(Z))

