### Testing AIMD for window modeling
import simpy

MAX_WINDOW_SIZE = 12


def main():
    env = simpy.Environment()
    env.process(AIMD(env))
    env.run(until=300)
    print("Simulation complete")


def AIMD(env):
    WINDOW_SIZE = 1  ## Slow Start
    while True:
        yield env.timeout(WINDOW_SIZE)
        WINDOW_SIZE += 1
        print("Window Size Increase to " + str(WINDOW_SIZE) + " at " + str(env.now))
        if WINDOW_SIZE >= MAX_WINDOW_SIZE:
            WINDOW_SIZE = WINDOW_SIZE / 2
            print("Window Size Decreased to " + str(WINDOW_SIZE))


if __name__ == "__main__":
    main()
