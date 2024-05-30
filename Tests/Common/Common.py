from Utils.CsvUtils import read_csv
from NetworkMetricBuilder.NetworkMetricBuilder import NetworkMetricBuilder
from NetworkMetricBuilder.IpConnectionPair import IpConnectionPair


def ProcessCsvAndFindScanners(csv_file_path: str, csv_delimiter: str, source_ip_column_index: int,
                              destination_ip_column_index, internal_subnet_ip: str, threshold_quantile: float):
    data = read_csv(csv_file_path, csv_delimiter)

    data.remove(data[0])

    ip_connection_pairs = list(map(lambda obj: IpConnectionPair.from_string_ip_addresses(
        obj[source_ip_column_index], obj[destination_ip_column_index]), data))

    network_metric_builder = NetworkMetricBuilder(ip_connection_pairs, internal_subnet_ip)

    scanners = network_metric_builder.find_scanners(threshold_quantile)

    for key, value in scanners.items():
        print(f"{key}: {value}")
