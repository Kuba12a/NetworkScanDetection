import sys
import os
from Tests.Common import Common

UsageInfo = "Usage: python SampleDataTests.py <quantile[0,1]>"


def run(threshold_quantile):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "data.csv")
    Common.ProcessCsvAndFindScanners(file_path, ';', 1, 2, "192.168.1.0/24", threshold_quantile)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(UsageInfo)
        sys.exit(1)

    try:
        quantile = float(sys.argv[1])
    except ValueError:
        print(UsageInfo)
        sys.exit(0)

    run(quantile)

