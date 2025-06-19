# core/ip_utils.py
import ipaddress
from typing import List

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError: return False

def is_private_ip(ip: str) -> bool:
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError: return False

def expand_targets(targets: List[str]) -> List[str]:
    """Expands a list of targets which can include IPs and CIDR ranges."""
    expanded_ips = []
    for target in targets:
        try:
            if '/' in target:
                network = ipaddress.ip_network(target, strict=False)
                expanded_ips.extend(str(ip) for ip in network.hosts())
            elif is_valid_ip(target):
                expanded_ips.append(target)
        except ValueError: continue
    return list(dict.fromkeys(expanded_ips)) # Remove duplicates