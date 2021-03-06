from Modelingfncs import Make_Y, Z_continuous
import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint


def validate_Y(df_simulated, ps, conf):
    """Logic for error extraction of Y_n"""
    df_simulated_departures = df_simulated.loc[:, ["departures"]]
    print("---------- Simulated Departure Data ----------")
    pprint(df_simulated_departures)
    print("Model Config Link Rate: ", conf.link_rate)
    generated_departures = Make_Y(ps.packets_rec - 1, conf)
    df_generated = pd.DataFrame.from_dict(generated_departures, orient='index')
    print("---------- Generated Departure Data ----------")
    pprint(df_generated)
    errors = {}
    for i in range(0, ps.packets_rec):
        errors[i] = {}
        for j in range(0, 4):
            errors[i]['Router {}'.format(j)] = abs(
                df_generated.values[i][0][j] - df_simulated_departures.values[i][0][j])

    df_errors = pd.DataFrame.from_dict(errors, orient='index')
    df_errors["sum"] = df_errors.sum(axis=1)

    print("---------- Error In Departure Times ----------")
    print(df_errors)
    ax = df_errors.plot()
    ax.set_ylabel('Quantity of Error')
    ax.set_xlabel('Packet Number')
    plt.title("Error Between Y(n) and Simulated Traffic")
    plt.show()


def validate_Z(df_simulated, ps, conf, flag=False):
    pprint(df_simulated)
    if flag:
        generated_departures = Make_Y(ps.packets_rec - 1, conf)
        data = pd.DataFrame.from_dict(generated_departures, orient='index')
    else:
        print("---------- Simulated Departure Data ----------")
        data = df_simulated.loc[:, ["departures", "V_n"]]

    pprint(data)
    current_packet = 0
    errors_by_z = {}

    zeee = Z_continuous(current_packet, ps.packets_rec - 1, conf)
    for m in zeee.keys():
        z = zeee[m].transpose()
        current_index_packet = m
        errors = {current_index_packet: {}}
        breakpoint = 0
        total_pkts = 0
        for j in range(0, z.cols):
            if current_index_packet < 0:
                errors[current_index_packet]['Router {}'.format(j % conf.number_of_routers)] = 0
                errors[current_index_packet]['packet'] = current_index_packet
            else:
                errors[current_index_packet]['Router {}'.format(j % conf.number_of_routers)] = \
                    abs((z[0, j]) - data["departures"][current_index_packet][j % conf.number_of_routers])
                breakpoint += 1
                errors[current_index_packet]['packet'] = current_index_packet
            if j % conf.number_of_routers == conf.number_of_routers - 1:
                current_index_packet -= 1
                total_pkts += 1
                if total_pkts < conf.number_of_routers:
                    errors[current_index_packet] = {}

            errors_by_z[m] = errors
    df = pd.DataFrame()
    for key in errors_by_z.keys():
        df_errors = pd.DataFrame.from_dict(errors_by_z[key], orient='index')
        df_errors["sum"] = df_errors[["Router 0", "Router 1", "Router 2", "Router 3"]].sum(axis=1)
        df = pd.concat([df, df_errors]).drop_duplicates(subset=['packet'])

    print("---------- Error In Departure Times ----------")
    df = df[df.packet >= 0]
    new = df.drop(columns=["packet"], axis=1)
    pprint(new)

    ax = new.plot(use_index=True)
    ax.set_ylabel('Quantity of Error')
    ax.set_xlabel('Packet Number')
    plt.title("Error Between Z(n) and Simulated Traffic")
    plt.show()
