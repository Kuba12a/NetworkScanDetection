from NetworkMetricBuilder.NetworkMetricBuilder import NetworkMetricBuilder
from NetworkMetricBuilder.IpConnectionPair import IpConnectionPair
from Utils.CsvUtils import read_csv
import sys
import os


def run(threshold_quantile):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'data.csv')
    data = read_csv(file_path, ',')

    data.remove(data[0])

    ip_connection_pairs = list(map(lambda obj: IpConnectionPair.from_string_ip_addresses(obj[1], obj[3]), data))

    network_metric_builder = NetworkMetricBuilder(ip_connection_pairs, '192.168.10.0/24')

    scanners = network_metric_builder.find_scanners(threshold_quantile)

    for key, value in scanners.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python UnbDataTests.py <quantile[0,1]>")
        sys.exit(1)

    try:
        quantile = float(sys.argv[1])
    except ValueError:
        print("Usage: python UnbDataTests.py <quantile[0,1]>")
        sys.exit(0)

    run(quantile)

