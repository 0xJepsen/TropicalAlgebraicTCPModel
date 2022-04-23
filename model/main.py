from Topologies import linear, simple_branch
from Validation import validate_Y, validate_Z


def main():
    df0, ps0, model_conf = linear()
    (df1, df2), (ps1, ps2), (conf1, conf2) = simple_branch()

    print(df0)

    validate_Z(df0, ps0, model_conf)
    # validate_Y(df0, ps0, conf0)


if __name__ == '__main__':
    main()
