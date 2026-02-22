import re
from collections import OrderedDict


NUMERIC_TOKEN = re.compile(r"\b\d+\b")
UUID_TOKEN = re.compile(
    r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
)
IP_TOKEN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
HEX_TOKEN = re.compile(r"\b(?:0x)?[0-9a-fA-F]{8,}\b")
ALNUM_ID_TOKEN = re.compile(
    r"(?<==)(?=[A-Za-z0-9]{8,}\b)(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b"
)
WINDOWS_PATH_TOKEN = re.compile(r"\b[A-Za-z]:\\(?:[^\\\s\"']+\\)*[^\\\s\"']+\b")
UNIX_PATH_TOKEN = re.compile(r"(?<![A-Za-z0-9_])/(?:[^/\s\"']+/)*[^/\s\"']+")
QUOTED_TOKEN = re.compile(r"\"[^\"\n]*\"|'[^'\n]*'")


def normalize_log_line(line: str) -> str:
    """Normalize dynamic values so similar log lines are grouped into one pattern."""
    normalized = UUID_TOKEN.sub("<UUID>", line.strip())
    normalized = WINDOWS_PATH_TOKEN.sub("<PATH>", normalized)
    normalized = UNIX_PATH_TOKEN.sub("<PATH>", normalized)
    normalized = IP_TOKEN.sub("<IP>", normalized)
    normalized = HEX_TOKEN.sub("<HEX>", normalized)
    normalized = ALNUM_ID_TOKEN.sub("<HEX>", normalized)
    normalized = QUOTED_TOKEN.sub("\"<STR>\"", normalized)
    normalized = NUMERIC_TOKEN.sub("<NUM>", normalized)
    return normalized


def extract_patterns(text: str) -> list[dict[str, str | int]]:
    grouped: OrderedDict[str, dict[str, str | int]] = OrderedDict()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        normalized = normalize_log_line(line)
        if normalized not in grouped:
            grouped[normalized] = {"pattern_text": normalized, "count": 0, "sample_line": line}
        grouped[normalized]["count"] = int(grouped[normalized]["count"]) + 1
    return list(grouped.values())
