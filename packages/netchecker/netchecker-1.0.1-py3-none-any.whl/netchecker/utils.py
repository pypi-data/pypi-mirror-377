import requests
from icmplib import ping


def can_send_icmp(host: str, count: int, timeout: int) -> bool:
    return ping(host, count=count, timeout=timeout).is_alive


def get(url, timeout=3) -> requests.Response:
    return requests.get(url, timeout=timeout)


def ok(status_code: int) -> bool:
    return status_code == 200
