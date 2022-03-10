### Testing AIMD for window modeling
from tkinter import N, ROUND
import simpy
import random

MAX_WINDOW_SIZE = 140
ROUNDS = 20
NUM_FAILED = 0
TOTAL_SENT = 0


def main():

    average_loss = 0
    for _ in range(1, ROUNDS):
        global NUM_FAILED
        global TOTAL_SENT
        NUM_FAILED = 0
        TOTAL_SENT = 0
        env = simpy.Environment()
        env.process(AIMD(env))
        env.run(until=300)
        round_loss = NUM_FAILED / TOTAL_SENT
        average_loss += round_loss
        print("{} percent of packets experienced loss".format(round_loss))
    average_loss = round_loss / ROUNDS
    print("average loss of {} rounds was {}".format(ROUNDS, average_loss))


def AIMD(env):
    WINDOW_SIZE = 0  ## Slow Start

    while True:
        yield env.timeout(1)
        WINDOW_SIZE += 1
        global TOTAL_SENT
        TOTAL_SENT += 1
        print(
            "Window Size Increase to " + str(WINDOW_SIZE) + " at epoch " + str(env.now)
        )
        loss = random.randint(0, 100)
        if (loss == 1) or (WINDOW_SIZE >= MAX_WINDOW_SIZE):
            global NUM_FAILED
            NUM_FAILED += 1
            WINDOW_SIZE = int(WINDOW_SIZE / 2)
            print("Window Size Decreased to " + str(WINDOW_SIZE))


if __name__ == "__main__":
    main()
