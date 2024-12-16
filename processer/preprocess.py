import re
from urllib.parse import urlparse, parse_qs
from googlesearch import search

class URLProcessor:
    def __init__(self):
        pass

    def is_valid_url(self, url):
        """Check if the URL is valid."""
        try:
            parsed_url = urlparse(url)
            return parsed_url.scheme in ['http', 'https'] and bool(parsed_url.netloc)
        except Exception:
            return False

    def breakdown_url(self, url):
        try:
            parsed_url = urlparse(url)
            scheme = parsed_url.scheme
            domain = parsed_url.netloc
            path = parsed_url.path
            query = parsed_url.query
            fragment = parsed_url.fragment
            path_parts = path.strip("/").split("/") if path else []
            query_params = parse_qs(query)
            query_keys = list(query_params.keys())
            query_values = [".".join(values) for values in query_params.values()]

            return {
                "original_url": url,
                "scheme": scheme,
                "domain": domain,
                "path": path,
                "path_parts": path_parts,
                "query": query,
                "query_keys": query_keys,
                "query_values": query_values,
                "fragment": fragment,
            }
        except ValueError as e:
            print(f"Error parsing URL {url}: {e}")
            return None

    def having_ip_address(self, url):
        if not url:
            return 0
        match = re.search(
            r"(([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."  # IPv4
            r"([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."  # IPv4 part
            r"([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\."  # IPv4 part
            r"([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\/)|"  # IPv4 ending
            r"((?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4})",  # IPv6
            url,
        )
        return 1 if match else 0

    def abnormal_url(self, url):
        try:
            hostname = urlparse(url).hostname or ""
            return 1 if hostname in url else 0
        except Exception:
            return 0

    def google_index(self, url):
        try:
            site = search(url, num_results=5)
            return 1 if site else 0
        except Exception:
            return 0

    def count_character(self, url, char):
        return url.count(char)

    def url_length(self, url):
        return len(url)

    def hostname_length(self, url):
        return len(urlparse(url).netloc)

    def suspicious_words(self, url):
        match = re.search(
            r"PayPal|login|signin|bank|account|update|free|lucky|service|bonus|ebayisapi|webscr",
            url,
        )
        return 1 if match else 0

    def digit_count(self, url):
        return sum(1 for char in url if char.isdigit())

    def letter_count(self, url):
        return sum(1 for char in url if char.isalpha())

    def shortening_service(self, url):
        match = re.search(
            r"bit\\.ly|goo\\.gl|shorte\\.st|go2l\\.ink|x\\.co|ow\\.ly|t\\.co|tinyurl|tr\\.im|is\\.gd|cli\\.gs|"
            r"yfrog\\.com|migre\\.me|ff\\.im|tiny\\.cc|url4\\.eu|twit\\.ac|su\\.pr|twurl\\.nl|snipurl\\.com|"
            r"short\\.to|BudURL\\.com|ping\\.fm|post\\.ly|Just\\.as|bkite\\.com|snipr\\.com|fic\\.kr|loopt\\.us|"
            r"doiop\\.com|short\\.ie|kl\\.am|wp\\.me|rubyurl\\.com|om\\.ly|to\\.ly|bit\\.do|lnkd\\.in|db\\.tt|"
            r"qr\\.ae|adf\\.ly|goo\\.gl|bitly\\.com|cur\\.lv|tinyurl\\.com|ow\\.ly|bit\\.ly|ity\\.im|q\\.gs|is\\.gd|po\\.st|"
            r"bc\\.vc|twitthis\\.com|u\\.to|j\\.mp|buzurl\\.com|cutt\\.us|u\\.bb|yourls\\.org|x\\.co|prettylinkpro\\.com|"
            r"scrnch\\.me|filoops\\.info|vzturl\\.com|qr\\.net|1url\\.com|tweez\\.me|v\\.gd|tr\\.im|link\\.zip\\.net",
            url,
        )
        return 1 if match else 0

    def process_url(self, url):
        if not self.is_valid_url(url):
            return {"error": "Invalid URL"}

        data = self.breakdown_url(url)
        if not data:
            return {"error": "Failed to process URL"}

        # Update features to match the specified order
        data.update({
            "use_of_ip": self.having_ip_address(url),
            "abnormal_url": self.abnormal_url(url),
            "google_index": self.google_index(url),
            "count_dot": self.count_character(url, "."),
            "count_www": self.count_character(url, "www"),
            "count_at": self.count_character(url, "@"),
            "count_dir": self.count_character(urlparse(url).path, "/"),
            "count_embed_domian": self.count_character(url, "//"),
            "short_url": self.shortening_service(url),
            "count_percent": self.count_character(url, "%"),
            "count_question": self.count_character(url, "?"),
            "count_hyphen": self.count_character(url, "-"),
            "count_equals": self.count_character(url, "="),
            "url_length": self.url_length(url),
            "hostname_length": self.hostname_length(url),
            "sus_url": self.suspicious_words(url),
            "count_digits": self.digit_count(url),
            "count_letters": self.letter_count(url),
        })
        return data
