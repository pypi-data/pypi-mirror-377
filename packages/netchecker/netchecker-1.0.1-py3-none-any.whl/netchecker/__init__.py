import socket
from .utils import can_send_icmp, get, ok


def has_dns(domains_override: list[str] | None = None) -> bool:
    """
    Check if DNS resolution is working by attempting to resolve github.com, google.com, and cloudflare.com.

    :type domains_override: list[str], None, optional
    :param domains_override: Optional list of domains to use instead of the default ones.
    """

    domains = [
        "www.github.com",
        "www.google.com",
        "www.cloudflare.com"
    ] if domains_override is None else domains_override

    domain_count: int = len(domains)
    failed: int = 0
    threshold: float = domain_count / 2  # more than 50% of the domains must resolve

    for domain in domains:
        try:
            socket.gethostbyname(domain)
        except socket.gaierror:
            failed += 1

    return failed < threshold


def has_internet(request_timeout: int = 3, ping_count: int = 4, server_override: list[str] | None = None) -> bool:
    """
    Check if the internet is reachable by sending ICMP requests to three known servers
    (8.8.8.8 - Google DNS, 1.1.1.1 - Cloudflare DNS, 9.9.9.9 - Quad9 DNS).

    :type request_timeout: int, optional
    :param request_timeout: Timeout for each ICMP request in seconds. Default is 3 seconds.

    :type ping_count: int, optional
    :param ping_count: Number of ICMP requests to send to each server. Default is 4.

    :type server_override: list[str], None, optional
    :param server_override: Optional list of server IPs to use instead of the default DNS servers.
    """

    servers: list[str] = [
        "8.8.8.8",
        "1.1.1.1",
        "9.9.9.9"
    ] if server_override is None else server_override

    server_count: int = len(servers)
    failed: int = 0
    threshold: float = server_count / 2  # more than 50% of the servers must respond

    for server in servers:
        can_send = can_send_icmp(
            server,
            count=ping_count,
            timeout=request_timeout
        )

        if not can_send:
            failed += 1

    return failed < threshold


def get_public_ip(https: bool = True) -> str | None:
    """
    Get the public IP address of the machine.

    :return: The public IP address as a string, or None if it could not be determined.
    :rtype: str | None
    """

    services: dict[str, list[str]] = {
        "https": [
            "https://api.ipify.org/",
            "https://icanhazip.com/",
            "https://ifconfig.me/ip",
            "https://ipecho.net/plain",
        ],
        "http": [
            "http://checkip.amazonaws.com/",
            "http://ifconfig.me/ip",
        ],
    }

    if https:
        for service in services["https"]:
            try:
                response = get(service)
                if response.status_code == 200:
                    return response.text.strip()
            except Exception:
                continue

    for service in services["http"]:
        try:
            response = get(service)
            if ok(response.status_code):
                return response.text.strip()
        except Exception:
            continue

    return None
