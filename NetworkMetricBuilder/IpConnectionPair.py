from dataclasses import dataclass
from ipaddress import IPv4Address


@dataclass
class IpConnectionPair:
    source_ip: IPv4Address
    destination_ip: IPv4Address

    @classmethod
    def from_string_ip_addresses(cls, source_ip: str, destination_ip: str):
        return cls(IPv4Address(source_ip), IPv4Address(destination_ip))
