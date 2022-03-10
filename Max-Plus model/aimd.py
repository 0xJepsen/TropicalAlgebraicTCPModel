### Testing AIMD for window modeling
import simpy
import random

MAX_WINDOW_SIZE = 140


def main():
    env = simpy.Environment()
    env.process(AIMD(env))
    env.run(until=300)
    print("Simulation complete")


def AIMD(env):
    WINDOW_SIZE = 0  ## Slow Start
    while True:
        yield env.timeout(WINDOW_SIZE)
        WINDOW_SIZE += 1
        print(
            "Window Size Increase to " + str(WINDOW_SIZE) + " at epoch" + str(env.now)
        )
        loss = random.randint(0, 25)
        if loss or WINDOW_SIZE >= MAX_WINDOW_SIZE:
            WINDOW_SIZE = WINDOW_SIZE / 2
            print("Window Size Decreased to " + str(WINDOW_SIZE))


if __name__ == "__main__":
    main()
