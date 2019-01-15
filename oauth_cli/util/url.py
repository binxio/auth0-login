from urllib.parse import urlparse

def get_listen_port_from_url(url : str) -> int:
    """
    get the listen port from an url, if not specified, defaults to 443 for https and 80 for everything else.
    """
    result = urlparse(url)
    authority = result.netloc.split(':')
    return int(authority[1] if len(authority) == 2 else (443 if result.scheme == 'https' else 80))
