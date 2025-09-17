import re
from decimal import Decimal
from urllib.parse import urlparse, parse_qs


def fetch_urls_from_text(text: str) -> list[str]:
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return urls


def fetch_url_param_value(*, url: str, param: str) -> str:
    parsed = urlparse(url)
    value = parse_qs(parsed.query)[param][0]
    return value


def calculate_tax(price: Decimal, tax: Decimal) -> Decimal:
    return price * tax
