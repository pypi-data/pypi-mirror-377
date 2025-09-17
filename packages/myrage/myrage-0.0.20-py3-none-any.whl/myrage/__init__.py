import os

from decolog.logger import Logger


APP_NAME = "MYRAGE"
LOG_PATH = os.path.join(
        os.environ['HOME'],
        ".local",
        "share",
        "myrage"
        )

TOR_CMD_PATH = "/usr/sbin/tor"
CONTROL_PORT = 9050
SOCKS_PORT = 9051
GEO_IP_FILE = os.path.abspath(os.path.join(__file__, "..", "geoip"))
GEO_IP_V6_FILE = os.path.abspath(os.path.join(__file__, "..", "geoip6"))
EXIT_NODES = "{BE}, {DE}, {IT}"
STRICT_NODES = 1

PROXIES = {
    "http": "socks5h://127.0.0.1:9051",
    "https": "socks5h://127.0.0.1:9051",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
    "AppleWebKit/537.36 (HTML, like Gecko) "
    "Chrome/39.0.2171.95 Safari/537.36"
}


app_name = (
    os.environ.get("APP_NAME").replace(" ", "_")
    if os.environ.get("APP_NAME") is not None
    else APP_NAME.replace(" ", "_")
)
logger = Logger(app_name=app_name, dir_path=LOG_PATH, log_level=20)
