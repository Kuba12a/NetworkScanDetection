from ipaddress import IPv4Network, IPv4Address

from typing import Dict, List

from NetworkMetricBuilder.ExternalIpMetrics import ExternalIpMetrics
from NetworkMetricBuilder.IpConnectionPair import IpConnectionPair
import math


class NetworkMetricBuilder:
    """
    The NetworkMetricBuilder class is used to build network metrics based on the provided dictionary of unique network
    connections between ip addresses.

    Attributes:
        ConnectionPairs (List[IpConnectionPair]): A list containing pairs of IP addresses.
        that exchanged network packets.

    """

    def __init__(self, connection_pairs: List[IpConnectionPair], internal_subnet: str):
        """
        Initializes an instance of the NetworkMetricBuilder class.

        Parameters:
            connection_pairs (List[IpConnectionPair]): A list containing unique pairs of IP addresses.
            internal_subnet (str): Private subnet used to filter out connection pairs with destination ip address outside
            this subnet.
        """

        filtered_connection_pairs = self.__filter_by_subnet(connection_pairs, IPv4Network(internal_subnet))
        self.ConnectionPairs = self.__filter_unique_connection_pairs(filtered_connection_pairs)

        self.RHash: Dict[IPv4Address, float] = {}
        self.LHash: Dict[IPv4Address, ExternalIpMetrics] = {}

        self.__calculate_w_score()
        self.__calculate_s_and_c_score()

        self.sorted_s_metrics = []
        self.sorted_c_metrics = []
        self.__build_sorted_metric_arrays()

    def get_thresholds(self, threshold_quantile: float) -> {int, int}:
        """Gets threshold from sorted S and C arrays based on given threshold_quantile.

        Parameters:
            threshold_quantile (float): Threshold quantile should be in [0,1].

        Returns:
            Pair of calculated S and C thresholds
        """
        s_threshold_index = math.ceil(len(self.sorted_s_metrics) * threshold_quantile)
        if s_threshold_index > len(self.sorted_s_metrics) - 1:
            s_threshold = self.sorted_s_metrics[len(self.sorted_s_metrics) - 1] + 1
        else:
            s_threshold = self.sorted_s_metrics[s_threshold_index]

        c_threshold_index = math.ceil(len(self.sorted_c_metrics) * threshold_quantile)
        if c_threshold_index > len(self.sorted_c_metrics) - 1:
            c_threshold = self.sorted_c_metrics[len(self.sorted_c_metrics) - 1] + 1
        else:
            c_threshold = self.sorted_c_metrics[c_threshold_index]

        return s_threshold, c_threshold

    def find_scanners(self, threshold_quantile: float) -> Dict[IPv4Address, ExternalIpMetrics]:
        """Finds scanners ip with their S and C score based on calculated thresholds.
         Thresholds are calculated based on given threshold_quantile.

        Parameters:
            threshold_quantile (float): Threshold quantile should be in [0,1].

        Returns:
            Dict[IPv4Address, ExternalIpMetrics]: Scanners found by the algorithm with their C and S score.
        """
        s_threshold, c_threshold = self.get_thresholds(threshold_quantile)

        filtered_scanners_metrics = {key: value for key, value in self.LHash.items()
                                     if value.S >= s_threshold and value.C >= c_threshold}
        return filtered_scanners_metrics

    def __calculate_w_score(self):
        """
        Calculates W score.
        """
        for ip_connection_pair in self.ConnectionPairs:
            destination_ip = ip_connection_pair.destination_ip

            if destination_ip in self.RHash:
                self.RHash[destination_ip] += 1

            else:
                self.RHash[destination_ip] = 1

        for destination_ip in self.RHash:
            self.RHash[destination_ip] = 1 / self.RHash[destination_ip]

    def __calculate_s_and_c_score(self):
        """
        Calculates S and C score.
        """
        for ip_connection_pair in self.ConnectionPairs:
            source_ip = ip_connection_pair.source_ip

            s_temp = self.RHash[ip_connection_pair.destination_ip]

            if source_ip in self.LHash:
                external_ip_metrics = self.LHash[source_ip]
                external_ip_metrics.C += 1

                if s_temp > external_ip_metrics.S:
                    external_ip_metrics.S = s_temp

            else:
                self.LHash[source_ip] = ExternalIpMetrics(s_temp, 1)

    def __build_sorted_metric_arrays(self):
        """
        Build sorted arrays of S and C scores
        """
        s_metrics = []
        c_metrics = []
        for key, metric in self.LHash.items():
            s_metrics.append(metric.S)
            c_metrics.append(metric.C)

        s_metrics.sort()
        c_metrics.sort()

        self.sorted_s_metrics = s_metrics
        self.sorted_c_metrics = c_metrics

    @staticmethod
    def __filter_by_subnet(connection_pairs: List[IpConnectionPair], subnet: IPv4Network)\
            -> List[IpConnectionPair]:
        """Filters the ip addresses dictionary to include only keys that belong to the given subnet.

        Parameters:
            subnet (str): The subnet in CIDR notation (e.g., '192.168.1.0/24').
            connection_pairs (List[IpConnectionPair]): List of ip address connection pairs

        Returns:
            List[IpConnectionPair]: A filtered list of connection pairs.
        """
        filtered_pairs = []

        for pair in connection_pairs:
            if pair.destination_ip in subnet:
                filtered_pairs.append(pair)

        return filtered_pairs

    @staticmethod
    def __filter_unique_connection_pairs(connection_pairs: List[IpConnectionPair]) -> List[IpConnectionPair]:
        """Filters the ip addresses connections list to include only unique pairs.

        Parameters:
            connection_pairs (List[IpConnectionPair]): List of ip address connection pairs

        Returns:
            List[IpConnectionPair]: A filtered list of connection pairs.
        """
        unique_pairs_set = set()
        unique_connection_pairs = []

        for pair in connection_pairs:
            pair_tuple = (pair.source_ip, pair.destination_ip)

            if pair_tuple not in unique_pairs_set:
                unique_pairs_set.add(pair_tuple)
                unique_connection_pairs.append(pair)

        return unique_connection_pairs
