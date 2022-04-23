from Topologies import linear, simple_branch
from Validation import validate_Y, validate_Z


def main():
    # df1, ps1, conf = linear()
    (df1, df2), (ps1, ps2), conf = simple_branch()
    validate_Z(df2, ps2, conf, flag=False)

    # validate_Y(df1, ps1, conf)

    # df_simulated, ps = simulate(config)
    # pprint(df_simulated)


if __name__ == '__main__':
    main()
