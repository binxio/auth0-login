#
# Copyright 2019 - binx.io B.V.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import socket
from urllib.parse import urlparse

from auth0_login.logging import fatal


def assert_listen_port_is_available(port: int):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(('0.0.0.0', port))
        s.close()
    except socket.error as e:
        fatal('port %d is not available, %s', port, e.strerror)


def get_listen_port_from_url(url: str) -> int:
    """
    get the listen port from an url, if not specified, defaults to 443 for https and 80 for everything else.
    """
    result = urlparse(url)
    authority = result.netloc.split(':')
    return int(authority[1] if len(authority) == 2 else (443 if result.scheme == 'https' else 80))
