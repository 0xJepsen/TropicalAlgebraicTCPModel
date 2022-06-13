from Topologies import linear, simple_branch
from Validation import validate_Y, validate_Z


def main():
    df1, ps1, conf1 = linear()

    # (df1, df2), (ps1, ps2), (conf1, conf2) = simple_branch("rand")
    # (df1, df2), (ps1, ps2), (conf1, conf2) = simple_branch("rational_alt")
    # (df1, df2), (ps1, ps2), (conf1, conf2) = simple_branch("alpha=2beta")
    # (df1, df2), (ps1, ps2), (conf1, conf2) = simple_branch()

    validate_Z(df1, ps1, conf1)
    # validate_Z(df2, ps2, conf2)

    validate_Y(df1, ps1, conf1)
    # validate_Y(df2, ps2, conf2)


if __name__ == "__main__":
    main()
