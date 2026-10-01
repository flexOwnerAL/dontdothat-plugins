# fuck off anhedonuya, im the leader
import asyncio
import copy
import csv
import difflib
import hashlib
import hmac
import html
import io
import json
import math
import random
import re
import secrets as _secrets
import sqlite3
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional
from urllib.parse import quote_plus, unquote, urljoin, urlparse, parse_qsl, urlencode, urlunparse
from urllib.request import Request, urlopen, build_opener, ProxyHandler

from core.tetko import Module, command, watcher, loop

try:
    from curl_cffi.requests import AsyncSession as _CurlSession
    _HAS_CURL = True
except Exception:
    _CurlSession = None
    _HAS_CURL = False

try:
    import httpx
    _HAS_HTTPX = True
except Exception:
    _HAS_HTTPX = False

try:
    import pymorphy2
    _MORPH = pymorphy2.MorphAnalyzer()
except Exception:
    _MORPH = None

try:
    from telethon.tl.custom import Button as _TButton
except Exception:
    _TButton = None

try:
    from telethon import events as _tg_events
except Exception:
    _tg_events = None


USER_AGENTS_BY_REGION = {
    "ru": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/25.2.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/25.2.0.00 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 YaBrowser/24.11.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 YaBrowser/24.10.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 YaBrowser/24.9.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 YaBrowser/24.8.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 YaBrowser/24.7.0.00 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 YaBrowser/24.6.0.00 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 16; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/25.2.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 16; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/25.2.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 15; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 15; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 YaBrowser/24.11.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 YaBrowser/24.10.0.00 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 YaBrowser/25.2.0.00 YaBrowser/25.2.0.00 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 YaBrowser/25.1.0.00 YaBrowser/25.1.0.00 Safari/605.1.15",
        "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 YaBrowser/25.2.0.00 YaBrowser/25.2.0.00 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 YaBrowser/25.2.0.00 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 YaBrowser/25.2.0.00 Safari/537.36",
    ],
    "en": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
        "Mozilla/5.0 (Linux; Android 16; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 15; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Vivaldi/7.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Brave/1.70",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Brave/1.70",
    ],
    "cn": [
        "Mozilla/5.0 (Linux; Android 16; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 16; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 15; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 16; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36 Quark/7.0",
        "Mozilla/5.0 (Linux; Android 15; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 UCBrowser/17.0",
    ],
}

CLOUDFLARE_MARKERS = (
    "just a moment",
    "checking your browser",
    "checking if the site connection is secure",
    "cf-browser-verification",
    "cf-challenge",
    "cf_chl_",
    "cf_chl_opt",
    "cf_chl_prog",
    "cf_chl_2",
    "__cf_chl",
    "__cf_chl_rt_tk",
    "__cf_bm",
    "__cfduid",
    "__cfruid",
    "cf_clearance",
    "attention required",
    "ddos protection by cloudflare",
    "cloudflare ray id",
    "cloudflare-nginx",
    "cloudflare.com/cdn-cgi",
    "cdn-cgi/challenge-platform",
    "cdn-cgi/trace",
    "cdn-cgi/l/chk_jschl",
    "cf-please-wait",
    "cf-error-details",
    "ray id:",
    "performance & security by cloudflare",
    "please wait while we verify",
    "verify you are human",
    "verifying you are human",
    "enable javascript and cookies to continue",
    "enable javascript and cookies",
    "this process is automatic",
    "your browser will redirect",
    "one more step",
    "complete the security check",
    "verify you are not a robot",
    "protected by cloudflare",
    "powered by cloudflare",
    "cloudflare protection",
    "cf-verify",
    "cf_challenge_",
    "cloudflare_challenge",
    "web application firewall",
    "waf by cloudflare",
    "cloudflare bot management",
    "bot management by cloudflare",
    "cloudflare turnstile",
    "challenges.cloudflare.com",
    "turnstile challenge",
    "cf-turnstile",
    "cf_turnstile",
    "why have i been blocked",
    "what can i do to resolve this",
    "you are unable to access",
    "the owner of this website has banned your access",
    "the owner of this website has banned",
    "access denied | cloudflare",
    "error 1020",
    "error 1015",
    "error 1005",
    "error 1006",
    "error 1007",
    "error 1008",
    "error 1009",
    "error 1010",
    "error 1011",
    "error 1012",
    "error 1013",
    "error 1014",
    "error 1016",
    "error 1018",
    "error 1019",
    "error 1021",
    "error 1022",
    "error 1023",
    "error 1024",
    "error 1025",
    "error 1027",
    "error 1028",
    "error 1029",
    "error 1030",
    "error 1031",
    "error 1032",
    "error 1033",
    "error 1034",
    "error 1035",
    "error 1036",
    "error 1037",
    "error 1038",
    "error 1039",
    "error 1040",
    "error 1041",
    "error 1042",
    "error 1043",
    "error 1044",
    "error 1045",
    "error 1046",
    "error 1047",
    "error 1048",
    "error 1049",
    "error 1050",
    "error 1051",
    "error 1052",
    "error 1053",
    "error 1054",
    "error 1055",
    "error 1056",
    "error 1057",
    "error 1058",
    "error 1059",
    "error 1060",
    "error 1061",
    "error 1062",
    "error 1063",
    "error 1064",
    "error 1065",
    "error 1066",
    "error 1067",
    "error 1068",
    "error 1069",
    "error 1070",
    "error 1071",
    "error 1072",
    "error 1073",
    "error 1074",
    "error 1075",
    "error 1076",
    "error 1077",
    "error 1078",
    "error 1079",
    "error 1080",
    "error 1081",
    "error 1082",
    "error 1083",
    "error 1084",
    "error 1085",
    "error 1086",
    "error 1087",
    "error 1088",
    "error 1089",
    "error 1090",
    "error 1091",
    "error 1092",
    "error 1093",
    "error 1094",
    "error 1095",
    "error 1096",
    "error 1097",
    "error 1098",
    "error 1099",
    "error 1100",
    "error 1101",
    "error 1102",
    "error 1103",
    "error 1104",
    "error 1105",
    "error 1106",
    "error 1107",
    "error 1108",
    "error 1109",
    "error 1110",
    "error 1111",
    "error 1112",
    "error 1113",
    "error 1114",
    "error 1115",
    "error 1116",
    "error 1117",
    "error 1118",
    "error 1119",
    "error 1120",
    "error 1121",
    "error 1122",
    "error 1123",
    "error 1124",
    "error 1125",
    "error 1126",
    "error 1127",
    "error 1128",
    "error 1129",
    "error 1130",
    "error 1131",
    "error 1132",
    "error 1133",
    "error 1134",
    "error 1135",
    "error 1136",
    "error 1137",
    "error 1138",
    "error 1139",
    "error 1140",
    "error 1141",
    "error 1142",
    "error 1143",
    "error 1144",
    "error 1145",
    "error 1146",
    "error 1147",
    "error 1148",
    "error 1149",
    "error 1150",
    "error 1151",
    "error 1152",
    "error 1153",
    "error 1154",
    "error 1155",
    "error 1156",
    "error 1157",
    "error 1158",
    "error 1159",
    "error 1160",
)

CAPTCHA_MARKERS = (
    "complete the following challenge", "select all squares", "confirm this search was made by a human",
    "unfortunately, bots", "please complete the challenge", "g-recaptcha", "recaptcha/api",
    "hcaptcha.com", "h-captcha", "are you human", "verify you are human", "verify you are not a robot",
    "unusual traffic", "our systems have detected unusual", "automated queries",
    "верификация", "проверка браузера", "подтвердите, что запросы", "капча",
    "cf-turnstile", "turnstile challenge", "challenges.cloudflare.com",
)

JS_MARKERS = (
    "you need to enable javascript", "please enable javascript", "enable javascript to continue",
    "javascript is required", "window.__nuxt__", "__next_data__", "window.__initial_state__",
    'id="root"', 'id="app"',
)

STOPWORDS = (
    "cookie", "cookies", "subscribe", "sign in", "log in", "javascript",
    "privacy policy", "terms of service", "all rights reserved",
)

PII_REDACTION = (
    (re.compile(r"(?i)\b(?:password|passwd|pwd|token|api[_-]?key|secret|authorization|cookie|session[_-]?id)\s*[:=]\s*\S+"), "[redacted]"),
    (re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b"), "[phone hidden]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[ip hidden]"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[email hidden]"),
)

PRIVATE_HOST_PATTERNS = re.compile(
    r"^(?:localhost$"
    r"|127\."
    r"|\[::1\]$"
    r"|::1$"
    r"|0\.0\.0\.0$"
    r"|10\."
    r"|172\.(?:1[6-9]|2\d|3[01])\."
    r"|192\.168\."
    r"|169\.254\."
    r"|fe80:"
    r"|fc[0-9a-f]{2}:"
    r"|fd[0-9a-f]{2}:"
    r"|\.local$"
    r"|metadata\.google\.internal$"
    r"|metadata\.goog$"
    r")",
    re.IGNORECASE,
)

SITE_URL_OVERRIDES = {
    "duckduckgo.com": {"url": "https://lite.duckduckgo.com/lite/?q={query}", "param": "q", "note": "lite.ddg"},
    "html.duckduckgo.com": {"url": "https://lite.duckduckgo.com/lite/?q={query}", "param": "q", "note": "lite.ddg"},
    "google.com": {"url": "https://www.google.com/search?q={query}&num=20&gbv=1", "param": "q", "note": "basic html"},
    "reddit.com": {"url": "https://old.reddit.com/search?q={query}", "param": "q", "note": "old reddit"},
    "www.reddit.com": {"url": "https://old.reddit.com/search?q={query}", "param": "q", "note": "old reddit"},
    "twitter.com": {"url": "https://nitter.net/search?q={query}", "param": "q", "note": "nitter"},
    "x.com": {"url": "https://nitter.net/search?q={query}", "param": "q", "note": "nitter"},
    "youtube.com": {"url": "https://www.youtube.com/results?search_query={query}&sp=EgIQAQ%253D%253D", "param": "search_query", "note": "video filter"},
    "github.com": {"url": "https://github.com/search?q={query}&type=repositories", "param": "q", "note": "repos"},
}

API_PRESETS = {
    "github-api": {"url": "https://api.github.com/search/repositories?q={query}", "type": "json", "path": "items", "title_field": "full_name", "url_field": "html_url", "desc_field": "description", "param": "q"},
    "github-users": {"url": "https://api.github.com/search/users?q={query}", "type": "json", "path": "items", "title_field": "login", "url_field": "html_url", "desc_field": "type", "param": "q"},
    "hibp-breaches": {"url": "https://haveibeenpwned.com/api/v3/breaches", "type": "json", "path": None, "title_field": "Name", "url_field": "Domain", "desc_field": "Description", "param": None},
    "reddit-json": {"url": "https://www.reddit.com/search.json?q={query}&limit=25", "type": "json", "path": "data.children", "title_field": "data.title", "url_field": "data.url", "desc_field": "data.selftext", "param": "q"},
    "wikipedia-api": {"url": "https://ru.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=20&format=json", "type": "json", "path": None, "special": "opensearch", "param": "search"},
}

DEFAULT_SITES = {
    "lite_ddg": {"url": "https://lite.duckduckgo.com/lite/?q={query}", "host": "lite.duckduckgo.com", "alive": None, "tags": ["web"], "priority": "high"},
    "mojeek": {"url": "https://www.mojeek.com/search?q={query}", "host": "www.mojeek.com", "alive": None, "tags": ["web"], "priority": "normal"},
    "marginalia": {"url": "https://search.marginalia.nu/search?query={query}", "host": "search.marginalia.nu", "alive": None, "tags": ["web"], "priority": "normal"},
    "wiki": {"url": "https://ru.wikipedia.org/w/index.php?search={query}", "host": "ru.wikipedia.org", "alive": None, "tags": ["wiki"], "priority": "normal"},
}

ENTITY_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+?\d[\d\s().-]{7,}\d)\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "btc": re.compile(r"\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b"),
    "eth": re.compile(r"\b0x[a-fA-F0-9]{40}\b"),
    "domain": re.compile(r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b"),
    "telegram": re.compile(r"@[A-Za-z][A-Za-z0-9_]{4,31}\b"),
}

ROLE_ORDER = {
    "guest": -1, "viewer": 0, "contributor": 1, "verified": 2, "searcher": 2,
    "editor": 3, "admin": 4, "superadmin": 5, "owner": 6,
}

ROLE_COMMANDS = {
    "guest": {"whoami", "help", "version"},
    "viewer": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency"},
    "contributor": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending"},
    "verified": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending", "search", "multi", "trace", "raw", "retry", "history", "profile", "page", "openall", "json", "save", "saved"},
    "searcher": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending", "search", "multi", "trace", "raw", "retry", "history", "profile", "page", "openall", "json", "save", "saved"},
    "editor": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending", "search", "multi", "trace", "raw", "retry", "history", "profile", "page", "openall", "json", "save", "saved", "add", "remove", "enable", "disable", "rename", "clone", "tag", "priority", "ping", "heal", "doctor", "dead", "slow", "slow-source", "watch", "note", "notes", "snapshot", "diff", "export", "audit-me"},
    "admin": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending", "search", "multi", "trace", "raw", "retry", "history", "profile", "page", "openall", "json", "save", "saved", "add", "remove", "enable", "disable", "rename", "clone", "tag", "priority", "ping", "heal", "doctor", "dead", "slow", "slow-source", "watch", "note", "notes", "snapshot", "diff", "export", "audit-me", "logs", "metrics", "audit", "mute", "unmute"},
    "superadmin": {"whoami", "help", "version", "sites", "tags", "info", "stat", "top", "dashboard", "my-stats", "latency", "add-contrib", "pending", "search", "multi", "trace", "raw", "retry", "history", "profile", "page", "openall", "json", "save", "saved", "add", "remove", "enable", "disable", "rename", "clone", "tag", "priority", "ping", "heal", "doctor", "dead", "slow", "slow-source", "watch", "note", "notes", "snapshot", "diff", "export", "audit-me", "logs", "metrics", "audit", "mute", "unmute", "plugin", "plugins", "cfg", "import"},
    "owner": None,
}


class DontDoThat(Module):
    name = "DontDoThat"
    __compat__ = "0.0.9.0"
    version = "6.8.0"
    author = "@flexOwnerAL"
    description = "Public web search with roles, plugins, trust, morfology, boolean ops, readability, backup, audit."

    config = {
        "sites": {},
        "sites_initialized": False,
        "timeout": 12,
        "max_bytes": 500_000,
        "max_links": 50,
        "max_parallel": 5,
        "max_snippet": 1200,
        "max_sources_display": 10,
        "healthcheck_interval": 3600,
        "cache_ttl": 300,
        "log_searches": False,
        "default_param": "q",
        "use_jina": True,
        "use_curl_cffi": True,
        "blocked_detection": True,
        "js_detection": True,
        "priority_first": True,
        "cf_refuse": True,
        "captcha_bypass": True,
        "captcha_bypass_retries": 2,
        "proxies": [],
        "tor_proxy": "socks5://127.0.0.1:9050",
        "use_tor": False,
        "region_ua": True,
        "highlight_matches": True,
        "rate_limit_seconds": 0.5,
        "persist_stats": True,
        "history_size": 50,
        "audit_log": True,
        "sqlite_log": True,
        "plugins_enabled": True,
        "plugins_dir": "data/dontdothat_plugins",
        "plugins_repo": "flexOwnerAL/dontdothat-plugins",
        "plugins_repo_branch": "main",
        "plugins_index_path": "index.json",
        "plugins_index_ttl": 3600,
        "trusted_plugin_authors": [],
        "trusted_plugin_repos": [],
        "privileged_plugin_authors": [],
        "plugin_trust_overrides": {},
        "require_signed_plugins": False,
        "plugins_metadata": {},
        "watchers": [],
        "site_overrides": True,
        "auto_fallback_url": True,
        "cookies_enabled": True,
        "snapshots_enabled": True,
        "notes": {},
        "saved_results": {},
        "synonyms": {},
        "templates": {},
        "webhook_url": "",
        "webhook_secret": "",
        "webhook_retries": 3,
        "allowed_chats": [],
        "blocked_users": [],
        "trusted_chat_id": None,
        "trusted_log_chat": None,
        "rate_limit_per_user": 30,
        "user_rate_map": {},
        "roles": {"admins": [], "superadmins": [], "editors": [], "contributors": [], "verified": [], "searchers": [], "viewers": [], "guests": [], "trusted": []},
        "role_commands": {},
        "role_rate": {"guest": 0, "viewer": 10, "contributor": 20, "verified": 30, "searcher": 30, "editor": 100, "admin": 200, "superadmin": 500},
        "trusted_quotas": {},
        "quota_used": {},
        "pending_sources": {},
        "pending_next_id": 1,
        "pending_actions": {},
        "muted_until": {},
        "blocked_queries": [],
        "notify_owner_on_trusted": True,
        "cc_owner_on_trusted": False,
        "auto_demote_threshold": 60,
        "auto_demote_window": 3600,
        "bm25_k1": 1.5,
        "bm25_b": 0.75,
        "dedup_threshold": 0.85,
        "auto_disable_threshold": 10,
        "entities_enabled": True,
        "operators_enabled": True,
        "require_approval_for_remove": True,
        "role_requires_trusted": False,
        "sites_per_page": 5,
        "trusted_per_page": 5,
        "use_inline_bot": False,
        "inline_cb_ttl": 900,
        "inline_edit_in_place": False,
        "menu_ttl": 3600,
        "morphology_enabled": True,
        "readability_enabled": True,
        "boolean_operators_enabled": True,
        "backup_encryption_key": "",
        "plugin_quota_per_minute": 60,
        "source_weight_default": 1.0,
        "pii_filter_in_snippet": False,
        "pending_actions_ttl": 86400,
        "slow_query_threshold": 5.0,
        "cookie_jar_max": 500,
        "user_activity_max": 500,
        "morph_cache_max": 5000,
        "latency_max_entries": 200,
    }

    _RX_URL = re.compile(r"https?://\S+")
    _RX_WORD = re.compile(r"\w+", re.UNICODE)
    _RX_CYR = re.compile(r"[а-яё]", re.IGNORECASE)
    _RX_FLAG = re.compile(r'--(\w+)(?:=(?:"([^"]*)"|\'([^\']*)\'|(\S+)))?')
    _RX_BARE_URL = re.compile(r"\b([a-zA-Z0-9][a-zA-Z0-9-]*(?:\.[a-zA-Z0-9-]+)+(?:/[^\s]*)?)")
    _RX_QUOTED = re.compile(r'"([^"]+)"')
    _RX_TOKEN = re.compile(r'("(?:[^"\\]|\\.)*"|\(|\)|\bAND\b|\bOR\b|\bNOT\b|[+\-]?\S+)', re.IGNORECASE)
    _RX_WILDCARD = re.compile(r"(\w+)\*")
    _RX_FUZZY = re.compile(r"~(\w+)")
    _RX_DDG_REDIRECT = re.compile(
        r"^https?://(?:lite\.|html\.|www\.)?duckduckgo\.com/l/\?[^\"']*?uddg=([^&\s\"']+)",
        re.IGNORECASE,
    )
    _RX_DDG_REDIRECT_INLINE = re.compile(
        r"https?://(?:lite\.|html\.|www\.)?duckduckgo\.com/l/\?[^\"'\s>]*?uddg=([^&\s\"'>]+)",
        re.IGNORECASE,
    )
    _RX_TITLE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
    _RX_OG_TITLE = re.compile(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE)
    _RX_TW_TITLE = re.compile(r'<meta[^>]+name=["\']twitter:title["\'][^>]+content=["\']([^"\']+)["\']', re.IGNORECASE)
    _RX_H1 = re.compile(r"(?is)<h1[^>]*>(.*?)</h1>")

    def __init__(self, kernel=None):
        super().__init__(kernel)
        self._sem = None
        self._sem_limit = None
        self._sem_lock = threading.Lock()
        self._sqlite_lock = threading.Lock()
        self._morph_lock = threading.Lock()
        self._rate_lock = threading.Lock()
        self._cache = {}
        self._stats = {
            "total_queries": 0, "total_sources_hit": 0, "top_queries": {}, "per_source": {},
            "per_source_fail": {}, "per_user": {}, "latency": {}, "slow_queries": [],
        }
        self._history = []
        self._audit = []
        self._rate_limit_map = {}
        self._last_result = {}
        self._plugins = {}
        self._hooks = {
            "before_fetch": [], "after_fetch": [], "on_blocked": [], "on_js_required": [],
            "on_error": [], "on_result": [], "on_search": [], "on_command": [],
            "on_start": [], "on_stop": [], "on_menu": [], "on_button": [],
            "on_stats": [], "on_sites_change": [], "on_role_change": [], "on_help": [],
            "on_plugin_load": [], "on_plugin_unload": [], "on_backup": [], "on_restore": [],
        }
        self._sqlite = None
        self._cookie_jar = {}
        self._strategy_stats = {}
        self._repo_index_cache = {}
        self._dead_services = set()
        self._user_activity = {}
        self._active_menus = {}
        self._my_tokens = set()
        self._morph_cache = {}
        self._plugin_quota = {}
        self._state_loaded = False
        self._load_persistent_state()

    async def on_load(self):
        if not self._state_loaded:
            self._load_persistent_state()
            self._state_loaded = True
        if self.cfg.get("plugins_enabled", True):
            d = self._plugins_dir()
            if d.exists():
                for py in sorted(d.glob("*.py")):
                    if py.name.startswith("_"):
                        continue
                    ok, msg, _ = await self._load_plugin_from_path(py, source="local")
                    if not ok:
                        try:
                            self.log.warning(f"[DontDoThat] plugin {py.name} failed: {msg}")
                        except Exception:
                            pass
        await self._run_hook("on_start", {"module": self})

    async def on_unload(self):
        try:
            inline = getattr(self.kernel, "inline", None)
            handlers = getattr(inline, "_handlers", None) if inline is not None else None
            if isinstance(handlers, dict):
                for token in list(self._my_tokens):
                    handlers.pop(token, None)
        except Exception:
            pass
        self._my_tokens.clear()
        self._active_menus.clear()
        await self._run_hook("on_stop", {"module": self})

    def _load_persistent_state(self):
        if not self.cfg.get("persist_stats", True):
            return
        try:
            data = self.cfg.get("_stats_cache") or {}
            if isinstance(data, dict):
                for k in ("total_queries", "total_sources_hit", "top_queries", "per_source", "per_source_fail", "per_user", "latency", "slow_queries"):
                    if k in data:
                        self._stats[k] = data[k]
            hist = self.cfg.get("_history_cache") or []
            if isinstance(hist, list):
                self._history = hist[-int(self.cfg.get("history_size", 50) or 50):]
            ck = self.cfg.get("_cookie_cache") or {}
            if isinstance(ck, dict):
                self._cookie_jar = ck
            ss = self.cfg.get("_strategy_stats") or {}
            if isinstance(ss, dict):
                self._strategy_stats = ss
        except Exception:
            pass

    def _save_persistent_state(self):
        if not self.cfg.get("persist_stats", True):
            return
        try:
            self.cfg.set("_stats_cache", self._stats)
            self.cfg.set("_history_cache", self._history[-int(self.cfg.get("history_size", 50) or 50):])
            self.cfg.set("_cookie_cache", self._cookie_jar)
            self.cfg.set("_strategy_stats", self._strategy_stats)
        except Exception:
            pass

    def _audit_log(self, actor, action, details=""):
        if not self.cfg.get("audit_log", True):
            return
        self._audit.append({
            "ts": time.time(),
            "actor": str(actor) if actor is not None else "?",
            "action": action,
            "details": details[:300],
        })
        if len(self._audit) > 2000:
            self._audit = self._audit[-2000:]

    def _sqlite_conn(self):
        if not self.cfg.get("sqlite_log", True):
            return None
        if self._sqlite is not None:
            return self._sqlite
        with self._sqlite_lock:
            if self._sqlite is not None:
                return self._sqlite
            try:
                path = Path("data/dontdothat.db")
                path.parent.mkdir(parents=True, exist_ok=True)
                conn = sqlite3.connect(str(path), check_same_thread=False)
                try:
                    conn.execute("PRAGMA journal_mode=WAL")
                except Exception:
                    pass
                conn.execute("CREATE TABLE IF NOT EXISTS fetches (ts REAL, source TEXT, url TEXT, status INTEGER, elapsed REAL, size INTEGER, blocked INTEGER, verdict TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS queries (ts REAL, actor TEXT, query TEXT, hits INTEGER, errors INTEGER)")
                conn.execute("CREATE TABLE IF NOT EXISTS snapshots (ts REAL, source TEXT, query TEXT, url TEXT, html TEXT)")
                conn.execute("CREATE TABLE IF NOT EXISTS slow_queries (ts REAL, actor TEXT, query TEXT, elapsed REAL, hits INTEGER)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_fetches_ts ON fetches(ts)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_queries_ts ON queries(ts)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_sq ON snapshots(source, query, ts)")
                try:
                    conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS queries_fts USING fts5(query, actor, content='queries', content_rowid='rowid')")
                except Exception:
                    pass
                conn.commit()
                self._sqlite = conn
            except Exception:
                self._sqlite = None
        return self._sqlite

    def _sqlite_log_fetch(self, source, url, status, elapsed, size, blocked, verdict):
        c = self._sqlite_conn()
        if c is None:
            return
        try:
            with self._sqlite_lock:
                c.execute(
                    "INSERT INTO fetches (ts, source, url, status, elapsed, size, blocked, verdict) VALUES (?,?,?,?,?,?,?,?)",
                    (time.time(), source, url[:2000], status, elapsed, size, 1 if blocked else 0, verdict[:200]),
                )
                c.commit()
        except Exception:
            pass

    def _sqlite_log_query(self, actor, query, hits, errors):
        c = self._sqlite_conn()
        if c is None:
            return
        try:
            with self._sqlite_lock:
                c.execute(
                    "INSERT INTO queries (ts, actor, query, hits, errors) VALUES (?,?,?,?,?)",
                    (time.time(), str(actor) if actor is not None else "?", query, hits, errors),
                )
                c.commit()
        except Exception:
            pass

    def _sqlite_log_slow(self, actor, query, elapsed, hits):
        c = self._sqlite_conn()
        if c is None:
            return
        try:
            with self._sqlite_lock:
                c.execute(
                    "INSERT INTO slow_queries (ts, actor, query, elapsed, hits) VALUES (?,?,?,?,?)",
                    (time.time(), str(actor) if actor is not None else "?", query, elapsed, hits),
                )
                c.commit()
        except Exception:
            pass

    def _sqlite_save_snapshot(self, source, query, url, html_text):
        if not self.cfg.get("snapshots_enabled", True):
            return
        c = self._sqlite_conn()
        if c is None:
            return
        try:
            with self._sqlite_lock:
                c.execute(
                    "INSERT INTO snapshots (ts, source, query, url, html) VALUES (?,?,?,?,?)",
                    (time.time(), source, query, url, html_text[:500_000]),
                )
                c.commit()
        except Exception:
            pass

    def _semaphore(self):
        limit = int(self.cfg.get("max_parallel", 5) or 5)
        limit = max(1, limit)
        with self._sem_lock:
            if self._sem is None or self._sem_limit != limit:
                self._sem = asyncio.Semaphore(limit)
                self._sem_limit = limit
            return self._sem

    def _prefix(self):
        try:
            return getattr(self.kernel.context, "prefix", ".") or "."
        except Exception:
            return "."

    def _sender_id(self, event):
        s = getattr(event, "sender_id", None)
        if s is None:
            s = getattr(getattr(event, "from_user", None), "id", None)
        try:
            return int(s) if s is not None else None
        except (TypeError, ValueError):
            return None

    def _is_owner(self, event):
        try:
            return bool(self.kernel.context.is_owner(self._sender_id(event)))
        except Exception:
            return False

    def _role_of(self, event):
        if self._is_owner(event):
            return "owner"
        sid = self._sender_id(event)
        if sid is None:
            return None
        r = self.cfg.get("roles", {}) or {}
        for role_key, role_name in (
            ("superadmins", "superadmin"), ("admins", "admin"), ("editors", "editor"),
            ("verified", "verified"), ("contributors", "contributor"), ("searchers", "searcher"),
            ("viewers", "viewer"), ("guests", "guest"), ("trusted", "searcher"),
        ):
            if sid in (r.get(role_key) or []):
                return role_name
        return None

    def _role_of_by_uid(self, uid):
        if uid is None:
            return None
        try:
            if int(self.kernel.context.admin_id) == int(uid):
                return "owner"
        except Exception:
            pass
        r = self.cfg.get("roles", {}) or {}
        for role_key, role_name in (
            ("superadmins", "superadmin"), ("admins", "admin"), ("editors", "editor"),
            ("verified", "verified"), ("contributors", "contributor"), ("searchers", "searcher"),
            ("viewers", "viewer"), ("guests", "guest"), ("trusted", "searcher"),
        ):
            if uid in (r.get(role_key) or []):
                return role_name
        return None

    def _role_gte(self, role, target):
        return ROLE_ORDER.get(role or "", -99) >= ROLE_ORDER.get(target, 99)

    def _has_role(self, event, target):
        return self._role_gte(self._role_of(event), target)

    def _is_trusted_uid(self, uid):
        if uid is None:
            return False
        r = self.cfg.get("roles", {}) or {}
        for k in ("superadmins", "admins", "editors", "verified", "contributors", "searchers", "viewers", "guests", "trusted"):
            if uid in (r.get(k) or []):
                return True
        return False

    def _set_role(self, uid, role):
        r = self.cfg.get("roles", {}) or {}
        for k in ("superadmins", "admins", "editors", "verified", "contributors", "searchers", "viewers", "guests", "trusted"):
            r[k] = [x for x in (r.get(k) or []) if x != uid]
        mapping = {
            "superadmin": "superadmins", "admin": "admins", "editor": "editors",
            "verified": "verified", "contributor": "contributors", "searcher": "searchers",
            "viewer": "viewers", "guest": "guests", "trusted": "trusted",
        }
        key = mapping.get(role)
        if key:
            r.setdefault(key, []).append(uid)
        self.cfg.set("roles", r)

    def _remove_role(self, uid):
        r = self.cfg.get("roles", {}) or {}
        for k in ("superadmins", "admins", "editors", "verified", "contributors", "searchers", "viewers", "guests", "trusted"):
            r[k] = [x for x in (r.get(k) or []) if x != uid]
        self.cfg.set("roles", r)

    def _is_muted(self, uid):
        m = self.cfg.get("muted_until", {}) or {}
        until = m.get(str(uid))
        if not until:
            return None
        if until < time.time():
            m.pop(str(uid), None)
            self.cfg.set("muted_until", m)
            return None
        return until

    def _mute_user(self, uid, seconds):
        m = self.cfg.get("muted_until", {}) or {}
        m[str(uid)] = time.time() + seconds
        self.cfg.set("muted_until", m)

    def _unmute_user(self, uid):
        m = self.cfg.get("muted_until", {}) or {}
        m.pop(str(uid), None)
        self.cfg.set("muted_until", m)

    def _sites(self):
        data = self.cfg.get("sites", {}) or {}
        if not isinstance(data, dict):
            data = {}
        if not self.cfg.get("sites_initialized", False):
            if not data and DEFAULT_SITES:
                data = copy.deepcopy(DEFAULT_SITES)
            self.cfg.set("sites", data)
            self.cfg.set("sites_initialized", True)
        return data

    def _save_sites(self, data):
        self.cfg.set("sites", data)
        self.cfg.set("sites_initialized", True)

    def _args(self, event):
        text = (getattr(event, "raw_text", "") or "").strip()
        p = self._prefix()
        if not text.startswith(p):
            return ""
        body = text[len(p):]
        parts = body.split(maxsplit=1)
        return parts[1].strip() if len(parts) > 1 else ""

    def _clean(self, text):
        for rx, repl in PII_REDACTION:
            text = rx.sub(repl, text)
        return text

    def _normalize(self, text):
        return text.lower().replace("ё", "е")

    def _lemmatize(self, text):
        if not self.cfg.get("morphology_enabled", True) or _MORPH is None:
            return self._normalize(text)
        norm = self._normalize(text)
        out = []
        with self._morph_lock:
            for w in self._RX_WORD.findall(norm):
                if len(w) <= 2:
                    out.append(w)
                    continue
                cached = self._morph_cache.get(w)
                if cached is not None:
                    out.append(cached)
                    continue
                try:
                    lemma = _MORPH.parse(w)[0].normal_form
                except Exception:
                    lemma = w
                self._morph_cache[w] = lemma
                out.append(lemma)
                if len(self._morph_cache) > int(self.cfg.get("morph_cache_max", 5000) or 5000):
                    self._morph_cache = dict(list(self._morph_cache.items())[-2500:])
        return " ".join(out)

    def _region_for_url(self, url):
        try:
            host = urlparse(url).netloc.lower()
        except Exception:
            return "en"
        if host.endswith(".ru") or host.endswith(".рф") or host.endswith(".su") or host.endswith(".by") or host.endswith(".kz"):
            return "ru"
        if host.endswith(".cn") or "baidu" in host:
            return "cn"
        return "en"

    def _pick_ua(self, url):
        pool = USER_AGENTS_BY_REGION.get(self._region_for_url(url), USER_AGENTS_BY_REGION["en"]) if self.cfg.get("region_ua", True) else USER_AGENTS_BY_REGION["en"]
        return random.choice(pool)

    def _is_cloudflare(self, text):
        low = (text or "").lower()
        return any(m in low for m in CLOUDFLARE_MARKERS)

    def _is_captcha(self, text):
        low = (text or "").lower()
        return any(m in low for m in CAPTCHA_MARKERS)

    def _looks_blocked(self, text):
        if not self.cfg.get("blocked_detection", True):
            return False
        return self._is_cloudflare(text) or self._is_captcha(text)

    def _looks_js_required(self, text, raw_html=""):
        if not self.cfg.get("js_detection", True):
            return False
        low = (text or "").lower()
        if any(m in low for m in JS_MARKERS):
            return True
        rl = (raw_html or "").lower()
        if any(m in rl for m in JS_MARKERS):
            return True
        if len((text or "").strip()) < 250 and len(raw_html or "") > 30_000:
            return True
        return False

    def _is_ssrf_safe(self, url):
        try:
            p = urlparse(url)
        except Exception:
            return False
        if p.scheme.lower() not in ("http", "https"):
            return False
        host = (p.hostname or "").lower()
        if not host:
            return False
        if PRIVATE_HOST_PATTERNS.search(host):
            return False
        if host.endswith(".onion"):
            return bool(self.cfg.get("use_tor", False))
        return True

    def _extract_embedded_json(self, raw_html):
        out = {}
        for marker, pattern in (
            ("next", r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'),
            ("nuxt", r'window\.__NUXT__\s*=\s*(\{.*?\});'),
            ("initial_state", r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'),
            ("ld_json", r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>'),
        ):
            m = re.search(pattern, raw_html, re.DOTALL | re.IGNORECASE)
            if not m:
                continue
            try:
                out[marker] = json.loads(m.group(1).strip())
            except Exception:
                continue
        return out

    def _extract_meta(self, raw_html):
        meta = {}
        for name, pattern in (
            ("og_title", r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']'),
            ("og_desc", r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']'),
            ("og_image", r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']'),
            ("author", r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']'),
            ("date", r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']'),
            ("desc", r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']'),
            ("canonical", r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']'),
        ):
            m = re.search(pattern, raw_html, re.IGNORECASE)
            if m:
                meta[name] = html.unescape(m.group(1).strip())[:300]
        return meta

    def _flatten_json(self, obj, out):
        if isinstance(obj, dict):
            for v in obj.values():
                self._flatten_json(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._flatten_json(v, out)
        elif isinstance(obj, (str, int, float)):
            s = str(obj)
            if len(s) > 2:
                out.append(s)

    def _json_path(self, obj, path):
        if not path:
            return obj
        cur = obj
        for part in path.split("."):
            if cur is None:
                return None
            if isinstance(cur, list):
                try:
                    i = int(part)
                    cur = cur[i] if -len(cur) <= i < len(cur) else None
                except ValueError:
                    return None
            elif isinstance(cur, dict):
                cur = cur.get(part)
            else:
                return None
        return cur

    def _token_bucket_wait(self, host):
        wait = float(self.cfg.get("rate_limit_seconds", 0.5) or 0.5)
        if wait <= 0:
            return
        with self._rate_lock:
            last = self._rate_limit_map.get(host, 0)
            delta = time.time() - last
            if delta < wait:
                time.sleep(wait - delta)
            self._rate_limit_map[host] = time.time()

    def _user_rate_ok(self, uid, event=None):
        if uid is None:
            return True
        role = self._role_of(event) if event is not None else None
        per_role = (self.cfg.get("role_rate") or {}).get(role or "", 30)
        limit = int(per_role if per_role is not None else self.cfg.get("rate_limit_per_user", 30) or 30)
        if limit <= 0:
            return True
        now = time.time()
        with self._rate_lock:
            m = self.cfg.get("user_rate_map", {}) or {}
            bucket = m.get(str(uid), [])
            bucket = [t for t in bucket if now - t < 60]
            if len(bucket) >= limit:
                m[str(uid)] = bucket
                self.cfg.set("user_rate_map", m)
                return False
            bucket.append(now)
            m[str(uid)] = bucket
            if len(m) > 500:
                cutoff = now - 3600
                m = {k: v for k, v in m.items() if any(t > cutoff for t in (v or []))}
            self.cfg.set("user_rate_map", m)
        return True

    def _check_quota_pre(self, uid, action):
        quotas = self.cfg.get("trusted_quotas", {}) or {}
        per = quotas.get(str(uid))
        if not per:
            return True, None
        key = "daily_searches" if action == "search" else "daily_adds" if action in ("add", "add-api", "add-contrib") else None
        if not key:
            return True, None
        used = self.cfg.get("quota_used", {}) or {}
        today = time.strftime("%Y-%m-%d")
        bucket = used.get(str(uid)) or {}
        if bucket.get("date") != today:
            bucket = {"date": today, "counts": {}}
        counts = bucket.get("counts") or {}
        limit = int(per.get(key, 999999))
        cur = int(counts.get(key, 0))
        if cur >= limit:
            return False, f"daily quota exceeded ({cur}/{limit} {key})"
        return True, key

    def _check_quota_commit(self, uid, key):
        if not key:
            return
        used = self.cfg.get("quota_used", {}) or {}
        today = time.strftime("%Y-%m-%d")
        bucket = used.get(str(uid)) or {}
        if bucket.get("date") != today:
            bucket = {"date": today, "counts": {}}
        counts = bucket.get("counts") or {}
        counts[key] = int(counts.get(key, 0)) + 1
        bucket["counts"] = counts
        used[str(uid)] = bucket
        if len(used) > 500:
            used = {k: v for k, v in used.items() if v.get("date") == today}
        self.cfg.set("quota_used", used)

    def _check_quota(self, uid, action):
        ok, key = self._check_quota_pre(uid, action)
        if ok:
            self._check_quota_commit(uid, key)
        return ok, None if ok else f"quota exceeded"

    def _chat_allowed(self, event):
        allowed = self.cfg.get("allowed_chats", []) or []
        if not allowed:
            return True
        try:
            cid = event.chat_id
        except Exception:
            cid = None
        return cid in allowed

    def _user_blocked(self, event):
        blocked = self.cfg.get("blocked_users", []) or []
        sid = self._sender_id(event)
        return sid in blocked

    def _query_forbidden(self, query):
        bl = self.cfg.get("blocked_queries", []) or []
        low = self._normalize(query)
        for w in bl:
            try:
                if re.search(w, low):
                    return True
            except Exception:
                if self._normalize(w) in low:
                    return True
        return False

    def _proxies(self):
        if self.cfg.get("use_tor", False):
            p = self.cfg.get("tor_proxy")
            return {"http": p, "https": p}
        pool = self.cfg.get("proxies") or []
        if pool:
            p = random.choice(pool)
            return {"http": p, "https": p}
        return None

    def _cookie_for(self, domain):
        if not self.cfg.get("cookies_enabled", True):
            return None
        e = self._cookie_jar.get(domain)
        if not e:
            return None
        if e.get("expires", 0) < time.time():
            self._cookie_jar.pop(domain, None)
            return None
        return e

    def _save_cookie(self, domain, cookie, ua, proxy):
        if not self.cfg.get("cookies_enabled", True):
            return
        self._cookie_jar[domain] = {"cookie": cookie, "ua": ua, "proxy": proxy or "", "expires": time.time() + 3600 * 6}
        limit = int(self.cfg.get("cookie_jar_max", 500) or 500)
        if len(self._cookie_jar) > limit:
            items = sorted(self._cookie_jar.items(), key=lambda kv: kv[1].get("expires", 0))
            for k, _ in items[: len(items) // 2]:
                self._cookie_jar.pop(k, None)
        self._save_persistent_state()

    async def _http_request(self, url, headers=None, timeout=None, use_cookie=True):
        if not self._is_ssrf_safe(url):
            raise ValueError(f"unsafe url: {url[:100]}")
        ua = self._pick_ua(url)
        try:
            domain = urlparse(url).netloc.lower()
        except Exception:
            domain = ""
        cookie_header = None
        if use_cookie and domain:
            ck = self._cookie_for(domain)
            if ck:
                cookie_header = ck.get("cookie")
                if ck.get("ua"):
                    ua = ck["ua"]
        h = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Upgrade-Insecure-Requests": "1",
        }
        if cookie_header:
            h["Cookie"] = cookie_header
        if headers:
            h.update(headers)
        t = timeout or float(self.cfg.get("timeout", 12) or 12)
        max_bytes = int(self.cfg.get("max_bytes", 500_000) or 500_000)
        proxies = self._proxies()

        if _HAS_CURL and self.cfg.get("use_curl_cffi", True) and not proxies:
            try:
                async with _CurlSession() as session:
                    r = await session.get(url, headers=h, timeout=t, impersonate="chrome", allow_redirects=True)
                    try:
                        final_url = str(getattr(r, "url", "") or "")
                        if final_url and not self._is_ssrf_safe(final_url):
                            raise ValueError(f"unsafe redirect: {final_url[:100]}")
                    except ValueError:
                        raise
                    except Exception:
                        pass
                    try:
                        sc = r.cookies
                        if sc:
                            ck_str = "; ".join(f"{k}={v}" for k, v in sc.items())
                            if "cf_clearance" in ck_str.lower() and domain:
                                self._save_cookie(domain, ck_str, ua, None)
                    except Exception:
                        pass
                    return (r.text or "")[:max_bytes], r.status_code
            except ValueError:
                raise
            except Exception:
                pass

        if _HAS_HTTPX:
            try:
                proxy_arg = None
                if proxies:
                    proxy_arg = proxies.get("http")
                kwargs = {"http2": True, "timeout": t, "follow_redirects": True, "headers": h}
                if proxy_arg:
                    kwargs["proxy"] = proxy_arg
                try:
                    async with httpx.AsyncClient(**kwargs) as client:
                        r = await client.get(url)
                        final_url = str(r.url)
                        if final_url and not self._is_ssrf_safe(final_url):
                            raise ValueError(f"unsafe redirect: {final_url[:100]}")
                        return (r.text or "")[:max_bytes], r.status_code
                except TypeError:
                    kwargs.pop("proxy", None)
                    if proxy_arg:
                        kwargs["proxies"] = proxy_arg
                    async with httpx.AsyncClient(**kwargs) as client:
                        r = await client.get(url)
                        final_url = str(r.url)
                        if final_url and not self._is_ssrf_safe(final_url):
                            raise ValueError(f"unsafe redirect: {final_url[:100]}")
                        return (r.text or "")[:max_bytes], r.status_code
            except ValueError:
                raise
            except Exception:
                pass

        def _sync():
            req = Request(url, headers=h)
            opener = build_opener(ProxyHandler(proxies)) if proxies else build_opener()
            with opener.open(req, timeout=t) as resp:
                final_url = resp.geturl()
                raw = resp.read(max_bytes)
                cs = resp.headers.get_content_charset() or "utf-8"
                try:
                    text = raw.decode(cs, errors="ignore")
                except LookupError:
                    text = raw.decode("utf-8", errors="ignore")
                return text, resp.status, final_url

        text, status, final_url = await asyncio.to_thread(_sync)
        if final_url and not self._is_ssrf_safe(final_url):
            raise ValueError(f"unsafe redirect: {final_url[:100]}")
        return text, status

    async def _fetch_async(self, url):
        started = time.time()
        text, status = await self._http_request(url)
        return text, status, round(time.time() - started, 2)

    async def _fetch_json(self, url):
        text, status = await self._http_request(url, headers={"Accept": "application/json"})
        try:
            return json.loads(text), status
        except Exception:
            return None, status

    async def _fetch_with_jina(self, url, fmt="markdown"):
        if "jina" in self._dead_services:
            return ""
        jina_url = f"https://r.jina.ai/{url}"
        headers = {}
        if fmt == "text":
            headers["X-Return-Format"] = "text"
        elif fmt == "html":
            headers["X-Return-Format"] = "html"
        try:
            text, _ = await self._http_request(jina_url, headers=headers)
            if not text:
                self._dead_services.add("jina")
            return text
        except Exception:
            self._dead_services.add("jina")
            return ""

    async def _bypass_captcha(self, url):
        attempts = int(self.cfg.get("captcha_bypass_retries", 2) or 2)
        strategies = [
            ("retry_curl", lambda: self._http_request(url, headers={"Referer": f"https://{urlparse(url).netloc}/"})),
            ("retry_mobile", lambda: self._http_request(url, headers={"User-Agent": USER_AGENTS_BY_REGION["en"][0]})),
            ("jina_markdown", lambda: self._fetch_with_jina(url, "markdown")),
            ("jina_text", lambda: self._fetch_with_jina(url, "text")),
        ]
        for name, fn in strategies[: max(1, attempts) + 2]:
            try:
                r = await fn()
                text = r[0] if isinstance(r, tuple) else r
                if not text:
                    continue
                if self._is_cloudflare(text):
                    return None, "cloudflare_refused"
                if not self._is_captcha(text) and len(text) > 500:
                    return text, f"bypassed:{name}"
            except Exception:
                continue
        return None, "bypass_failed"

    def _ping(self, url):
        try:
            req = Request(url, headers={"User-Agent": self._pick_ua(url)})
            with urlopen(req, timeout=8) as r:
                body = r.read(65536)
                cs = r.headers.get_content_charset() or "utf-8"
                try:
                    text = body.decode(cs, errors="ignore")
                except LookupError:
                    text = body.decode("utf-8", errors="ignore")
                return not self._looks_blocked(text)
        except Exception:
            return False

    def _readability_extract(self, raw_html):
        if not self.cfg.get("readability_enabled", True):
            return None
        try:
            html_clean = re.sub(r"(?is)<script.*?</script>", " ", raw_html)
            html_clean = re.sub(r"(?is)<style.*?</style>", " ", html_clean)
            html_clean = re.sub(r"(?is)<nav.*?</nav>", " ", html_clean)
            html_clean = re.sub(r"(?is)<footer.*?</footer>", " ", html_clean)
            html_clean = re.sub(r"(?is)<header.*?</header>", " ", html_clean)
            html_clean = re.sub(r"(?is)<aside.*?</aside>", " ", html_clean)
            html_clean = re.sub(r"(?is)<form.*?</form>", " ", html_clean)
            blocks = re.findall(r"(?is)<(article|main|section|div|p)[^>]*>(.*?)</\1>", html_clean)
            scored = []
            for tag, content in blocks:
                txt = re.sub(r"(?s)<[^>]+>", " ", content)
                txt = html.unescape(txt)
                txt = re.sub(r"\s+", " ", txt).strip()
                if len(txt) < 100:
                    continue
                links = len(re.findall(r"(?i)<a\s", content))
                ps = len(re.findall(r"(?i)<p[\s>]", content))
                score = len(txt) - links * 30 + ps * 10
                if tag in ("article", "main"):
                    score += 200
                scored.append((score, txt))
            if not scored:
                return None
            scored.sort(key=lambda x: -x[0])
            top = " ".join(t for _, t in scored[:5])
            return top[:8000]
        except Exception:
            return None

    def _extract_title_fallback(self, html_raw, url, meta):
        for rx in (self._RX_OG_TITLE, self._RX_TW_TITLE):
            try:
                m = rx.search(html_raw)
                if m:
                    t = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
                    if t:
                        return t
            except Exception:
                continue
        try:
            m = self._RX_TITLE.search(html_raw)
            if m:
                t = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()
                t = re.sub(r"\s+", " ", t)
                if t:
                    return t
        except Exception:
            pass
        try:
            m = self._RX_H1.search(html_raw)
            if m:
                t = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).strip()
                if t:
                    return t
        except Exception:
            pass
        if meta.get("og_title"):
            return meta["og_title"]
        try:
            p = urlparse(url)
            path = p.path.strip("/")
            if path:
                last = path.split("/")[-1]
                last = re.sub(r"\.(?:html?|php|aspx?|jsp)$", "", last, flags=re.IGNORECASE)
                last = unquote(last).replace("_", " ").replace("-", " ").strip()
                if len(last) >= 3:
                    return last
            return p.netloc
        except Exception:
            return ""

    def _extract(self, source, base_url):
        raw = source
        readable = self._readability_extract(raw)
        source = re.sub(r"(?is)<script.*?</script>", " ", source)
        source = re.sub(r"(?is)<style.*?</style>", " ", source)
        source = re.sub(r"(?is)<noscript.*?</noscript>", " ", source)
        title = ""
        tm = re.search(r"(?is)<title[^>]*>(.*?)</title>", source)
        if tm:
            title = re.sub(r"<[^>]+>", " ", tm.group(1))
            title = html.unescape(title).strip()
        meta = self._extract_meta(raw)
        if not title:
            title = self._extract_title_fallback(raw, base_url, meta)
        text = re.sub(r"(?s)<[^>]+>", " ", source)
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        text = self._clean(text)
        if readable and len(readable) > len(text) * 0.4:
            text = readable + " || " + text[:3000]
        embedded = self._extract_embedded_json(raw)
        if embedded and len(text) < 500:
            extra = []
            for obj in embedded.values():
                self._flatten_json(obj, extra)
            if extra:
                text = text + " || " + " ".join(extra[:200])
        links = []
        for href in re.findall(r'''(?is)<a[^>]+href=["']([^"']+)["']''', source):
            try:
                full = urljoin(base_url, href)
                if urlparse(full).scheme in ("http", "https"):
                    links.append(full)
            except Exception:
                pass
        files = [l for l in links if re.search(r"\.(pdf|docx?|xlsx?|zip|rar|7z|txt|csv|json)$", l, re.I)]
        images = re.findall(r'''(?is)<img[^>]+src=["']([^"']+)["']''', source)
        images = [urljoin(base_url, i) for i in images[:20] if not i.startswith("data:")]
        links = list(dict.fromkeys(links))
        max_links = int(self.cfg.get("max_links", 50) or 50)
        return title, text, links[:max_links], files[:10], images[:10], meta

    def _build_url(self, site, query):
        template = site["url"]
        if "{query}" in template:
            return template.replace("{query}", quote_plus(query))
        param = site.get("param") or self._autodetect_param(template) or self.cfg.get("default_param", "q")
        sep = "&" if "?" in template else "?"
        return f"{template}{sep}{param}={quote_plus(query)}"

    def _autodetect_param(self, url):
        try:
            qs = urlparse(url).query
        except Exception:
            return None
        preferred = ("q", "query", "text", "search", "s", "keyword", "k", "wd", "word", "term", "find")
        for key in preferred:
            for pair in qs.split("&"):
                if "=" in pair:
                    k = pair.split("=", 1)[0]
                    if k == key:
                        return key
        return None

    def _apply_site_override(self, name, site):
        if not self.cfg.get("site_overrides", True):
            return site
        host = (site.get("host") or "").lower()
        for h, ov in SITE_URL_OVERRIDES.items():
            if h in host or host in h:
                ns = dict(site)
                ns["url"] = ov["url"]
                ns["param"] = ov.get("param", "q")
                ns["_override_note"] = ov.get("note", "")
                return ns
        return site

    def _highlight(self, escaped_text, query):
        if not self.cfg.get("highlight_matches", True):
            return escaped_text
        if not escaped_text or not query:
            return escaped_text
        norm_query = self._normalize(query)
        words = [w for w in self._RX_WORD.findall(norm_query) if len(w) > 1]
        if not words:
            return escaped_text
        pattern = r"(?<![\w])(?:" + "|".join(re.escape(html.escape(w)) for w in sorted(set(words), key=len, reverse=True)) + r")(?![\w])"
        try:
            return re.sub(pattern, lambda m: f"<b>{m.group(0)}</b>", escaped_text, flags=re.IGNORECASE | re.UNICODE)
        except Exception:
            return escaped_text

    def _safe_truncate(self, text, limit):
        if len(text) <= limit:
            return text
        cut = text[:limit]
        for tag in ("<b>", "</b>", "<i>", "</i>", "<code>", "</code>", "<pre>", "</pre>", "<blockquote>", "</blockquote>", "<u>", "</u>", "<s>", "</s>", "<tg-spoiler>", "</tg-spoiler>"):
            if cut.count(tag) % 2 != 0:
                cut = cut.rsplit(tag, 1)[0]
        depth = 0
        for m in re.finditer(r"</?(?:b|i|code|pre|blockquote|u|s|tg-spoiler)\b", cut):
            if m.group(0).startswith("</"):
                depth -= 1
            else:
                depth += 1
        while depth > 0:
            cut += "</blockquote>"
            depth -= 1
        return cut

    def _context_snippet(self, text, query, window=200, max_snippets=2):
        norm = self._lemmatize(text)
        words = [w for w in self._lemmatize(query).split() if len(w) > 1]
        if not words:
            return text[:700]
        positions = []
        for w in words:
            for m in re.finditer(re.escape(w), norm):
                positions.append(m.start())
                if len(positions) > 30:
                    break
        if not positions:
            return text[:700]
        positions.sort()
        snippets = []
        used_end = -1
        for pos in positions:
            if pos < used_end:
                continue
            start = max(0, pos - window)
            end = min(len(text), pos + window * 2)
            s = text[start:end].strip()
            for sw in STOPWORDS:
                s = re.sub(re.escape(sw), "", s, flags=re.IGNORECASE)
            snippets.append(s)
            used_end = end
            if len(snippets) >= max_snippets:
                break
        return " ... ".join(snippets) if snippets else text[:700]

    def _bm25_score(self, result, query, all_results, site):
        q_lemma = self._lemmatize(query)
        words = [w for w in q_lemma.split() if len(w) > 1]
        if not words:
            return 0.0
        text = self._lemmatize(result.get("snippet", ""))
        dl = len(text.split()) or 1
        lens = [len(self._lemmatize(r.get("snippet", "")).split()) for r in all_results]
        avgdl = max(1, sum(lens) / max(len(lens), 1))
        k1 = float(self.cfg.get("bm25_k1", 1.5) or 1.5)
        b = float(self.cfg.get("bm25_b", 0.75) or 0.75)
        N = max(1, len(all_results))
        score = 0.0
        for w in words:
            tf = text.count(w)
            if tf == 0:
                continue
            df = sum(1 for r in all_results if w in self._lemmatize(r.get("snippet", "")))
            idf = max(0.0, (N - df + 0.5) / (df + 0.5))
            idf = math.log(idf + 1) if idf > 0 else 0.0
            score += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
        priority_bonus = {"high": 0.3, "normal": 0.0, "low": -0.2}.get(site.get("priority", "normal"), 0.0)
        links_bonus = min(result.get("total_links", 0) / 100, 0.2)
        weight = float(site.get("weight", self.cfg.get("source_weight_default", 1.0)) or 1.0)
        return (score + priority_bonus + links_bonus) * weight

    def _parse_bool_ast(self, query):
        tokens = self._RX_TOKEN.findall(query)
        if not tokens:
            return None
        pos = [0]

        def peek():
            return tokens[pos[0]] if pos[0] < len(tokens) else None

        def consume():
            t = peek()
            pos[0] += 1
            return t

        def parse_or():
            left = parse_and()
            while peek() and peek().upper() == "OR":
                consume()
                right = parse_and()
                left = ("OR", left, right)
            return left

        def parse_and():
            left = parse_not()
            while True:
                nxt = peek()
                if nxt is None:
                    break
                if nxt.upper() == "OR" or nxt == ")":
                    break
                if nxt.upper() == "AND":
                    consume()
                right = parse_not()
                left = ("AND", left, right)
            return left

        def parse_not():
            if peek() and peek().upper() == "NOT":
                consume()
                return ("NOT", parse_not())
            return parse_atom()

        def parse_atom():
            t = peek()
            if t is None:
                return ("LEAF", "")
            if t == "(":
                consume()
                node = parse_or()
                if peek() == ")":
                    consume()
                return node
            consume()
            if t.startswith('"') and t.endswith('"'):
                return ("LEAF", t[1:-1])
            if t.startswith("+"):
                return ("LEAF", t[1:])
            if t.startswith("-"):
                return ("NOT", ("LEAF", t[1:]))
            return ("LEAF", t)

        try:
            return parse_or()
        except Exception:
            return None

    def _eval_bool_ast(self, node, text):
        if node is None:
            return True
        op = node[0]
        if op == "LEAF":
            w = self._lemmatize(node[1])
            if not w:
                return True
            txt = self._lemmatize(text)
            for part in w.split():
                if part and part not in txt:
                    return False
            return True
        if op == "AND":
            return self._eval_bool_ast(node[1], text) and self._eval_bool_ast(node[2], text)
        if op == "OR":
            return self._eval_bool_ast(node[1], text) or self._eval_bool_ast(node[2], text)
        if op == "NOT":
            return not self._eval_bool_ast(node[1], text)
        return True

    def _parse_boolean(self, query):
        ops = {"include": [], "exclude": [], "site": None, "filetype": None, "intitle": None, "phrase": None, "wildcards": [], "fuzzy": [], "ast": None}
        if not self.cfg.get("operators_enabled", True):
            return query, ops
        phrase_m = self._RX_QUOTED.search(query)
        if phrase_m:
            ops["phrase"] = phrase_m.group(1)
            query = self._RX_QUOTED.sub(" ", query, count=1).strip()
        for m in re.finditer(r'(?:^|\s)(site|filetype|intitle):(\S+)', query):
            ops[m.group(1)] = m.group(2)
            query = query.replace(m.group(0), " ")
        wildcards = self._RX_WILDCARD.findall(query)
        if wildcards:
            ops["wildcards"] = wildcards
        fuzzy = self._RX_FUZZY.findall(query)
        if fuzzy:
            ops["fuzzy"] = fuzzy
        if self.cfg.get("boolean_operators_enabled", True):
            ast = self._parse_bool_ast(query)
            if ast is not None:
                ops["ast"] = ast
        tokens = query.split()
        cleaned = []
        for t in tokens:
            if t.startswith("+") and len(t) > 1:
                ops["include"].append(t[1:])
            elif t.startswith("-") and len(t) > 1:
                ops["exclude"].append(t[1:])
            elif t.startswith("~") and len(t) > 1:
                continue
            elif t.endswith("*") and len(t) > 1:
                continue
            elif t.upper() in ("AND", "OR", "NOT"):
                continue
            else:
                cleaned.append(t)
        return " ".join(cleaned).strip(), ops

    def _apply_synonyms(self, query):
        syn = self.cfg.get("synonyms", {}) or {}
        if not syn:
            return query
        out = [query]
        for w in self._RX_WORD.findall(query):
            for k, vals in syn.items():
                if w.lower() == k.lower() and isinstance(vals, list):
                    out.extend(vals)
        return " ".join(dict.fromkeys(out))

    def _apply_wildcards(self, results, wildcards):
        if not wildcards:
            return results
        out = []
        for r in results:
            txt = self._lemmatize((r.get("snippet") or "") + " " + (r.get("title") or ""))
            ok = True
            for wc in wildcards:
                prefix_words = self._lemmatize(wc).split()
                if not prefix_words:
                    continue
                p = prefix_words[0][:max(2, len(prefix_words[0]) - 1)]
                if not any(w.startswith(p) for w in txt.split()):
                    ok = False
                    break
            if ok:
                out.append(r)
        return out

    def _apply_fuzzy(self, results, fuzzy):
        if not fuzzy:
            return results
        out = []
        for r in results:
            txt = self._lemmatize((r.get("snippet") or "") + " " + (r.get("title") or ""))
            words = set(txt.split())
            ok = True
            for fw in fuzzy:
                fl = self._lemmatize(fw)
                found = False
                for w in words:
                    if abs(len(w) - len(fl)) > 2:
                        continue
                    if difflib.SequenceMatcher(None, w, fl).ratio() >= 0.8:
                        found = True
                        break
                if not found:
                    ok = False
                    break
            if ok:
                out.append(r)
        return out

    def _apply_operators_filter(self, results, ops):
        filtered = []
        for r in results:
            if ops["site"] and ops["site"].lower() not in r.get("url", "").lower():
                continue
            if ops["filetype"]:
                exts = [e.strip().lstrip(".").lower() for e in ops["filetype"].split(",") if e.strip()]
                if exts:
                    hit = False
                    for ext in exts:
                        dot = "." + ext
                        if any(dot in (f or "").lower() for f in r.get("files", [])):
                            hit = True
                            break
                        if dot in (r.get("url") or "").lower():
                            hit = True
                            break
                    if not hit:
                        continue
            if ops["intitle"]:
                if ops["intitle"].lower() not in (r.get("title") or "").lower():
                    continue
            txt = self._lemmatize((r.get("snippet") or "") + " " + (r.get("title") or ""))
            if ops["phrase"] and self._lemmatize(ops["phrase"]) not in txt:
                continue
            if any(self._lemmatize(w) not in txt for w in ops["include"]):
                continue
            if any(self._lemmatize(w) in txt for w in ops["exclude"]):
                continue
            if ops.get("ast") is not None:
                if not self._eval_bool_ast(ops["ast"], txt):
                    continue
            filtered.append(r)
        filtered = self._apply_wildcards(filtered, ops.get("wildcards") or [])
        filtered = self._apply_fuzzy(filtered, ops.get("fuzzy") or [])
        return filtered

    def _dedup_difflib(self, results):
        thr = float(self.cfg.get("dedup_threshold", 0.85) or 0.85)
        out = []
        for r in sorted(results, key=lambda x: -len(x.get("snippet") or "")):
            dup = False
            r_len = len(r.get("snippet") or "")
            for o in out:
                o_len = len(o.get("snippet") or "")
                if o_len and abs(r_len - o_len) / max(r_len, o_len, 1) > 0.5:
                    continue
                ratio = difflib.SequenceMatcher(None, r.get("snippet", "")[:400], o.get("snippet", "")[:400]).ratio()
                if ratio >= thr:
                    dup = True
                    break
            if not dup:
                out.append(r)
        return out

    def _extract_entities(self, text):
        if not self.cfg.get("entities_enabled", True):
            return {}
        found = {}
        for name, rx in ENTITY_PATTERNS.items():
            matches = list(dict.fromkeys(rx.findall(text)))
            if matches:
                found[name] = matches[:10]
        return found

    def _cache_key(self, query, actor=None, chat_id=None):
        payload = query
        if actor is not None:
            payload = f"{actor}|{payload}"
        if chat_id is not None:
            payload = f"{chat_id}|{payload}"
        return hashlib.sha1(payload.encode("utf-8", errors="ignore")).hexdigest()

    def _cache_get(self, query, actor=None, chat_id=None):
        ttl = int(self.cfg.get("cache_ttl", 300) or 300)
        if ttl <= 0:
            return None
        k = self._cache_key(query, actor, chat_id)
        e = self._cache.get(k)
        if not e:
            return None
        if time.time() - e["ts"] > ttl:
            del self._cache[k]
            return None
        return e["data"]

    def _cache_set(self, query, data, actor=None, chat_id=None):
        ttl = int(self.cfg.get("cache_ttl", 300) or 300)
        if ttl <= 0:
            return
        self._cache[self._cache_key(query, actor, chat_id)] = {"ts": time.time(), "data": data}
        if len(self._cache) > 1000:
            now = time.time()
            self._cache = {k: v for k, v in self._cache.items() if now - v["ts"] < ttl * 2}
            if len(self._cache) > 1000:
                items = sorted(self._cache.items(), key=lambda kv: kv[1]["ts"])
                for k, _ in items[: len(items) // 2]:
                    self._cache.pop(k, None)

    def _run_hook_ignore_errors(self, hook_name, ctx):
        for fn in self._hooks.get(hook_name, []):
            try:
                r = fn(ctx)
                if asyncio.iscoroutine(r):
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(r)
                    except RuntimeError:
                        pass
            except Exception:
                continue

    async def _run_hook(self, hook_name, ctx):
        for fn in self._hooks.get(hook_name, []):
            try:
                plugin_info = None
                fn_module = getattr(fn, "__module__", None)
                for name, info in self._plugins.items():
                    mod = info.get("module")
                    if mod is not None and getattr(mod, "__name__", None) == fn_module:
                        plugin_info = info
                        break
                enriched = dict(ctx)
                if plugin_info is not None:
                    trust = plugin_info.get("trust_level", "sandboxed")
                    access = set(plugin_info.get("access") or [])
                    enriched["trust_level"] = trust
                    if plugin_info.get("enabled") is False:
                        continue
                    if "module" in access and trust in ("trusted", "privileged"):
                        enriched["module"] = self
                        enriched["trusted_module"] = self
                    if trust == "privileged":
                        enriched["kernel"] = getattr(self, "kernel", None)
                        enriched["cfg"] = self.cfg
                        enriched["logger"] = self.log
                    self._check_plugin_quota(plugin_info)
                r = fn(enriched)
                if asyncio.iscoroutine(r):
                    r = await r
                if r is not None:
                    return r
            except Exception as e:
                try:
                    self.log.warning(f"[DontDoThat] hook {hook_name} failed: {e}")
                except Exception:
                    pass
                continue
        return None

    def _check_plugin_quota(self, plugin_info):
        limit = int(self.cfg.get("plugin_quota_per_minute", 60) or 60)
        if limit <= 0:
            return
        key = plugin_info.get("name") or "?"
        now = time.time()
        bucket = self._plugin_quota.get(key, [])
        bucket = [t for t in bucket if now - t < 60]
        if len(bucket) >= limit:
            raise RuntimeError(f"plugin quota exceeded: {key}")
        bucket.append(now)
        self._plugin_quota[key] = bucket

    def _extract_url_from_text(self, text):
        if not text:
            return ""
        m = self._RX_URL.search(text)
        if m:
            url = m.group(0)
        else:
            bm = self._RX_BARE_URL.search(text)
            if bm:
                url = "https://" + bm.group(1)
            else:
                url = text.strip()
        url = url.rstrip(".,;:!?")
        if len(url) >= 2 and url[0] in "<([{" and url[-1] in ">)]}":
            pairs = {"<": ">", "(": ")", "[": "]", "{": "}"}
            if pairs.get(url[0]) == url[-1]:
                url = url[1:-1].strip()
        return url

    def _parse_flags(self, tail):
        flags = {}
        for m in self._RX_FLAG.finditer(tail):
            key = m.group(1)
            val = m.group(2) or m.group(3) or m.group(4)
            if val is None:
                val = True
            flags[key] = val
        cleaned = self._RX_FLAG.sub("", tail).strip()
        return cleaned, flags

    def _unwrap_ddg(self, url):
        if not url:
            return url
        m = self._RX_DDG_REDIRECT.match(url)
        if not m:
            m = self._RX_DDG_REDIRECT_INLINE.search(url)
        if not m:
            return url
        try:
            return unquote(m.group(1))
        except Exception:
            return url

    def _unwrap_ddg_in_html(self, html_text):
        if not html_text or "uddg=" not in html_text:
            return html_text
        try:
            return self._RX_DDG_REDIRECT_INLINE.sub(lambda m: unquote(m.group(1)), html_text)
        except Exception:
            return html_text

    async def _log_search(self, event, query):
        if not self.cfg.get("log_searches", False):
            return
        try:
            cid = getattr(self.kernel, "log_chat_id", None)
            if not cid:
                return
            s = getattr(event, "sender_id", "?")
            await self.kernel.log_to_chat(f"🔍 <b>DontDoThat</b>: <code>{html.escape(str(s))}</code> → <code>{html.escape(query)}</code>")
        except Exception:
            pass

    def _plugins_dir(self):
        d = Path(self.cfg.get("plugins_dir", "data/dontdothat_plugins"))
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _file_sha256(self, path):
        try:
            h = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def _resolve_trust_level(self, reg_name, meta, source="local"):
        overrides = self.cfg.get("plugin_trust_overrides", {}) or {}
        if reg_name in overrides:
            return overrides[reg_name]
        declared = str(meta.get("name", reg_name)).lower().replace(" ", "_")
        if declared in overrides:
            return overrides[declared]
        author = str(meta.get("author") or "").strip().lstrip("@")
        if not author:
            return "sandboxed"
        trusted_authors = [a.lstrip("@") for a in (self.cfg.get("trusted_plugin_authors") or [])]
        priv_authors = [a.lstrip("@") for a in (self.cfg.get("privileged_plugin_authors") or [])]
        if author in priv_authors:
            return "privileged"
        if author in trusted_authors:
            if source == "repo":
                repos = self.cfg.get("trusted_plugin_repos") or []
                repo = self.cfg.get("plugins_repo", "")
                if repos and repo not in repos:
                    return "sandboxed"
            return "trusted"
        if source == "repo":
            repos = self.cfg.get("trusted_plugin_repos") or []
            repo = self.cfg.get("plugins_repo", "")
            if repo and repo in repos:
                return "trusted"
        return "sandboxed"

    def _register_plugin_hooks(self, reg_name, module_obj, trust_level="sandboxed"):
        meta = getattr(module_obj, "PLUGIN", None)
        if not isinstance(meta, dict):
            raise ValueError("PLUGIN dict missing")
        declared_access = set(meta.get("access") or [])
        allowed_access = {
            "sandboxed": set(),
            "trusted": {"module"},
            "privileged": {"module", "kernel", "cfg"},
        }.get(trust_level, set())
        forbidden = declared_access - allowed_access
        if forbidden:
            raise ValueError(f"plugin declares access {forbidden} but trust_level={trust_level}")
        hooks = meta.get("hooks") or []
        registered = []
        missing = []
        for h in hooks:
            fn = getattr(module_obj, h, None)
            if callable(fn):
                self._hooks.setdefault(h, []).append(fn)
                registered.append(h)
            else:
                missing.append(h)
        self._plugins[reg_name] = {
            "name": meta.get("name", reg_name),
            "declared_name": meta.get("name", reg_name),
            "version": meta.get("version", "?"),
            "author": meta.get("author", "?"),
            "description": meta.get("description", ""),
            "min_core": meta.get("min_core", ""),
            "tags": meta.get("tags") or [],
            "access": list(declared_access),
            "trust_level": trust_level,
            "hooks": registered,
            "missing_hooks": missing,
            "module": module_obj,
            "enabled": True,
            "path": str(self._plugins_dir() / f"{reg_name}.py"),
        }

    def _unregister_plugin_hooks(self, name):
        info = self._plugins.get(name)
        if not info:
            return
        mod = info.get("module")
        mn = getattr(mod, "__name__", None)
        for hn, handlers in self._hooks.items():
            self._hooks[hn] = [h for h in handlers if not (mn and getattr(h, "__module__", None) == mn)]
        self._plugins.pop(name, None)
        if mn:
            sys.modules.pop(mn, None)
        self._plugin_quota.pop(name, None)
        try:
            self._run_hook_ignore_errors("on_plugin_unload", {"name": name})
        except Exception:
            pass

    async def _load_plugin_from_path(self, path, forced_name=None, source="local"):
        import importlib.util
        stem = path.stem
        try:
            spec = importlib.util.spec_from_file_location(f"ddt_plugin_{stem}", path)
            if spec is None or spec.loader is None:
                return False, "spec failed", {}
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            return False, f"exec failed: {e}", {}
        meta = getattr(mod, "PLUGIN", None)
        if not isinstance(meta, dict):
            return False, "PLUGIN dict missing", {}
        declared = str(meta.get("name") or "").strip()
        if not declared:
            return False, "PLUGIN.name missing", {}
        min_core = str(meta.get("min_core") or "").strip()
        if min_core:
            try:
                from core.tetko.version_utils import compare_versions
                if compare_versions(min_core, self.version) > 0:
                    return False, f"requires core >= {min_core}, have {self.version}", {}
            except Exception:
                pass
        reg_name = declared.lower().replace(" ", "_")
        if forced_name:
            reg_name = forced_name.lower().replace(" ", "_")
        if reg_name in self._plugins:
            self._unregister_plugin_hooks(reg_name)
        trust_level = self._resolve_trust_level(reg_name, meta, source=source)
        try:
            self._register_plugin_hooks(reg_name, mod, trust_level=trust_level)
        except Exception as e:
            return False, f"register failed: {e}", {}
        info = self._plugins.get(reg_name, {})
        info["file_stem"] = stem
        info["path"] = str(path)
        info["description"] = str(meta.get("description") or "").strip()
        info["declared_name"] = declared
        info["trust_level"] = trust_level
        info["source"] = source
        info["sha256"] = self._file_sha256(path)
        info["loaded_at"] = time.time()
        self._plugins[reg_name] = info
        self._run_hook_ignore_errors("on_plugin_load", {"name": reg_name, "trust": trust_level})
        return True, reg_name, info

    def _set_plugin_trust(self, reg_name, level):
        if level not in ("sandboxed", "trusted", "privileged"):
            return False
        info = self._plugins.get(reg_name)
        if not info:
            return False
        mod = info.get("module")
        if mod is None:
            return False
        prev_path = info.get("path")
        prev_stem = info.get("file_stem")
        prev_source = info.get("source", "local")
        prev_sha = info.get("sha256")
        self._unregister_plugin_hooks(reg_name)
        try:
            self._register_plugin_hooks(reg_name, mod, trust_level=level)
        except Exception as e:
            self.log.warning(f"[DontDoThat] failed to re-register {reg_name}: {e}")
            return False
        info2 = self._plugins.get(reg_name) or {}
        info2["path"] = prev_path
        info2["file_stem"] = prev_stem
        info2["source"] = prev_source
        info2["sha256"] = prev_sha
        self._plugins[reg_name] = info2
        overrides = self.cfg.get("plugin_trust_overrides", {}) or {}
        overrides[reg_name] = level
        self.cfg.set("plugin_trust_overrides", overrides)
        return True

    async def _install_plugin_from_reply(self, event, forced_name=None):
        reply = None
        try:
            reply = await event.get_reply_message()
        except Exception:
            reply = None
        if reply is None:
            return False, "reply to a .py file", {}
        fname = None
        doc = getattr(reply, "document", None)
        if doc is not None:
            for a in getattr(doc, "attributes", []) or []:
                n = getattr(a, "file_name", None)
                if n:
                    fname = n
                    break
        if not fname or not fname.endswith(".py"):
            return False, "file must be .py", {}
        try:
            data = await reply.download_media(bytes)
        except Exception as e:
            return False, f"download failed: {e}", {}
        try:
            import ast
            import tokenize
            import io as _io
            buf = _io.BytesIO(data)
            try:
                encoding, _ = tokenize.detect_encoding(buf.readline)
            except Exception:
                encoding = "utf-8"
            try:
                src = data.decode(encoding, errors="strict")
            except Exception:
                src = data.decode("utf-8", errors="ignore")
            ast.parse(src)
        except SyntaxError as e:
            return False, f"syntax error: {e}", {}
        new_stem = Path(fname).stem
        existing_key = None
        for k, v in list(self._plugins.items()):
            if v.get("file_stem", "") == new_stem:
                existing_key = k
                break
            if str(v.get("declared_name") or v.get("name") or "").lower() == new_stem.lower():
                existing_key = k
                break
        update_mode = existing_key is not None
        old_version = None
        old_path = None
        if update_mode:
            oi = self._plugins.get(existing_key) or {}
            old_version = oi.get("version")
            old_path = oi.get("path")
            self._unregister_plugin_hooks(existing_key)
        target = self._plugins_dir() / fname
        target.write_bytes(data)
        if update_mode and old_path and Path(old_path) != target:
            try:
                Path(old_path).unlink()
            except Exception:
                pass
        ok, reg_name, info = await self._load_plugin_from_path(target, forced_name=forced_name, source="local")
        if not ok:
            try:
                target.unlink()
            except Exception:
                pass
            return False, reg_name, {}
        info["_was_update"] = update_mode
        info["_old_version"] = old_version
        return True, reg_name, info

    def _find_plugin(self, raw_name):
        norm = raw_name.lower().replace(" ", "_")
        if norm in self._plugins:
            return norm
        for k, v in self._plugins.items():
            if k.lower() == raw_name.lower():
                return k
            dn = str(v.get("declared_name") or v.get("name") or "")
            if dn.lower() == raw_name.lower() or dn.lower().replace(" ", "_") == norm:
                return k
        return None

    def _repo_url(self, path):
        repo = self.cfg.get("plugins_repo", "flexOwnerAL/dontdothat-plugins")
        branch = self.cfg.get("plugins_repo_branch", "main")
        return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"

    async def _repo_index(self, force=False):
        ttl = int(self.cfg.get("plugins_index_ttl", 3600) or 3600)
        now = time.time()
        if not force and self._repo_index_cache and now - self._repo_index_cache.get("ts", 0) < ttl:
            return self._repo_index_cache.get("data")
        url = self._repo_url(self.cfg.get("plugins_index_path", "index.json"))
        try:
            text, _ = await self._http_request(url, headers={"Accept": "application/json"})
            data = json.loads(text)
            self._repo_index_cache = {"ts": now, "data": data}
            return data
        except Exception:
            return self._repo_index_cache.get("data")

    async def _repo_fetch_plugin(self, file_path):
        url = self._repo_url(file_path)
        try:
            text, _ = await self._http_request(url)
            return text
        except Exception:
            return None

    async def _repo_install(self, name, trust_override=None):
        data = await self._repo_index()
        if not data or not isinstance(data.get("plugins"), list):
            return False, "repo index unavailable"
        entry = None
        for p in data["plugins"]:
            if p.get("name", "").lower() == name.lower():
                entry = p
                break
        if entry is None:
            return False, "not found in repo"
        file_path = entry.get("file")
        if not file_path:
            return False, "no file field"
        content = await self._repo_fetch_plugin(file_path)
        if not content:
            return False, "download failed"
        expected = entry.get("sha256") or ""
        actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if expected and actual != expected:
            return False, f"sha256 mismatch ({actual[:8]} vs {expected[:8]})"
        if self.cfg.get("require_signed_plugins") and not expected:
            return False, "unsigned plugin rejected"
        min_core = entry.get("min_core", "")
        if min_core:
            try:
                from core.tetko.version_utils import compare_versions
                if compare_versions(min_core, self.version) > 0:
                    return False, f"requires core >= {min_core}"
            except Exception:
                pass
        try:
            import ast
            ast.parse(content)
        except SyntaxError as e:
            return False, f"syntax error: {e}"
        target = self._plugins_dir() / f"{entry.get('name', name)}.py"
        target.write_text(content, encoding="utf-8")
        ok, reg_name, info = await self._load_plugin_from_path(target, source="repo")
        if not ok:
            return False, reg_name
        if trust_override:
            self._set_plugin_trust(reg_name, trust_override)
        info["sha256"] = actual
        info["repo_entry"] = entry
        return True, info

    async def _repo_update(self, name=None):
        data = await self._repo_index()
        if not data:
            return []
        updated = []
        for p in data.get("plugins", []):
            pname = p.get("name")
            key = self._find_plugin(pname or "")
            if not key:
                continue
            if name and pname.lower() != name.lower():
                continue
            installed = self._plugins[key]
            cur = installed.get("version", "?")
            new = p.get("version", "?")
            if cur == new:
                continue
            ok, res = await self._repo_install(pname)
            if ok:
                updated.append((pname, cur, new))
        return updated

    async def _respond(self, event, text, **kwargs):
        try:
            if getattr(event, "out", None) is True:
                try:
                    return await event.edit(text, **kwargs)
                except Exception as e:
                    try:
                        self.log.debug(f"[DontDoThat] _respond edit failed: {e}")
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            return await event.respond(text, **kwargs)
        except Exception as e:
            try:
                self.log.debug(f"[DontDoThat] _respond respond failed: {e}")
            except Exception:
                pass
        try:
            return await event.reply(text, **kwargs)
        except Exception as e:
            try:
                self.log.debug(f"[DontDoThat] _respond reply failed: {e}")
            except Exception:
                pass
        return None

    async def _send_result(self, event, query, ok, err, page=0, original_message=None):
        if not ok:
            await self._respond(event, self._no_result_text(err), parse_mode="html")
            return
        text, total = self._format_results(query, ok, page=page)
        self._last_result = {"query": query, "ok": ok, "err": err, "ts": time.time()}
        await self._respond(event, text, parse_mode="html")

    async def _notify_owner_trusted(self, event, action, details=""):
        if not self.cfg.get("notify_owner_on_trusted", True):
            return
        try:
            owner_id = getattr(self.kernel.context, "admin_id", None)
            if not owner_id:
                return
            sid = self._sender_id(event)
            await event.client.send_message(owner_id, f"🔔 <b>trusted action</b>\n<b>user:</b> <code>{sid}</code>\n<b>action:</b> {html.escape(action)}\n<b>details:</b> <code>{html.escape(details[:200])}</code>", parse_mode="html")
        except Exception:
            pass

    def _backup_path(self):
        return Path(f"data/dontdothat_backup_{int(time.time())}.json")

    def _encrypt_data(self, raw: bytes) -> bytes:
        key = self.cfg.get("backup_encryption_key") or ""
        if not key:
            return raw
        try:
            from cryptography.fernet import Fernet
            import base64
            k = hashlib.sha256(key.encode()).digest()
            fkey = base64.urlsafe_b64encode(k)
            return Fernet(fkey).encrypt(raw)
        except Exception as e:
            try:
                self.log.warning(f"[DontDoThat] backup encryption failed: {e}")
            except Exception:
                pass
            return raw

    def _decrypt_data(self, raw: bytes) -> bytes:
        key = self.cfg.get("backup_encryption_key") or ""
        if not key:
            return raw
        try:
            from cryptography.fernet import Fernet
            import base64
            k = hashlib.sha256(key.encode()).digest()
            fkey = base64.urlsafe_b64encode(k)
            return Fernet(fkey).decrypt(raw)
        except Exception as e:
            try:
                self.log.warning(f"[DontDoThat] backup decryption failed: {e}")
            except Exception:
                pass
            return raw

    def _build_backup(self):
        return {
            "version": self.version,
            "ts": time.time(),
            "sites": self._sites(),
            "roles": self.cfg.get("roles", {}),
            "notes": self.cfg.get("notes", {}),
            "saved_results": self.cfg.get("saved_results", {}),
            "synonyms": self.cfg.get("synonyms", {}),
            "templates": self.cfg.get("templates", {}),
            "watchers": self.cfg.get("watchers", []),
            "blocked_queries": self.cfg.get("blocked_queries", []),
            "blocked_users": self.cfg.get("blocked_users", []),
            "allowed_chats": self.cfg.get("allowed_chats", []),
            "plugin_trust_overrides": self.cfg.get("plugin_trust_overrides", {}),
            "trusted_plugin_authors": self.cfg.get("trusted_plugin_authors", []),
            "privileged_plugin_authors": self.cfg.get("privileged_plugin_authors", []),
            "plugins_metadata": self.cfg.get("plugins_metadata", {}),
            "stats": self._stats,
            "history": self._history[-200:],
        }

    async def _watch_runner_once(self, wid=None):
        watchers = self.cfg.get("watchers") or []
        now = time.time()
        changed = False
        for w in watchers:
            if wid and w.get("id") != wid:
                continue
            if not wid and w.get("next_run", 0) > now:
                continue
            q = w.get("query")
            if not q:
                w["next_run"] = now + int(w.get("interval", 3600))
                changed = True
                continue
            try:
                ok, err = await self._search_everywhere(q, actor="watcher")
            except Exception:
                ok, err = [], []
                w["next_run"] = now + max(60, int(w.get("interval", 3600)) * 2)
            else:
                w["next_run"] = now + int(w.get("interval", 3600))
            changed = True
            seen = set(w.get("seen") or [])
            if w.get("new_only"):
                new = [r for r in ok if r["url"] not in seen]
            else:
                new = ok
            for r in ok:
                seen.add(r["url"])
            w["seen"] = list(seen)[-500:]
            if new:
                try:
                    cid = getattr(self.kernel, "log_chat_id", None)
                    if cid:
                        text, _ = self._format_results(q, new)
                        await self.kernel.client.send_message(cid, text, parse_mode="html")
                except Exception:
                    pass
        if changed:
            self.cfg.set("watchers", watchers)

    def _latency_percentiles(self):
        out = {}
        for src, arr in (self._stats.get("latency") or {}).items():
            if not arr:
                continue
            s = sorted(arr)
            n = len(s)
            out[src] = {
                "p50": s[int(n * 0.5)] if n > 0 else 0,
                "p95": s[min(int(n * 0.95), n - 1)] if n > 0 else 0,
                "p99": s[min(int(n * 0.99), n - 1)] if n > 0 else 0,
                "avg": round(sum(s) / n, 3),
                "n": n,
            }
        return out

    def _format_results(self, query, results, page=0):
        maxd = int(self.cfg.get("max_sources_display", 10) or 10)
        total = max(1, (len(results) + maxd - 1) // maxd)
        page = max(0, min(page, total - 1))
        chunk = results[page * maxd:(page + 1) * maxd]
        p = self._prefix()
        out = [
            "<blockquote><b>some founded!!</b></blockquote>",
            f"<b>target:</b> <code>{html.escape(query)}</code>",
            f"<b>sources hit:</b> <code>{len(results)}</code>",
            f"<b>page:</b> <code>{page + 1}/{total}</code>",
        ]
        if total > 1:
            nav = []
            if page > 0:
                nav.append(f"{p}dothat page {page} {query}")
            if page + 1 < total:
                nav.append(f"{p}dothat page {page + 2} {query}")
            if nav:
                out.append("<i>next: " + " | ".join(f"<code>{html.escape(n)}</code>" for n in nav) + "</i>")
        out.append("")
        for r in chunk:
            badges = []
            if r.get("bypass"):
                badges.append(f"bypass:{r['bypass']}")
            if r.get("fallback"):
                badges.append(f"fallback:{r['fallback']}")
            if r.get("override"):
                badges.append(f"override:{r['override']}")
            bs = f" <i>({', '.join(badges)})</i>" if badges else ""
            snip = self._safe_truncate(r.get("snippet_hl") or "", 700)
            out.append(
                "<blockquote>"
                f"<b>{html.escape(r['name'])}</b> <i>(score {r.get('score', 0):.2f}, {r.get('elapsed', 0)}s)</i>{bs}\n"
                f"<b>title:</b> {html.escape(r['title'])}\n"
                f"<b>url:</b> <code>{html.escape(r['url'][:300])}</code>\n"
                f"<b>matches:</b> <code>{r['matches']}</code> | <b>links:</b> <code>{r['total_links']}</code>\n"
                f"<i>{snip}</i>"
                "</blockquote>"
            )
            if r.get("entities"):
                lines = []
                for k, vs in r["entities"].items():
                    lines.append(f"  <b>{k}:</b> {', '.join(html.escape(v) for v in vs[:5])}")
                if lines:
                    out.append("<b>entities:</b>\n" + "\n".join(lines))
            if r.get("meta"):
                m = r["meta"]
                meta_bits = []
                for k in ("author", "date", "og_title", "canonical"):
                    if m.get(k):
                        meta_bits.append(f"{k}={html.escape(str(m[k])[:80])}")
                if meta_bits:
                    out.append("<b>meta:</b> " + " | ".join(meta_bits))
            if r.get("files"):
                out.append("<b>📎 files:</b>")
                for f in r["files"][:3]:
                    out.append(f"• <code>{html.escape(f[:200])}</code>")
            if r.get("links"):
                out.append("<b>related stuff:</b>")
                for l in r["links"][:5]:
                    out.append(f"• <code>{html.escape(l[:200])}</code>")
            out.append("")
        return "\n".join(out), total

    def _no_result_text(self, errors):
        if errors:
            lines = ["<blockquote><b>all sources failed 💀</b>"]
            for e in errors[:8]:
                lines.append(f"• <code>{html.escape(e.get('__error__', '?'))}</code>: <i>{html.escape((e.get('error') or '')[:120])}</i>")
            lines.append("<i>tips: .dothat cfg use_tor false | .dothat cfg proxies []</i>")
            lines.append("</blockquote>")
            return "\n".join(lines)
        return "<blockquote><b>no information..</b></blockquote>"

    def _usage(self):
        p = html.escape(self._prefix())
        return f"<blockquote><b>DontDoThat v{self.version}</b>\n<code>{p}dothat help</code> — full reference\n<code>{p}dothat &lt;query&gt;</code> — quick search</blockquote>"

    def _help_main(self, p):
        return (
            "<blockquote><b>DontDoThat help</b>\n"
            f"<code>{p}dothat help search</code> — search syntax\n"
            f"<code>{p}dothat help sources</code> — manage sources\n"
            f"<code>{p}dothat help diag</code> — diagnostics\n"
            f"<code>{p}dothat help plugins</code> — plugins\n"
            f"<code>{p}dothat help trust</code> — plugin trust system\n"
            f"<code>{p}dothat help roles</code> — roles + trust\n"
            f"<code>{p}dothat help service</code> — service commands\n"
            f"<code>{p}dothat help operators</code> — search operators\n"
            f"<code>{p}dothat help commands [role]</code> — commands by role\n"
            "</blockquote>"
        )

    def _help_search(self, p):
        return (
            "<blockquote><b>🔍 search</b>\n"
            f"<code>{p}dothat &lt;query&gt;</code> — search all\n"
            f"<code>{p}dothat all &lt;query&gt;</code> — ignore priority\n"
            f"<code>{p}dothat fast &lt;query&gt;</code> — high priority only\n"
            f"<code>{p}dothat deep &lt;query&gt;</code> — deep + snapshots\n"
            f"<code>{p}dothat multi q1 | q2 | q3</code> — batch\n"
            f"<code>{p}dothat search &lt;name&gt; &lt;query&gt;</code> — one source\n"
            f"<code>{p}dothat @source &lt;query&gt;</code> — one source\n"
            f"<code>{p}dothat @s1,@s2 &lt;query&gt;</code> — multiple sources\n"
            f"<code>{p}dothat raw &lt;name&gt; &lt;query&gt;</code> — raw html\n"
            f"<code>{p}dothat trace &lt;query&gt;</code> — step by step\n"
            f"<code>{p}dothat profile &lt;query&gt;</code> — timing\n"
            f"<code>{p}dothat page &lt;n&gt; &lt;query&gt;</code> — page n\n"
            f"<code>{p}dothat openall</code> — send all urls\n"
            f"<code>{p}dothat json</code> — download json\n"
            f"<code>{p}dothat save [--tag=x]</code> — save last result\n"
            f"<code>{p}dothat saved</code> — list saved\n"
            f"<code>{p}dothat retry</code> — repeat last\n"
            f"<code>{p}dothat history [actor]</code> — recent queries\n"
            f"<code>{p}dothat find-in-history &lt;q&gt;</code> — fts search\n"
            f"<code>{p}dothat &lt;q&gt; --tag=x</code> — by tag\n"
            f"<code>{p}dothat &lt;q&gt; --to=&lt;chat_id&gt;</code> — to chat\n"
            "</blockquote>"
        )

    def _help_sources(self, p):
        return (
            "<blockquote><b>🗂 sources</b>\n"
            f"<code>{p}dothat add &lt;name&gt; &lt;url&gt; [--param=q] [--tag=x] [--priority=high]</code>\n"
            f"<code>{p}dothat add-api &lt;name&gt; &lt;preset|url&gt; [--path=... --title_field=... --url_field=...]</code>\n"
            f"<code>{p}dothat add-contrib &lt;name&gt; &lt;url&gt;</code> — propose\n"
            f"<code>{p}dothat pending</code> — pending queue\n"
            f"<code>{p}dothat approve &lt;id&gt;</code>\n"
            f"<code>{p}dothat reject &lt;id&gt;</code>\n"
            f"<code>{p}dothat remove &lt;name&gt;</code>\n"
            f"<code>{p}dothat enable|disable &lt;name&gt;</code>\n"
            f"<code>{p}dothat rename &lt;old&gt; &lt;new&gt;</code>\n"
            f"<code>{p}dothat clone &lt;old&gt; &lt;new&gt;</code>\n"
            f"<code>{p}dothat tag &lt;name&gt; [+|-]tag</code>\n"
            f"<code>{p}dothat priority &lt;name&gt; high|normal|low</code>\n"
            f"<code>{p}dothat weight &lt;name&gt; &lt;float&gt;</code>\n"
            f"<code>{p}dothat sites [page]</code> — list\n"
            f"<code>{p}dothat tags</code> — all tags\n"
            f"<code>{p}dothat info &lt;name&gt;</code> — one source\n"
            "</blockquote>"
        )

    def _help_diag(self, p):
        return (
            "<blockquote><b>🔬 diagnostics</b>\n"
            f"<code>{p}dothat test &lt;url&gt; [--param=q] [--save]</code>\n"
            f"<code>{p}dothat ping</code>\n"
            f"<code>{p}dothat heal</code>\n"
            f"<code>{p}dothat doctor</code>\n"
            f"<code>{p}dothat dead</code>\n"
            f"<code>{p}dothat slow</code>\n"
            f"<code>{p}dothat slow-source</code>\n"
            f"<code>{p}dothat stat</code>\n"
            f"<code>{p}dothat latency</code>\n"
            f"<code>{p}dothat top</code>\n"
            f"<code>{p}dothat dashboard</code>\n"
            f"<code>{p}dothat whoami</code>\n"
            f"<code>{p}dothat my-stats</code>\n"
            f"<code>{p}dothat audit [n]</code>\n"
            f"<code>{p}dothat audit-me</code>\n"
            f"<code>{p}dothat logs [n]</code>\n"
            f"<code>{p}dothat snapshot &lt;name&gt; &lt;query&gt;</code>\n"
            f"<code>{p}dothat diff &lt;name&gt; &lt;query&gt;</code>\n"
            f"<code>{p}dothat note add &lt;url&gt; &lt;text&gt;</code>\n"
            f"<code>{p}dothat notes [search]</code>\n"
            f"<code>{p}dothat note remove &lt;url&gt;</code>\n"
            "</blockquote>"
        )

    def _help_plugins(self, p):
        return (
            "<blockquote><b>🧩 plugins</b>\n"
            f"<code>{p}dothat install [name]</code>\n"
            f"<code>{p}dothat plugins [--trust=trusted]</code>\n"
            f"<code>{p}dothat plugin info|reload|enable|disable|remove &lt;name&gt;</code>\n"
            f"<code>{p}dothat plugin search &lt;query&gt;</code>\n"
            f"<code>{p}dothat plugin install &lt;name&gt; [--trust=privileged]</code>\n"
            f"<code>{p}dothat plugin update [&lt;name&gt;]</code>\n"
            f"<code>{p}dothat plugin upgrade-all</code>\n"
            f"<code>{p}dothat plugin refresh-index</code>\n"
            f"<code>{p}dothat plugin trust &lt;name&gt; &lt;sandboxed|trusted|privileged&gt;</code>\n"
            f"<code>{p}dothat plugin trust-list</code>\n"
            "</blockquote>"
        )

    def _help_trust(self, p):
        return (
            "<blockquote><b>🔐 plugin trust</b>\n"
            "<b>sandboxed</b> — только ctx\n"
            "<b>trusted</b> — ctx + module\n"
            "<b>privileged</b> — ctx + module + kernel + cfg\n"
            f"<code>{p}dothat cfg trusted_plugin_authors [\"@author\"]</code>\n"
            f"<code>{p}dothat cfg privileged_plugin_authors [\"@author\"]</code>\n"
            f"<code>{p}dothat plugin trust &lt;name&gt; trusted</code>\n"
            f"<code>{p}dothat plugin trust-list</code>\n"
            "</blockquote>"
        )

    def _help_roles(self, p):
        return (
            "<blockquote><b>🛡 roles</b>\n"
            f"<code>{p}dothat help roles list</code>\n"
            f"<code>{p}dothat help roles manage</code>\n"
            f"<code>{p}dothat help roles perms</code>\n"
            f"<code>{p}dothat help roles trust</code>\n"
            f"<code>{p}dothat help roles quotas</code>\n"
            f"<code>{p}dothat help roles mute</code>\n"
            "</blockquote>"
        )

    def _help_roles_list(self, p):
        return (
            "<blockquote><b>roles · list</b>\n"
            f"<code>{p}dothat trusted</code>\n"
            f"<code>{p}dothat roles</code>\n"
            f"<code>{p}dothat roleinfo &lt;uid|@u|reply&gt;</code>\n"
            "</blockquote>"
        )

    def _help_roles_manage(self, p):
        return (
            "<blockquote><b>roles · manage</b>\n"
            f"<code>{p}dothat trust</code>\n"
            f"<code>{p}dothat untrust</code>\n"
            f"<code>{p}dothat role set &lt;uid|@u|reply&gt; &lt;role&gt;</code>\n"
            f"<code>{p}dothat role remove &lt;uid|@u|reply&gt;</code>\n"
            f"<code>{p}dothat role up &lt;uid|@u|reply&gt;</code>\n"
            f"<code>{p}dothat role down &lt;uid|@u|reply&gt;</code>\n"
            "roles: guest viewer contributor verified searcher editor admin superadmin\n"
            "</blockquote>"
        )

    def _help_roles_perms(self, p):
        return (
            "<blockquote><b>roles · permissions</b>\n"
            "<b>guest</b> — whoami, help\n"
            "<b>viewer</b> — + sites, tags, info, stat, top, dashboard, my-stats, latency\n"
            "<b>contributor</b> — + add-contrib, pending\n"
            "<b>verified/searcher</b> — + search, multi, trace, raw, retry, history, profile, page, openall, json, save, saved\n"
            "<b>editor</b> — + add, remove, enable, disable, rename, clone, tag, priority, weight, ping, heal, doctor, dead, slow, watch, note, snapshot, diff, export\n"
            "<b>admin</b> — + logs, metrics, audit, mute, unmute\n"
            "<b>superadmin</b> — + plugins, plugin reload/enable/disable, cfg get, import\n"
            "<b>owner</b> — everything\n"
            "</blockquote>"
        )

    def _help_roles_trust(self, p):
        return (
            "<blockquote><b>roles · trust</b>\n"
            f"<code>{p}dothat trust</code>\n"
            f"<code>{p}dothat untrust</code>\n"
            f"<code>{p}dothat role set reply &lt;role&gt;</code>\n"
            "</blockquote>"
        )

    def _help_roles_quotas(self, p):
        return (
            "<blockquote><b>roles · quotas</b>\n"
            f"<code>{p}dothat cfg trusted_quotas {{\"123\":{{\"daily_searches\":50,\"daily_adds\":5}}}}</code>\n"
            f"<code>{p}dothat cfg quota_used</code>\n"
            "</blockquote>"
        )

    def _help_roles_mute(self, p):
        return (
            "<blockquote><b>roles · mute</b>\n"
            f"<code>{p}dothat mute reply 1h</code>\n"
            f"<code>{p}dothat mute 123456 30m</code>\n"
            f"<code>{p}dothat unmute reply</code>\n"
            "</blockquote>"
        )

    def _help_service(self, p):
        return (
            "<blockquote><b>⚙ service</b>\n"
            f"<code>{p}dothat cfg &lt;key&gt; [value]</code>\n"
            f"<code>{p}dothat cfg &lt;key&gt; --reset</code>\n"
            f"<code>{p}dothat export [--format=json|jsonl|csv|md|html|misp]</code>\n"
            f"<code>{p}dothat import</code>\n"
            f"<code>{p}dothat backup</code>\n"
            f"<code>{p}dothat restore</code>\n"
            f"<code>{p}dothat watch add|list|remove|run</code>\n"
            f"<code>{p}dothat metrics export [--since=7d] [--format=csv|json]</code>\n"
            f"<code>{p}dothat template add|list|run|remove</code>\n"
            f"<code>{p}dothat version</code>\n"
            "</blockquote>"
        )

    def _help_operators(self, p):
        return (
            "<blockquote><b>⚡ operators</b>\n"
            "<code>+word</code>\n<code>-word</code>\n"
            '<code>"phrase"</code>\n'
            "<code>site:example.com</code>\n"
            "<code>filetype:pdf,docx</code>\n"
            "<code>intitle:word</code>\n"
            "<code>кот*</code>\n<code>~котик</code>\n"
            "<code>(котик OR кот) AND NOT собака</code>\n"
            "</blockquote>"
        )

    def _help_commands(self, role_filter=None):
        p = html.escape(self._prefix())
        order = ["guest", "viewer", "contributor", "verified", "searcher", "editor", "admin", "superadmin", "owner"]
        start_idx = 0
        if role_filter and role_filter in ROLE_ORDER:
            start_idx = order.index(role_filter) if role_filter in order else 0
        lines = ["<blockquote><b>📋 commands by role</b></blockquote>"]
        seen = set()
        for role in order[start_idx:]:
            if role in seen:
                continue
            seen.add(role)
            cmds = ROLE_COMMANDS.get(role)
            if cmds is None:
                cmds = set()
                for r2 in order:
                    if r2 == "owner":
                        continue
                    c = ROLE_COMMANDS.get(r2)
                    if c:
                        cmds.update(c)
            prev = set()
            for r2 in order[:order.index(role)]:
                c = ROLE_COMMANDS.get(r2)
                if c:
                    prev.update(c)
            new = sorted(cmds - prev)
            if not new:
                continue
            lines.append(f"<b>— {role} —</b>")
            for c in new:
                lines.append(f"  <code>{p}dothat {html.escape(c)}</code>")
        lines.append(f"<i>full: <code>{p}dothat help commands [role]</code></i>")
        return "\n".join(lines)

    def _sites_text(self, page=0):
        sites = self._sites()
        names = sorted(sites.keys())
        per = max(1, int(self.cfg.get("sites_per_page", 5) or 5))
        total = max(1, (len(names) + per - 1) // per)
        page = max(0, min(page, total - 1))
        chunk = names[page * per:(page + 1) * per]
        p = self._prefix()
        out = [
            "<blockquote><b>🗂 sources</b></blockquote>",
            f"<b>total:</b> <code>{len(names)}</code> · <b>page:</b> <code>{page + 1}/{total}</code>",
            "",
        ]
        for n in chunk:
            d = sites[n]
            alive = d.get("alive")
            mark = "🟢" if alive else ("🔴" if alive is False else "⚪")
            dis = " ⏸" if d.get("disabled") else ""
            typ = " [api]" if d.get("type") == "api" else ""
            prio = d.get("priority") or "normal"
            tags = ",".join(d.get("tags") or []) or "-"
            weight = d.get("weight", 1.0)
            out.append(f"{mark} <b>{html.escape(n)}</b>{dis}{typ} — <code>{html.escape(d.get('host', '?'))}</code>")
            out.append(f"   prio=<code>{html.escape(prio)}</code> tags=<code>{html.escape(tags)}</code> w=<code>{weight}</code>")
        if total > 1:
            out.append("")
            nav = []
            if page > 0:
                nav.append(f"{p}dothat sites {page}")
            if page + 1 < total:
                nav.append(f"{p}dothat sites {page + 2}")
            if nav:
                out.append("<i>next: " + " | ".join(f"<code>{html.escape(n)}</code>" for n in nav) + "</i>")
        return "\n".join(out)

    def _trusted_text(self, page=0):
        r = self.cfg.get("roles", {}) or {}
        all_ids = []
        for k in ("superadmins", "admins", "editors", "verified", "contributors", "searchers", "viewers", "guests", "trusted"):
            for uid in r.get(k) or []:
                all_ids.append((uid, k))
        per = max(1, int(self.cfg.get("trusted_per_page", 5) or 5))
        total = max(1, (len(all_ids) + per - 1) // per)
        page = max(0, min(page, total - 1))
        chunk = all_ids[page * per:(page + 1) * per]
        p = self._prefix()
        out = [
            "<blockquote><b>trusted users</b></blockquote>",
            f"<b>total:</b> <code>{len(all_ids)}</code> · <b>page:</b> <code>{page + 1}/{total}</code>",
            "",
        ]
        if not all_ids:
            out.append("<i>no trusted users.</i>")
        else:
            for uid, rname in chunk:
                out.append(f"<code>{uid}</code> — <code>{rname}</code>")
        out.append("")
        out.append(f"<i>role set: <code>{p}dothat role set &lt;uid&gt; &lt;role&gt;</code></i>")
        return "\n".join(out)

    async def _search_site(self, name, site, query, deep=False):
        if site.get("disabled"):
            return {"__skipped__": name}
        site = self._apply_site_override(name, site)
        if site.get("type") == "api":
            return await self._search_api_site(name, site, query)
        url = self._build_url(site, query)
        sem = self._semaphore()
        try:
            self._token_bucket_wait(urlparse(url).netloc)
        except Exception:
            pass
        ctx = {"url": url, "site": site, "name": name, "query": query}
        pre = await self._run_hook("before_fetch", ctx)
        if pre is False:
            return {"__error__": name, "error": "blocked by plugin"}
        if isinstance(pre, str):
            url = pre
        async with sem:
            try:
                page, status, elapsed = await self._fetch_async(url)
            except Exception as e:
                hr = await self._run_hook("on_error", {**ctx, "error": str(e)})
                if isinstance(hr, str):
                    page, status, elapsed = hr, 200, 0.0
                else:
                    self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                    return {"__error__": name, "error": str(e)[:200]}
        post = await self._run_hook("after_fetch", {**ctx, "html": page, "status": status})
        if isinstance(post, str):
            page = post
        bypass_info = None
        fallback_used = None
        if self._is_cloudflare(page):
            hr = await self._run_hook("on_blocked", {**ctx, "html": page, "reason": "cloudflare"})
            if isinstance(hr, str) and hr:
                page = hr
                bypass_info = "plugin:cloudflare"
            elif self.cfg.get("cf_refuse", True):
                if self.cfg.get("auto_fallback_url", True) and not site.get("_fallback_done"):
                    fb = await self._try_url_fallback(name, site, query, ctx)
                    if fb:
                        page, fallback_used = fb, "url_fallback"
                    else:
                        self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "cloudflare")
                        self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                        return {"__error__": name, "error": "cloudflare (refused)"}
                else:
                    self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "cloudflare")
                    self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                    return {"__error__": name, "error": "cloudflare (refused)"}
        elif self._is_captcha(page):
            hr = await self._run_hook("on_blocked", {**ctx, "html": page, "reason": "captcha"})
            if isinstance(hr, str) and hr:
                page = hr
                bypass_info = "plugin:captcha"
            elif self.cfg.get("captcha_bypass", True):
                bypassed, info = await self._bypass_captcha(url)
                bypass_info = info
                if bypassed:
                    page = bypassed
                else:
                    if self.cfg.get("auto_fallback_url", True) and not site.get("_fallback_done"):
                        fb = await self._try_url_fallback(name, site, query, ctx)
                        if fb:
                            page, fallback_used = fb, "url_fallback"
                        else:
                            self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "captcha")
                            self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                            return {"__error__": name, "error": f"captcha ({info})"}
                    elif self.cfg.get("use_jina", True):
                        jp = await self._fetch_with_jina(url)
                        if jp and not self._is_captcha(jp) and not self._is_cloudflare(jp):
                            page = jp
                            bypass_info = "jina_fallback"
                        else:
                            self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "captcha")
                            self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                            return {"__error__": name, "error": f"captcha ({info})"}
                    else:
                        self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "captcha")
                        self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
                        return {"__error__": name, "error": f"captcha ({info})"}
            else:
                return {"__error__": name, "error": "captcha"}
        if self._is_cloudflare(page) or self._is_captcha(page):
            self._sqlite_log_fetch(name, url, status, elapsed, len(page), True, "still-blocked")
            self._stats["per_source_fail"][name] = self._stats["per_source_fail"].get(name, 0) + 1
            return {"__error__": name, "error": "still blocked after bypass"}
        page = self._unwrap_ddg_in_html(page)
        title, text, links, files, images, meta = self._extract(page, url)
        if self._looks_js_required(text, page):
            hr = await self._run_hook("on_js_required", {**ctx, "html": page})
            if isinstance(hr, str) and hr:
                jt, jtx, jl, jf, ji, jm = self._extract(hr, url)
                if jtx and len(jtx) > len(text):
                    title, text, links, files, images, meta = jt or title, jtx, jl or links, jf or files, ji or images, jm or meta
                    bypass_info = (bypass_info or "") + "|plugin:js"
            elif self.cfg.get("use_jina", True):
                jp = await self._fetch_with_jina(url)
                if jp:
                    jt, jtx, jl, jf, ji, jm = self._extract(jp, url)
                    if jtx and len(jtx) > len(text):
                        title, text, links, files, images, meta = jt or title, jtx, jl or links, jf or files, ji or images, jm or meta
        if not self._is_cloudflare(page) and not self._is_captcha(page):
            self._stats["per_source_fail"][name] = 0
        norm_text = self._lemmatize(text)
        words = [w for w in self._lemmatize(query).split() if len(w) > 1]
        matches = sum(1 for w in words if w in norm_text)
        if matches == 0 and words:
            matching_links = [l for l in links if any(w in l.lower() for w in words)]
        else:
            matching_links = links[:8]
        snippet_len = int(self.cfg.get("max_snippet", 1200) or 1200)
        snippet = self._context_snippet(text[:snippet_len * 2], query)[:snippet_len]
        if self.cfg.get("pii_filter_in_snippet", False):
            snippet = self._clean(snippet)
        snippet_esc = html.escape(snippet)
        snippet_hl = self._highlight(snippet_esc, query)
        self._sqlite_log_fetch(name, url, status, elapsed, len(page), False, bypass_info or fallback_used or "ok")
        lat = self._stats["latency"].setdefault(name, [])
        lat.append(elapsed)
        if len(lat) > int(self.cfg.get("latency_max_entries", 200) or 200):
            self._stats["latency"][name] = lat[-100:]
        if deep and self.cfg.get("snapshots_enabled", True):
            self._sqlite_save_snapshot(name, query, url, page)
        result = {
            "name": name, "url": url, "title": title or "untitled page",
            "snippet": snippet, "snippet_esc": snippet_esc, "snippet_hl": snippet_hl,
            "links": [self._unwrap_ddg(l) for l in matching_links[:8]],
            "files": [self._unwrap_ddg(f) for f in files],
            "images": images,
            "matches": matches, "total_links": len(links),
            "status": status, "elapsed": elapsed,
            "bypass": bypass_info, "fallback": fallback_used,
            "override": site.get("_override_note"),
            "tags": site.get("tags") or [], "priority": site.get("priority") or "normal",
            "entities": self._extract_entities(text),
            "meta": meta,
        }
        await self._run_hook("on_result", {**ctx, "result": result})
        return result

    async def _try_url_fallback(self, name, site, query, ctx):
        host = (site.get("host") or "").lower()
        for h, ov in SITE_URL_OVERRIDES.items():
            if h in host or host in h:
                fb = ov["url"].replace("{query}", quote_plus(query))
                try:
                    page, _, _ = await self._fetch_async(fb)
                    if page and not self._is_cloudflare(page) and not self._is_captcha(page):
                        return page
                except Exception:
                    continue
        return None

    async def _search_api_site(self, name, site, query):
        url = self._build_url(site, query)
        try:
            data, status = await self._fetch_json(url)
        except Exception as e:
            return {"__error__": name, "error": str(e)[:200]}
        if data is None:
            return {"__error__": name, "error": "invalid json"}
        special = site.get("special")
        items = []
        if special == "opensearch":
            if isinstance(data, list) and len(data) >= 4:
                titles = data[1] or []
                descs = data[2] or []
                urls = data[3] or []
                for i in range(min(len(titles), len(urls))):
                    items.append({"title": titles[i], "url": urls[i], "desc": descs[i] if i < len(descs) else ""})
        else:
            raw = self._json_path(data, site.get("path"))
            if isinstance(raw, dict):
                raw = [raw]
            if not isinstance(raw, list):
                raw = []
            tf = site.get("title_field")
            uf = site.get("url_field")
            df = site.get("desc_field")
            for it in raw[:30]:
                t = self._json_path(it, tf) if tf else None
                l = self._json_path(it, uf) if uf else None
                d = self._json_path(it, df) if df else ""
                if not l and not t:
                    continue
                items.append({"title": str(t or "untitled"), "url": str(l or site.get("host", "")), "desc": str(d or "")[:300]})
        text = " ".join(f"{it['title']} — {it['desc']}" for it in items)
        words = [w for w in self._lemmatize(query).split() if len(w) > 1]
        norm = self._lemmatize(text)
        matches = sum(1 for w in words if w in norm)
        snippet_len = int(self.cfg.get("max_snippet", 1200) or 1200)
        snippet = self._context_snippet(text[:snippet_len * 2], query)[:snippet_len]
        snippet_esc = html.escape(snippet)
        return {
            "name": name, "url": url, "title": f"{name} (api)",
            "snippet": snippet, "snippet_esc": snippet_esc, "snippet_hl": self._highlight(snippet_esc, query),
            "links": [it["url"] for it in items[:8]], "files": [], "images": [],
            "matches": matches, "total_links": len(items),
            "status": status or 0, "elapsed": 0.0, "bypass": "api",
            "tags": site.get("tags") or [], "priority": site.get("priority") or "normal",
            "entities": {},
        }

    async def _search_everywhere(self, query, tag=None, mode="normal", actor=None, chat_id=None):
        started_at = time.time()
        pre = await self._run_hook("on_search", {"query": query, "tag": tag, "mode": mode, "actor": actor})
        if isinstance(pre, tuple) and len(pre) == 2:
            return pre
        cache_suffix = f"|{tag or ''}|{mode}"
        cached = self._cache_get(query + cache_suffix, actor=actor)
        if cached is not None:
            return cached, []
        op_query, ops = self._parse_boolean(query)
        syn_query = self._apply_synonyms(op_query) if op_query else op_query
        sites = self._sites()
        if tag:
            sites = {n: s for n, s in sites.items() if tag in (s.get("tags") or [])}
        sites = {n: s for n, s in sites.items() if not s.get("disabled")}
        if not sites:
            return [], []
        deep = mode == "deep"
        if mode == "fast":
            fast = {n: s for n, s in sites.items() if s.get("priority") == "high"}
            if fast:
                sites = fast
        high_results = None
        if mode != "all" and self.cfg.get("priority_first", True) and mode != "fast":
            high = {n: s for n, s in sites.items() if s.get("priority") == "high"}
            if high:
                tasks = [self._search_site(n, s, syn_query or query, deep=deep) for n, s in high.items()]
                hr = await asyncio.gather(*tasks, return_exceptions=True)
                okh = [r for r in hr if isinstance(r, dict) and "__error__" not in r and "__skipped__" not in r]
                if okh and len(okh) >= max(1, len(high) // 2):
                    sites = high
                    high_results = hr
        if high_results is not None:
            raw = high_results
        else:
            tasks = [self._search_site(n, s, syn_query or query, deep=deep) for n, s in sites.items()]
            raw = await asyncio.gather(*tasks, return_exceptions=True)
        ok = []
        err = []
        seen_links = set()
        for item in raw:
            if isinstance(item, dict) and "__skipped__" in item:
                continue
            if isinstance(item, dict) and "__error__" in item:
                err.append(item)
            elif isinstance(item, dict):
                ul = []
                for l in item["links"]:
                    if l not in seen_links:
                        seen_links.add(l)
                        ul.append(l)
                item["links"] = ul
                ok.append(item)
            elif isinstance(item, BaseException):
                err.append({"__error__": "?", "error": str(item)[:200]})
        ok = self._apply_operators_filter(ok, ops)
        ok = self._dedup_difflib(ok)
        for r in ok:
            site = sites.get(r["name"], {})
            r["score"] = self._bm25_score(r, syn_query or query, ok, site)
        ok.sort(key=lambda r: r.get("score", 0), reverse=True)
        self._cache_set(query + cache_suffix, ok, actor=actor)
        self._stats["total_queries"] += 1
        self._stats["total_sources_hit"] += len(ok)
        self._stats["top_queries"][query] = self._stats["top_queries"].get(query, 0) + 1
        for r in ok:
            src = r["name"]
            self._stats["per_source"][src] = self._stats["per_source"].get(src, 0) + 1
        if actor is not None:
            pu = self._stats["per_user"]
            pu[str(actor)] = pu.get(str(actor), 0) + 1
        elapsed_total = time.time() - started_at
        if elapsed_total > float(self.cfg.get("slow_query_threshold", 5.0) or 5.0):
            self._stats["slow_queries"].append({"ts": time.time(), "query": query, "elapsed": round(elapsed_total, 2), "hits": len(ok)})
            if len(self._stats["slow_queries"]) > 100:
                self._stats["slow_queries"] = self._stats["slow_queries"][-100:]
            self._sqlite_log_slow(actor, query, elapsed_total, len(ok))
        self._last_result = {"query": query, "ok": ok, "err": err, "ts": time.time(), "actor": str(actor) if actor else "?"}
        self._history.append({"query": query, "ts": time.time(), "hits": len(ok), "errors": len(err), "actor": str(actor) if actor else "?"})
        if len(self._history) > int(self.cfg.get("history_size", 50) or 50):
            self._history = self._history[-int(self.cfg.get("history_size", 50) or 50):]
        self._save_persistent_state()
        self._sqlite_log_query(actor, query, len(ok), len(err))
        if actor is not None:
            self._user_activity.setdefault(str(actor), []).append({"ts": time.time(), "type": "search", "query": query})
            limit = int(self.cfg.get("user_activity_max", 500) or 500)
            if len(self._user_activity) > limit:
                items = sorted(self._user_activity.items(), key=lambda kv: -(max((a["ts"] for a in kv[1]), default=0)))
                self._user_activity = dict(items[: limit // 2])
        if self.cfg.get("webhook_url"):
            asyncio.create_task(self._fire_webhook(query, ok, err))
        return ok, err

    async def _fire_webhook(self, query, ok, err):
        url = self.cfg.get("webhook_url")
        if not url:
            return
        if not self._is_ssrf_safe(url):
            return
        payload = json.dumps({"query": query, "hits": len(ok), "errors": len(err), "urls": [r["url"] for r in ok[:20]]}, ensure_ascii=False)
        headers = {"Content-Type": "application/json"}
        secret = self.cfg.get("webhook_secret") or ""
        if secret:
            sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
            headers["X-DDT-Signature"] = f"sha256={sig}"
        retries = int(self.cfg.get("webhook_retries", 3) or 3)
        for attempt in range(retries):
            try:
                req = Request(url, data=payload.encode("utf-8"), headers=headers, method="POST")
                resp = await asyncio.to_thread(lambda: urlopen(req, timeout=10))
                code = getattr(resp, "status", 200)
                if 200 <= code < 300:
                    return
            except Exception:
                pass
            await asyncio.sleep(2 ** attempt)

    @watcher
    async def trusted_watcher(self, event):
        if getattr(event, "_tetko_handled", False):
            return
        if getattr(event, "_ddt_trusted", False):
            return
        if getattr(event, "out", False):
            return
        text = (getattr(event, "raw_text", "") or "").strip()
        if not text:
            return
        prefix = self._prefix()
        if not text.startswith(prefix):
            return
        body = text[len(prefix):].split(maxsplit=1)
        if not body:
            return
        cmd = body[0].lower()
        if cmd != "dothat":
            return
        sender = self._sender_id(event)
        if sender is None:
            return
        owner_id = getattr(self.kernel.context, "admin_id", None)
        if owner_id is not None and sender == owner_id:
            return
        role = self._role_of(event)
        if role is None:
            return
        if self._user_blocked(event):
            return
        if not self._chat_allowed(event):
            return
        tc = self.cfg.get("trusted_chat_id")
        if tc is not None:
            try:
                if event.chat_id != tc:
                    return
            except Exception:
                return
        muted_until = self._is_muted(sender)
        if muted_until:
            try:
                await event.reply(f"🚫 muted until {time.strftime('%Y-%m-%d %H:%M', time.localtime(muted_until))}")
            except Exception:
                pass
            return
        if not self._user_rate_ok(sender, event):
            try:
                await event.reply("🚫 rate limit")
            except Exception:
                pass
            return
        event._tetko_handled = True
        event._ddt_trusted = True
        event._ddt_role = role
        event._ddt_real_sender = sender
        self._audit_log(sender, "trusted_command", text[:200])
        await self._notify_owner_trusted(event, "command", text[:200])
        tlc = self.cfg.get("trusted_log_chat")
        if tlc:
            try:
                await event.client.send_message(tlc, f"👤 <code>{sender}</code> → <code>{html.escape(text[:200])}</code>", parse_mode="html")
            except Exception:
                pass
        cmd_hook = await self._run_hook("on_command", {"event": event, "text": text, "sender": sender, "role": role})
        if cmd_hook is False:
            return
        try:
            await self.dothat(event)
        except Exception as e:
            self._audit_log(sender, "trusted_error", str(e)[:200])
            try:
                await event.reply(f"❌ error: {e}")
            except Exception:
                pass

    @loop(interval=3600)
    async def healthcheck(self):
        sites = self._sites()
        if not sites:
            return
        sem = asyncio.Semaphore(5)
        st = {"ch": False}

        async def check(name, site):
            async with sem:
                tu = self._build_url(site, "test")
                try:
                    alive = await asyncio.wait_for(asyncio.to_thread(self._ping, tu), timeout=15)
                except Exception:
                    alive = False
                if site.get("alive") != alive:
                    site["alive"] = alive
                    st["ch"] = True

        await asyncio.gather(*(check(n, s) for n, s in sites.items()))
        if st["ch"]:
            self._save_sites(sites)

    @loop(interval=3600)
    async def auto_disable_dead(self):
        thr = int(self.cfg.get("auto_disable_threshold", 10) or 10)
        if thr <= 0:
            return
        fails = self._stats.get("per_source_fail", {}) or {}
        sites = self._sites()
        changed = False
        for name, count in list(fails.items()):
            if count >= thr and name in sites and not sites[name].get("disabled"):
                sites[name]["disabled"] = True
                changed = True
        if changed:
            self._save_sites(sites)

    @loop(interval=300)
    async def auto_demote(self):
        thr = int(self.cfg.get("auto_demote_threshold", 60) or 60)
        win = int(self.cfg.get("auto_demote_window", 3600) or 3600)
        if thr <= 0:
            return
        now = time.time()
        owner_id = None
        try:
            owner_id = str(self.kernel.context.admin_id)
        except Exception:
            pass
        for uid, acts in list(self._user_activity.items()):
            if uid == owner_id:
                continue
            recent = [a for a in acts if now - a["ts"] < win]
            self._user_activity[uid] = recent
            if len(recent) >= thr:
                try:
                    r = self.cfg.get("roles", {}) or {}
                    demoted = None
                    if int(uid) in (r.get("editors") or []):
                        self._set_role(int(uid), "verified")
                        demoted = "verified"
                    elif int(uid) in (r.get("verified") or []):
                        self._set_role(int(uid), "contributor")
                        demoted = "contributor"
                    elif int(uid) in (r.get("contributors") or []):
                        self._set_role(int(uid), "viewer")
                        demoted = "viewer"
                    if demoted and owner_id:
                        try:
                            await self.kernel.client.send_message(int(owner_id), f"⚠️ auto-demote <code>{uid}</code>: {len(recent)} actions in {win}s → <code>{demoted}</code>", parse_mode="html")
                        except Exception:
                            pass
                except Exception:
                    pass

    @loop(interval=600)
    async def cleanup_pending_actions(self):
        ttl = int(self.cfg.get("pending_actions_ttl", 86400) or 86400)
        if ttl <= 0:
            return
        pending = self.cfg.get("pending_actions", {}) or {}
        if not pending:
            return
        now = time.time()
        new = {k: v for k, v in pending.items() if now - v.get("ts", 0) < ttl}
        if len(new) != len(pending):
            self.cfg.set("pending_actions", new)

    @loop(interval=60)
    async def watch_runner(self):
        await self._watch_runner_once(None)

    @command(name="dothat", description="Public web search")
    async def dothat(self, event):
        if not self._chat_allowed(event):
            return
        if self._user_blocked(event):
            await self._respond(event, "<blockquote><b>🚫 blocked</b></blockquote>", parse_mode="html")
            return
        args = self._args(event)
        p = self._prefix()
        sender = self._sender_id(event)
        chat_id = None
        try:
            chat_id = event.chat_id
        except Exception:
            pass

        if not args:
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is not None:
                try:
                    is_bot_msg = getattr(reply, "out", False) or bool(getattr(reply, "via_bot_id", None))
                except Exception:
                    is_bot_msg = False
                if not is_bot_msg:
                    try:
                        s = await reply.get_sender()
                    except Exception:
                        s = None
                    un = getattr(s, "username", None) if s else None
                    if un:
                        args = f"@{un}"
                if not args:
                    await self._respond(event, self._usage(), parse_mode="html")
                    return
            else:
                await self._respond(event, self._usage(), parse_mode="html")
                return

        tag_filter = None
        tm = re.search(r"--tag=(\w+)", args)
        if tm:
            tag_filter = tm.group(1)
            args = re.sub(r"--tag=\w+", "", args).strip()

        to_chat = None
        to_m = re.search(r"--to=(-?\d+)", args)
        if to_m:
            to_chat = int(to_m.group(1))
            args = re.sub(r"--to=-?\d+", "", args).strip()

        parts = args.split(maxsplit=2)
        action = parts[0].lower() if parts else ""

        trusted = getattr(event, "_ddt_trusted", False)
        role = self._role_of(event)

        if action == "help":
            section = parts[1].lower() if len(parts) > 1 else ""
            sub = parts[2].lower() if len(parts) > 2 else ""
            if section == "roles":
                if sub == "list":
                    text = self._help_roles_list(p)
                elif sub == "manage":
                    text = self._help_roles_manage(p)
                elif sub == "perms":
                    text = self._help_roles_perms(p)
                elif sub == "trust":
                    text = self._help_roles_trust(p)
                elif sub == "quotas":
                    text = self._help_roles_quotas(p)
                elif sub == "mute":
                    text = self._help_roles_mute(p)
                else:
                    text = self._help_roles(p)
            elif section == "commands":
                text = self._help_commands(sub if sub in ROLE_ORDER else None)
            elif section == "search":
                text = self._help_search(p)
            elif section == "sources":
                text = self._help_sources(p)
            elif section == "diag":
                text = self._help_diag(p)
            elif section == "plugins":
                text = self._help_plugins(p)
            elif section == "trust":
                text = self._help_trust(p)
            elif section == "service":
                text = self._help_service(p)
            elif section == "operators":
                text = self._help_operators(p)
            else:
                all_known = ["search", "sources", "diag", "plugins", "trust", "roles", "service", "operators", "commands"]
                close = difflib.get_close_matches(section, all_known, n=1) if section else []
                if close:
                    text = f"<blockquote><b>unknown section</b> <code>{html.escape(section)}</code>\n<i>did you mean:</i> <code>{p}dothat help {html.escape(close[0])}</code></blockquote>"
                else:
                    text = self._help_main(p)
            await self._respond(event, text, parse_mode="html")
            return

        if action == "version":
            deps = []
            for name, mod in (("curl_cffi", _HAS_CURL), ("httpx", _HAS_HTTPX), ("pymorphy2", _MORPH is not None)):
                deps.append(f"{name}={'✓' if mod else '✗'}")
            trust_counts = {"sandboxed": 0, "trusted": 0, "privileged": 0}
            for v in self._plugins.values():
                t = v.get("trust_level", "sandboxed")
                trust_counts[t] = trust_counts.get(t, 0) + 1
            await self._respond(event, f"<blockquote><b>DontDoThat</b> v<code>{self.version}</code>\n<i>{html.escape(self.description)}</i>\n<b>plugins:</b> <code>{len(self._plugins)}</code> (🔒{trust_counts.get('sandboxed', 0)} 🔓{trust_counts.get('trusted', 0)} 👑{trust_counts.get('privileged', 0)})\n<b>sites:</b> <code>{len(self._sites())}</code>\n<b>deps:</b> <code>{' '.join(deps)}</code></blockquote>", parse_mode="html")
            return

        if action == "whoami":
            await self._respond(event, f"<blockquote><b>role:</b> <code>{html.escape(role or 'none')}</code></blockquote>", parse_mode="html")
            return

        if action == "my-stats":
            sid = str(sender)
            user_searches = self._stats["per_user"].get(sid, 0)
            my_hist = [h for h in self._history if h.get("actor") == sid]
            await self._respond(event, f"<blockquote><b>my stats</b>\n<b>role:</b> <code>{html.escape(role or 'none')}</code>\n<b>my searches:</b> <code>{user_searches}</code>\n<b>last 10:</b>\n" + "\n".join(f"<code>{time.strftime('%H:%M', time.localtime(h['ts']))}</code> — <code>{html.escape(h['query'][:60])}</code>" for h in my_hist[-10:]) + "</blockquote>", parse_mode="html")
            return

        if action == "audit-me":
            sid = str(sender)
            rows = [a for a in self._audit if a.get("actor") == sid]
            if not rows:
                await self._respond(event, "<blockquote><b>no actions.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>my audit</b></blockquote>"]
            for rec in rows[-20:][::-1]:
                ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(rec["ts"]))
                out.append(f"<code>{ts}</code> <b>{html.escape(rec['action'])}</b> — {html.escape(rec['details'])}")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if trusted and role is None:
            return

        if action == "trust":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is None:
                await self._respond(event, "<blockquote><b>reply to a user</b></blockquote>", parse_mode="html")
                return
            try:
                target = await reply.get_sender()
                uid = getattr(target, "id", None)
            except Exception:
                uid = None
            if uid is None:
                await self._respond(event, "<blockquote><b>cannot resolve user</b></blockquote>", parse_mode="html")
                return
            self._set_role(uid, "trusted")
            self._audit_log(sender, "trust", str(uid))
            await self._run_hook("on_role_change", {"uid": uid, "role": "trusted", "actor": sender})
            await self._respond(event, f"<blockquote><b>trusted:</b> <code>{uid}</code>\n<i>now assign role:</i> <code>{html.escape(p)}dothat role set reply viewer</code></blockquote>", parse_mode="html")
            return

        if action == "untrust":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is None:
                await self._respond(event, "<blockquote><b>reply to a user</b></blockquote>", parse_mode="html")
                return
            try:
                target = await reply.get_sender()
                uid = getattr(target, "id", None)
            except Exception:
                uid = None
            if uid is None:
                return
            self._remove_role(uid)
            await self._run_hook("on_role_change", {"uid": uid, "role": None, "actor": sender})
            await self._respond(event, f"<blockquote><b>untrusted:</b> <code>{uid}</code></blockquote>", parse_mode="html")
            return

        if action == "trusted":
            text = self._trusted_text(0)
            await self._respond(event, text, parse_mode="html")
            return

        if action == "roles":
            r = self.cfg.get("roles", {}) or {}
            out = ["<blockquote><b>roles</b></blockquote>"]
            for k in ("superadmins", "admins", "editors", "verified", "contributors", "searchers", "viewers", "guests", "trusted"):
                ids = r.get(k) or []
                out.append(f"<b>{k}:</b> <code>{', '.join(str(x) for x in ids) or '-'}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "role":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat role set|remove|up|down &lt;uid|@u|reply&gt; [role]</code></blockquote>", parse_mode="html")
                return
            sub = parts[1].lower()
            tail = parts[2]
            toks = tail.split()
            if not toks:
                return
            target = toks[0]
            new_role = toks[1].lower() if len(toks) > 1 else None
            uid = None
            if target == "reply":
                try:
                    reply = await event.get_reply_message()
                    s = await reply.get_sender()
                    uid = getattr(s, "id", None)
                except Exception:
                    uid = None
            elif target.startswith("@"):
                try:
                    e = await self.kernel.client.get_entity(target)
                    uid = e.id
                except Exception:
                    uid = None
            else:
                try:
                    uid = int(target)
                except ValueError:
                    uid = None
            if uid is None:
                await self._respond(event, "<blockquote><b>cannot resolve target</b></blockquote>", parse_mode="html")
                return
            if sub in ("set", "remove", "up", "down") and self.cfg.get("role_requires_trusted", False):
                if not self._is_trusted_uid(uid):
                    await self._respond(event, f"<blockquote><b>user not trusted</b>\n<i>use</i> <code>{html.escape(p)}dothat trust</code></blockquote>", parse_mode="html")
                    return
            if sub == "set":
                if new_role not in ("guest", "viewer", "contributor", "verified", "searcher", "editor", "admin", "superadmin", "trusted"):
                    await self._respond(event, "<blockquote><b>role must be guest|viewer|contributor|verified|searcher|editor|admin|superadmin|trusted</b></blockquote>", parse_mode="html")
                    return
                self._set_role(uid, new_role)
                self._audit_log(sender, "role_set", f"{uid} {new_role}")
                await self._run_hook("on_role_change", {"uid": uid, "role": new_role, "actor": sender})
                await self._respond(event, f"<blockquote><b>{uid}</b> → <code>{new_role}</code></blockquote>", parse_mode="html")
                return
            if sub == "remove":
                self._remove_role(uid)
                await self._run_hook("on_role_change", {"uid": uid, "role": None, "actor": sender})
                await self._respond(event, f"<blockquote><b>role removed:</b> <code>{uid}</code></blockquote>", parse_mode="html")
                return
            if sub == "up":
                order = ["guest", "viewer", "contributor", "verified", "searcher", "editor", "admin", "superadmin"]
                cur = self._role_of_by_uid(uid)
                idx = order.index(cur) if cur in order else 0
                nxt = order[min(idx + 1, len(order) - 1)]
                self._set_role(uid, nxt)
                await self._run_hook("on_role_change", {"uid": uid, "role": nxt, "actor": sender})
                await self._respond(event, f"<blockquote><b>{uid}</b>: <code>{cur}</code> → <code>{nxt}</code></blockquote>", parse_mode="html")
                return
            if sub == "down":
                order = ["guest", "viewer", "contributor", "verified", "searcher", "editor", "admin", "superadmin"]
                cur = self._role_of_by_uid(uid)
                if cur not in order:
                    await self._respond(event, "<blockquote><b>no role</b></blockquote>", parse_mode="html")
                    return
                idx = order.index(cur)
                prv = order[max(idx - 1, 0)]
                self._set_role(uid, prv)
                await self._run_hook("on_role_change", {"uid": uid, "role": prv, "actor": sender})
                await self._respond(event, f"<blockquote><b>{uid}</b>: <code>{cur}</code> → <code>{prv}</code></blockquote>", parse_mode="html")
                return
            return

        if action == "roleinfo":
            if len(parts) < 2:
                await self._respond(event, "<blockquote><b>need target</b></blockquote>", parse_mode="html")
                return
            tgt = parts[1]
            uid = None
            if tgt == "reply":
                try:
                    reply = await event.get_reply_message()
                    s = await reply.get_sender()
                    uid = getattr(s, "id", None)
                except Exception:
                    uid = None
            elif tgt.startswith("@"):
                try:
                    e = await self.kernel.client.get_entity(tgt)
                    uid = e.id
                except Exception:
                    uid = None
            else:
                try:
                    uid = int(tgt)
                except ValueError:
                    uid = None
            if uid is None:
                await self._respond(event, "<blockquote><b>cannot resolve</b></blockquote>", parse_mode="html")
                return
            r = self._role_of_by_uid(uid)
            await self._respond(event, f"<blockquote><b>{uid}</b> → <code>{r or 'none'}</code></blockquote>", parse_mode="html")
            return

        if action == "mute":
            if not self._role_gte(role, "admin"):
                await self._respond(event, "<blockquote><b>admin+</b></blockquote>", parse_mode="html")
                return
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat mute &lt;uid|reply&gt; &lt;1h|30m&gt;</code></blockquote>", parse_mode="html")
                return
            toks = parts[2].split()
            target = toks[0]
            dur = toks[1] if len(toks) > 1 else "1h"
            uid = None
            if target == "reply":
                try:
                    reply = await event.get_reply_message()
                    s = await reply.get_sender()
                    uid = getattr(s, "id", None)
                except Exception:
                    uid = None
            else:
                try:
                    uid = int(target)
                except ValueError:
                    uid = None
            if uid is None:
                await self._respond(event, "<blockquote><b>cannot resolve</b></blockquote>", parse_mode="html")
                return
            m = re.match(r"(\d+)([smhd])", dur)
            if not m:
                await self._respond(event, "<blockquote><b>bad duration</b></blockquote>", parse_mode="html")
                return
            n, u = int(m.group(1)), m.group(2)
            secs = n * {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]
            self._mute_user(uid, secs)
            self._audit_log(sender, "mute", f"{uid} {dur}")
            await self._respond(event, f"<blockquote><b>muted:</b> <code>{uid}</code> {dur}</blockquote>", parse_mode="html")
            return

        if action == "unmute":
            if not self._role_gte(role, "admin"):
                await self._respond(event, "<blockquote><b>admin+</b></blockquote>", parse_mode="html")
                return
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            uid = None
            if reply is not None:
                try:
                    s = await reply.get_sender()
                    uid = getattr(s, "id", None)
                except Exception:
                    uid = None
            if uid is None and len(parts) > 2:
                try:
                    uid = int(parts[2].split()[0])
                except Exception:
                    uid = None
            if uid is None:
                await self._respond(event, "<blockquote><b>cannot resolve</b></blockquote>", parse_mode="html")
                return
            self._unmute_user(uid)
            await self._respond(event, f"<blockquote><b>unmuted:</b> <code>{uid}</code></blockquote>", parse_mode="html")
            return

        if action == "add-contrib":
            if not self._role_gte(role, "contributor"):
                await self._respond(event, "<blockquote><b>contributor+</b></blockquote>", parse_mode="html")
                return
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat add-contrib &lt;name&gt; &lt;url&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].strip().lower()
            url = self._extract_url_from_text(parts[2])
            if not url.startswith(("http://", "https://")) or not self._is_ssrf_safe(url):
                await self._respond(event, "<blockquote><b>need valid url</b></blockquote>", parse_mode="html")
                return
            ok_limit, reason = self._check_quota(sender, "add")
            if not ok_limit:
                await self._respond(event, f"<blockquote><b>{html.escape(reason or 'quota exceeded')}</b></blockquote>", parse_mode="html")
                return
            pending = self.cfg.get("pending_sources", {}) or {}
            nid = str(int(self.cfg.get("pending_next_id", 1) or 1))
            pending[nid] = {"name": name, "url": url, "by": sender, "ts": time.time()}
            self.cfg.set("pending_sources", pending)
            self.cfg.set("pending_next_id", int(nid) + 1)
            await self._notify_owner_trusted(event, "add-contrib", f"{name} {url}")
            await self._respond(event, f"<blockquote><b>pending</b> <code>#{nid}</code>\n<i>waiting for owner</i></blockquote>", parse_mode="html")
            return

        if action == "pending":
            pending = self.cfg.get("pending_sources", {}) or {}
            if not pending:
                await self._respond(event, "<blockquote><b>empty queue</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>pending sources</b></blockquote>"]
            for pid, pdata in pending.items():
                out.append(f"<code>#{pid}</code> — <b>{html.escape(pdata.get('name', '?'))}</b> — <code>{html.escape(pdata.get('url', '')[:120])}</code> — by <code>{pdata.get('by')}</code>")
            out.append("")
            out.append(f"<i>approve: <code>{html.escape(p)}dothat approve &lt;id&gt;</code> | reject: <code>{html.escape(p)}dothat reject &lt;id&gt;</code></i>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "approve":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            if len(parts) < 2:
                await self._respond(event, "<blockquote><b>need id</b></blockquote>", parse_mode="html")
                return
            pid = parts[1].strip().lstrip("#")
            pending = self.cfg.get("pending_sources", {}) or {}
            pdata = pending.pop(pid, None)
            if not pdata:
                await self._respond(event, "<blockquote><b>not found</b></blockquote>", parse_mode="html")
                return
            sites = self._sites()
            sites[pdata["name"]] = {"url": pdata["url"], "host": urlparse(pdata["url"]).netloc, "alive": None}
            self._save_sites(sites)
            self.cfg.set("pending_sources", pending)
            await self._run_hook("on_sites_change", {"action": "add", "name": pdata["name"], "site": sites[pdata["name"]]})
            await self._respond(event, f"<blockquote><b>approved:</b> <code>{html.escape(pdata['name'])}</code></blockquote>", parse_mode="html")
            return

        if action == "reject":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            if len(parts) < 2:
                await self._respond(event, "<blockquote><b>need id</b></blockquote>", parse_mode="html")
                return
            pid = parts[1].strip().lstrip("#")
            pending = self.cfg.get("pending_sources", {}) or {}
            if pid in pending:
                del pending[pid]
                self.cfg.set("pending_sources", pending)
            await self._respond(event, f"<blockquote><b>rejected</b> <code>#{pid}</code></blockquote>", parse_mode="html")
            return

        if action == "multi":
            rest = args[len("multi"):].strip()
            queries = [q.strip() for q in rest.split("|") if q.strip()]
            if not queries:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat multi q1 | q2 | q3</code></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>running batch..</b></blockquote>", parse_mode="html")
            blocks = []
            for q in queries[:5]:
                ok, err = await self._search_everywhere(q, tag=tag_filter, actor=sender)
                header = f"<blockquote><b>{html.escape(q)}</b> — <code>{len(ok)} hits</code></blockquote>"
                body = self._format_results(q, ok)[0] if ok else self._no_result_text(err)
                blocks.append(header + "\n" + body)
            await self._respond(event, "\n\n".join(blocks), parse_mode="html")
            return

        if action == "trace":
            q = parts[1] if len(parts) > 1 else ""
            if not q:
                await self._respond(event, "<blockquote><b>need query.</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>tracing..</b></blockquote>", parse_mode="html")
            sites = self._sites()
            lines = [f"<blockquote><b>trace</b> {html.escape(q)}</blockquote>"]
            for name, site in list(sites.items())[:10]:
                if site.get("disabled"):
                    lines.append(f"⏸ <code>{html.escape(name)}</code> disabled")
                    continue
                url = self._build_url(self._apply_site_override(name, site), q)
                try:
                    page, status, elapsed = await self._fetch_async(url)
                    if self._is_cloudflare(page):
                        v = "☁ cloudflare"
                    elif self._is_captcha(page):
                        v = "🛡 captcha"
                    elif self._looks_js_required(page, page):
                        v = "⚠ js"
                    elif status >= 400:
                        v = f"🔴 http {status}"
                    else:
                        v = "✅ ok"
                    lines.append(f"{v} <code>{html.escape(name)}</code> — {elapsed}s, {len(page)}B")
                except Exception as e:
                    lines.append(f"🔴 <code>{html.escape(name)}</code> — {html.escape(type(e).__name__)}")
            await self._respond(event, "\n".join(lines), parse_mode="html")
            return

        if action == "profile":
            q = parts[1] if len(parts) > 1 else ""
            if not q:
                await self._respond(event, "<blockquote><b>need query.</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>profiling..</b></blockquote>", parse_mode="html")
            t0 = time.time()
            sites = self._sites()
            rows = []
            for name, site in sites.items():
                if site.get("disabled"):
                    continue
                url = self._build_url(self._apply_site_override(name, site), q)
                t1 = time.time()
                try:
                    page, status, elapsed = await self._fetch_async(url)
                    fetch_t = time.time() - t1
                    t2 = time.time()
                    self._extract(page, url)
                    parse_t = time.time() - t2
                    rows.append((name, round(fetch_t, 3), round(parse_t, 3), len(page)))
                except Exception:
                    rows.append((name, round(time.time() - t1, 3), 0.0, 0))
            rows.sort(key=lambda r: -r[1])
            out = [f"<blockquote><b>profile</b> {html.escape(q)} — total {round(time.time() - t0, 2)}s</blockquote>"]
            for n, ft, pt, sz in rows[:15]:
                out.append(f"<code>{html.escape(n)}</code> — fetch {ft}s, parse {pt}s, {sz}B")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "page":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat page &lt;n&gt; &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            try:
                page_n = max(0, int(parts[1]) - 1)
            except ValueError:
                await self._respond(event, "<blockquote><b>bad page number</b></blockquote>", parse_mode="html")
                return
            q = parts[2].strip()
            cached = self._cache_get(q + "||normal", actor=sender, chat_id=chat_id)
            if cached is None:
                ok, err = await self._search_everywhere(q, actor=sender, chat_id=chat_id)
            else:
                ok, err = cached, []
            if not ok:
                await self._respond(event, self._no_result_text(err), parse_mode="html")
                return
            text, total = self._format_results(q, ok, page=page_n)
            await self._respond(event, text, parse_mode="html")
            return

        if action == "openall":
            e = self._last_result or {}
            ok = e.get("ok") or []
            urls = [r["url"] for r in ok[:30]]
            if not urls:
                await self._respond(event, "<blockquote><b>nothing to open.</b></blockquote>", parse_mode="html")
                return
            chunks = []
            current = ""
            for u in urls:
                line = f"• {u}\n"
                if len(current) + len(line) > 3800:
                    chunks.append(current)
                    current = line
                else:
                    current += line
            if current:
                chunks.append(current)
            try:
                for chunk in chunks:
                    await event.client.send_message(event.chat_id, chunk[:4000])
            except Exception:
                pass
            return

        if action == "json":
            e = self._last_result or {}
            ok = e.get("ok") or []
            payload = json.dumps({"query": e.get("query"), "results": [{k: v for k, v in r.items() if k not in ("snippet_hl", "snippet_esc")} for r in ok]}, ensure_ascii=False, indent=2)
            try:
                await event.client.send_file(event.chat_id, payload.encode("utf-8"), file_name=f"dontdothat_{int(time.time())}.json")
            except Exception:
                pass
            return

        if action == "save":
            e = self._last_result or {}
            ok = e.get("ok") or []
            q = e.get("query") or ""
            tag = None
            sm = re.search(r"--tag=(\w+)", args)
            if sm:
                tag = sm.group(1)
            saved = self.cfg.get("saved_results", {}) or {}
            sid = hashlib.sha1((q + str(time.time())).encode()).hexdigest()[:10]
            saved[sid] = {"query": q, "ts": time.time(), "hits": len(ok), "tag": tag, "results": [{k: v for k, v in r.items() if k not in ("snippet_hl", "snippet_esc")} for r in ok[:50]]}
            self.cfg.set("saved_results", saved)
            await self._respond(event, f"<blockquote><b>saved as</b> <code>{sid}</code>{' (tag=' + html.escape(tag) + ')' if tag else ''}</blockquote>", parse_mode="html")
            return

        if action == "saved":
            saved = self.cfg.get("saved_results", {}) or {}
            if not saved:
                await self._respond(event, "<blockquote><b>no saved results.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>saved</b></blockquote>"]
            for sid, data in list(saved.items())[-20:]:
                t = time.strftime("%Y-%m-%d %H:%M", time.localtime(data.get("ts", 0)))
                tag = data.get("tag")
                tag_str = f" <i>[{html.escape(tag)}]</i>" if tag else ""
                out.append(f"<code>{sid}</code> — <code>{html.escape(data.get('query', ''))}</code> ({data.get('hits', 0)} hits){tag_str} — {t}")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "find-in-history":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat find-in-history &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            q = parts[1].strip()
            c = self._sqlite_conn()
            if c is None:
                await self._respond(event, "<blockquote><b>sqlite disabled.</b></blockquote>", parse_mode="html")
                return
            try:
                with self._sqlite_lock:
                    rows = c.execute("SELECT ts, query, hits FROM queries WHERE query LIKE ? ORDER BY ts DESC LIMIT 20", (f"%{q}%",)).fetchall()
            except Exception:
                rows = []
            if not rows:
                await self._respond(event, "<blockquote><b>nothing found.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>history search</b></blockquote>"]
            for ts, query, hits in rows:
                t = time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
                out.append(f"<code>{t}</code> — <code>{html.escape(query)}</code> (<i>{hits} hits</i>)")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "template":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat template add|list|run|remove &lt;name&gt; [query]</code></blockquote>", parse_mode="html")
                return
            sub = parts[1].lower()
            tail = parts[2] if len(parts) > 2 else ""
            templates = self.cfg.get("templates", {}) or {}
            if sub == "add":
                toks = tail.split(maxsplit=1)
                if len(toks) < 2:
                    await self._respond(event, "<blockquote><b>need name + query</b></blockquote>", parse_mode="html")
                    return
                tname, tquery = toks[0], toks[1]
                templates[tname] = {"query": tquery, "ts": time.time(), "by": sender}
                self.cfg.set("templates", templates)
                await self._respond(event, f"<blockquote><b>template saved:</b> <code>{html.escape(tname)}</code></blockquote>", parse_mode="html")
                return
            if sub == "list":
                if not templates:
                    await self._respond(event, "<blockquote><b>no templates.</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>templates</b></blockquote>"]
                for tname, data in templates.items():
                    out.append(f"<code>{html.escape(tname)}</code> — <code>{html.escape(data.get('query', '')[:100])}</code>")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return
            if sub == "run":
                tname = tail.strip()
                if tname not in templates:
                    await self._respond(event, "<blockquote><b>not found</b></blockquote>", parse_mode="html")
                    return
                q = templates[tname].get("query", "")
                if not q:
                    await self._respond(event, "<blockquote><b>empty query</b></blockquote>", parse_mode="html")
                    return
                ok, err = await self._search_everywhere(q, actor=sender)
                await self._send_result(event, q, ok, err)
                return
            if sub == "remove":
                tname = tail.strip()
                if tname in templates:
                    del templates[tname]
                    self.cfg.set("templates", templates)
                await self._respond(event, f"<blockquote><b>removed:</b> <code>{html.escape(tname)}</code></blockquote>", parse_mode="html")
                return
            return

        if action == "backup":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            payload = json.dumps(self._build_backup(), ensure_ascii=False, indent=2).encode("utf-8")
            payload = self._encrypt_data(payload)
            try:
                self._backup_path().write_bytes(payload)
            except Exception:
                pass
            try:
                await event.client.send_file(event.chat_id, payload, file_name=f"dontdothat_backup_{int(time.time())}.json")
            except Exception as e:
                await self._respond(event, f"<blockquote><b>backup failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
            return

        if action == "restore":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is None:
                await self._respond(event, "<blockquote><b>reply to backup json.</b></blockquote>", parse_mode="html")
                return
            try:
                raw = await reply.download_media(bytes)
                raw = self._decrypt_data(raw)
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("backup must be object")
            except Exception as e:
                await self._respond(event, f"<blockquote><b>restore failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
                return
            if isinstance(data.get("sites"), dict):
                self._save_sites(data["sites"])
            for key in ("roles", "notes", "saved_results", "synonyms", "watchers", "blocked_queries", "blocked_users", "allowed_chats", "plugin_trust_overrides", "trusted_plugin_authors", "privileged_plugin_authors", "templates", "plugins_metadata"):
                if key in data:
                    self.cfg.set(key, data[key])
            if isinstance(data.get("stats"), dict):
                self._stats.update(data["stats"])
            if isinstance(data.get("history"), list):
                self._history = data["history"][-int(self.cfg.get("history_size", 50) or 50):]
            self._save_persistent_state()
            await self._run_hook("on_restore", {"data": data})
            await self._respond(event, "<blockquote><b>restore ok.</b></blockquote>", parse_mode="html")
            return

        if args.startswith("@"):
            src_m = re.match(r"@([\w,\-]+)\s+(.+)$", args, re.DOTALL)
            if src_m:
                names = [n.strip().lower() for n in src_m.group(1).split(",") if n.strip()]
                query = src_m.group(2).strip()
                sites = self._sites()
                selected = {n: sites[n] for n in names if n in sites}
                if not selected:
                    await self._respond(event, "<blockquote><b>no matching sources.</b></blockquote>", parse_mode="html")
                    return
                await self._log_search(event, query)
                await self._respond(event, "<blockquote><b>doing that..</b></blockquote>", parse_mode="html")
                tasks = [self._search_site(n, s, query) for n, s in selected.items()]
                raw = await asyncio.gather(*tasks, return_exceptions=True)
                ok = [r for r in raw if isinstance(r, dict) and "__error__" not in r]
                err = [r for r in raw if isinstance(r, dict) and "__error__" in r]
                for r in ok:
                    r["score"] = self._bm25_score(r, query, ok, selected.get(r["name"], {}))
                ok.sort(key=lambda r: r.get("score", 0), reverse=True)
                await self._send_result(event, query, ok, err)
                return
            query = args
            if self._query_forbidden(query):
                await self._respond(event, "<blockquote><b>forbidden query</b></blockquote>", parse_mode="html")
                return
            await self._log_search(event, query)
            self._audit_log(sender, "search", query)
            ok_limit, key = self._check_quota_pre(sender, "search")
            if not ok_limit:
                await self._respond(event, "<blockquote><b>quota exceeded</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>doing that..</b></blockquote>", parse_mode="html")
            ok, err = await self._search_everywhere(query, tag=tag_filter, actor=sender, chat_id=chat_id)
            if ok or err:
                self._check_quota_commit(sender, key)
            await self._send_result(event, query, ok, err)
            return

        admin_actions = {
            "add", "add-api", "remove", "sites", "info", "heal", "doctor", "stat", "import", "export",
            "enable", "disable", "rename", "clone", "clear", "tag", "priority", "tags", "weight",
            "ping", "dead", "slow", "slow-source", "audit", "cfg", "install", "plugins", "plugin", "logs",
            "watch", "note", "notes", "snapshot", "diff", "dashboard", "metrics", "latency", "trust-list",
        }
        read_actions = {"sites", "stat", "tags", "info", "top", "dashboard", "latency", "trust-list"}
        if action in admin_actions:
            if action in read_actions:
                if not self._role_gte(role, "viewer"):
                    await self._respond(event, "<blockquote><b>access denied</b></blockquote>", parse_mode="html")
                    return
            elif action in ("cfg", "install", "plugins", "plugin", "import", "clear"):
                if action == "cfg":
                    if len(parts) > 2:
                        if not self._role_gte(role, "owner"):
                            await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                            return
                    else:
                        if not self._role_gte(role, "superadmin"):
                            await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                            return
                else:
                    if not self._role_gte(role, "superadmin"):
                        await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                        return
            else:
                if not self._role_gte(role, "editor"):
                    await self._respond(event, "<blockquote><b>editor+</b></blockquote>", parse_mode="html")
                    return

        if action == "install":
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            forced_name = None
            if len(parts) > 1:
                forced_name = parts[1].strip().lower().replace(" ", "_")
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is None and len(parts) > 1:
                ok, info = await self._repo_install(parts[1])
                if ok:
                    await self._respond(event, f"<blockquote><b>from repo:</b> <code>{html.escape(info.get('declared_name', parts[1]))}</code>\n<b>version:</b> <code>{html.escape(info.get('version', '?'))}</code>\n<b>trust:</b> <code>{html.escape(info.get('trust_level', 'sandboxed'))}</code></blockquote>", parse_mode="html")
                else:
                    await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(info))}</code></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>installing..</b></blockquote>", parse_mode="html")
            ok, reg_name, info = await self._install_plugin_from_reply(event, forced_name=forced_name)
            if ok:
                self._audit_log(sender, "plugin_install", reg_name)
                declared = info.get("declared_name", reg_name)
                version = info.get("version") or "?"
                author = info.get("author") or "?"
                trust = info.get("trust_level", "sandboxed")
                hooks = ",".join(info.get("hooks") or []) or "-"
                missing = info.get("missing_hooks") or []
                miss_str = f"\n<b>missing hooks:</b> <code>{html.escape(','.join(missing))}</code>" if missing else ""
                await self._respond(event, f"<blockquote><b>Plugin {html.escape(declared)} installed!</b>\n<b>Version:</b> <code>{html.escape(version)}</code>\n<b>Author:</b> <code>{html.escape(author)}</code>\n<b>Trust:</b> <code>{html.escape(trust)}</code>\n<b>Hooks:</b> <code>{html.escape(hooks)}</code>{miss_str}\n<b>Key:</b> <code>{html.escape(reg_name)}</code></blockquote>", parse_mode="html")
            else:
                await self._respond(event, f"<blockquote><b>install failed:</b> <code>{html.escape(str(reg_name))}</code></blockquote>", parse_mode="html")
            return

        if action == "plugins":
            trust_filter = None
            tm2 = re.search(r"--trust=(\w+)", args)
            if tm2:
                trust_filter = tm2.group(1).lower()
            if not self._plugins:
                await self._respond(event, "<blockquote><b>no plugins installed.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>plugins</b></blockquote>"]
            shown = 0
            for k, v in self._plugins.items():
                trust = v.get("trust_level", "sandboxed")
                if trust_filter and trust != trust_filter:
                    continue
                shown += 1
                st = "🟢" if v.get("enabled") else "🔴"
                emoji = {"sandboxed": "🔒", "trusted": "🔓", "privileged": "👑"}.get(trust, "?")
                dn = v.get("declared_name") or v.get("name") or k
                out.append(f"{st}{emoji} <b>{html.escape(dn)}</b> v{html.escape(v.get('version', '?'))} — <code>{html.escape(k)}</code> — <i>{trust}</i>")
            if shown == 0:
                out.append("<i>no plugins matching filter.</i>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "plugin":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat plugin info|remove|reload|enable|disable|search|install|update|upgrade-all|refresh-index|trust|trust-list &lt;name&gt;</code></blockquote>", parse_mode="html")
                return
            sub = parts[1].lower()
            tail = parts[2] if len(parts) > 2 else ""

            if sub == "trust":
                if not self._role_gte(role, "owner"):
                    await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                    return
                toks = tail.split()
                if len(toks) < 2:
                    await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat plugin trust &lt;name&gt; &lt;sandboxed|trusted|privileged&gt;</code></blockquote>", parse_mode="html")
                    return
                name, level = toks[0], toks[1].lower()
                key = self._find_plugin(name)
                if key is None:
                    await self._respond(event, f"<blockquote><b>not found:</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
                    return
                if self._set_plugin_trust(key, level):
                    self._audit_log(sender, "plugin_trust", f"{key} {level}")
                    await self._respond(event, f"<blockquote><b>{html.escape(key)}</b> → <code>{html.escape(level)}</code></blockquote>", parse_mode="html")
                else:
                    await self._respond(event, "<blockquote><b>failed</b></blockquote>", parse_mode="html")
                return

            if sub == "trust-list":
                if not self._role_gte(role, "viewer"):
                    await self._respond(event, "<blockquote><b>viewer+</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>plugin trust</b></blockquote>"]
                for k, v in self._plugins.items():
                    trust = v.get("trust_level", "sandboxed")
                    author = v.get("author", "?")
                    access = ",".join(v.get("access") or []) or "-"
                    source = v.get("source", "local")
                    emoji = {"sandboxed": "🔒", "trusted": "🔓", "privileged": "👑"}.get(trust, "?")
                    out.append(f"{emoji} <b>{html.escape(k)}</b> — <code>{trust}</code> — {html.escape(author)} — src=<code>{html.escape(source)}</code> — <i>access: {html.escape(access)}</i>")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return

            if sub in ("info", "remove", "reload", "enable", "disable"):
                raw = tail.strip()
                if not raw:
                    await self._respond(event, "<blockquote><b>need name.</b></blockquote>", parse_mode="html")
                    return
                key = self._find_plugin(raw)
                if key is None:
                    await self._respond(event, f"<blockquote><b>plugin not found:</b> <code>{html.escape(raw)}</code></blockquote>", parse_mode="html")
                    return
                info = self._plugins[key]
                if sub == "info":
                    dn = info.get("declared_name") or info.get("name") or key
                    trust = info.get("trust_level", "sandboxed")
                    access = ",".join(info.get("access") or []) or "-"
                    source = info.get("source", "local")
                    sha = (info.get("sha256") or "")[:16]
                    missing = ",".join(info.get("missing_hooks") or []) or "-"
                    await self._respond(event, f"<blockquote><b>{html.escape(dn)}</b>\n<b>description:</b> {html.escape(info.get('description') or '-')}\n<b>version:</b> <code>{html.escape(info.get('version', '?'))}</code>\n<b>author:</b> <code>{html.escape(info.get('author', '?'))}</code>\n<b>trust:</b> <code>{html.escape(trust)}</code>\n<b>access:</b> <code>{html.escape(access)}</code>\n<b>source:</b> <code>{html.escape(source)}</code>\n<b>sha256:</b> <code>{html.escape(sha)}...</code>\n<b>hooks:</b> <code>{html.escape(','.join(info.get('hooks') or []) or '-')}</code>\n<b>missing:</b> <code>{html.escape(missing)}</code>\n<b>enabled:</b> <code>{info.get('enabled')}</code>\n<b>key:</b> <code>{html.escape(key)}</code></blockquote>", parse_mode="html")
                    return
                if sub == "remove":
                    self._unregister_plugin_hooks(key)
                    try:
                        Path(info["path"]).unlink()
                    except Exception:
                        pass
                    self._audit_log(sender, "plugin_remove", key)
                    await self._respond(event, f"<blockquote><b>plugin removed:</b> <code>{html.escape(key)}</code></blockquote>", parse_mode="html")
                    return
                if sub == "reload":
                    self._unregister_plugin_hooks(key)
                    ok, msg, _ = await self._load_plugin_from_path(Path(info["path"]))
                    await self._respond(event, f"<blockquote><b>reload {html.escape(key)}:</b> <code>{html.escape(msg)}</code></blockquote>", parse_mode="html")
                    return
                if sub == "enable":
                    info["enabled"] = True
                    await self._respond(event, f"<blockquote><b>enabled:</b> <code>{html.escape(key)}</code></blockquote>", parse_mode="html")
                    return
                if sub == "disable":
                    info["enabled"] = False
                    await self._respond(event, f"<blockquote><b>disabled:</b> <code>{html.escape(key)}</code></blockquote>", parse_mode="html")
                    return

            if sub == "search":
                q = tail.strip()
                if not q:
                    await self._respond(event, "<blockquote><b>need query.</b></blockquote>", parse_mode="html")
                    return
                await self._repo_index(force=True)
                data = await self._repo_index()
                if not data:
                    await self._respond(event, "<blockquote><b>repo unavailable.</b></blockquote>", parse_mode="html")
                    return
                matches = []
                ql = q.lower()
                for pl in data.get("plugins", []):
                    hay = (str(pl.get("name", "")) + " " + str(pl.get("description", "")) + " " + " ".join(pl.get("tags") or [])).lower()
                    if ql in hay:
                        matches.append(pl)
                if not matches:
                    await self._respond(event, "<blockquote><b>no matches.</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>repo search</b></blockquote>"]
                for pl in matches:
                    access = ",".join(pl.get("access") or []) or "-"
                    mc = pl.get("min_core") or "-"
                    out.append(f"<b>{html.escape(str(pl.get('name', '?')))}</b> v{html.escape(str(pl.get('version', '?')))} — <code>{html.escape(str(pl.get('author', '?')))}</code> — access=<code>{html.escape(access)}</code> — min_core=<code>{html.escape(mc)}</code>")
                out.append("")
                out.append(f"<i>install: <code>{html.escape(p)}dothat plugin install &lt;name&gt;</code></i>")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return

            if sub == "install":
                if not self._role_gte(role, "superadmin"):
                    await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                    return
                tail_clean, flags = self._parse_flags(tail)
                name = tail_clean.strip()
                if not name:
                    await self._respond(event, "<blockquote><b>need name.</b></blockquote>", parse_mode="html")
                    return
                trust_override = flags.get("trust") if isinstance(flags.get("trust"), str) else None
                ok, info = await self._repo_install(name, trust_override=trust_override)
                if ok:
                    self._audit_log(sender, "plugin_install_repo", name)
                    await self._respond(event, f"<blockquote><b>Plugin {html.escape(info.get('declared_name', name))} installed from repo!</b>\n<b>Version:</b> <code>{html.escape(info.get('version', '?'))}</code>\n<b>Trust:</b> <code>{html.escape(info.get('trust_level', 'sandboxed'))}</code></blockquote>", parse_mode="html")
                else:
                    await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(info))}</code></blockquote>", parse_mode="html")
                return

            if sub == "update":
                if not self._role_gte(role, "superadmin"):
                    await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                    return
                name = tail.strip() or None
                updated = await self._repo_update(name)
                if not updated:
                    await self._respond(event, "<blockquote><b>no updates available.</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>updated</b></blockquote>"]
                for n, old, new in updated:
                    out.append(f"<b>{html.escape(n)}</b>: {html.escape(str(old))} → {html.escape(str(new))}")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return

            if sub == "upgrade-all":
                if not self._role_gte(role, "superadmin"):
                    await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                    return
                updated = await self._repo_update(None)
                if not updated:
                    await self._respond(event, "<blockquote><b>nothing to update.</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>upgraded</b></blockquote>"]
                for n, old, new in updated:
                    out.append(f"<b>{html.escape(n)}</b>: {html.escape(str(old))} → {html.escape(str(new))}")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return

            if sub == "refresh-index":
                if not self._role_gte(role, "superadmin"):
                    await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                    return
                await self._repo_index(force=True)
                await self._respond(event, "<blockquote><b>index refreshed.</b></blockquote>", parse_mode="html")
                return

            await self._respond(event, "<blockquote><b>unknown plugin subcommand.</b></blockquote>", parse_mode="html")
            return

        if action == "logs":
            c = self._sqlite_conn()
            if c is None:
                await self._respond(event, "<blockquote><b>sqlite log disabled.</b></blockquote>", parse_mode="html")
                return
            limit = 15
            if len(parts) > 1:
                try:
                    limit = int(parts[1])
                except ValueError:
                    pass
            try:
                with self._sqlite_lock:
                    rows = c.execute("SELECT ts, source, url, status, elapsed, size, blocked, verdict FROM fetches ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
            except Exception as e:
                await self._respond(event, f"<blockquote><b>error:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
                return
            if not rows:
                await self._respond(event, "<blockquote><b>no fetch logs yet.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>recent fetches</b></blockquote>"]
            for ts, src, url, status, elapsed, size, blocked, verdict in rows:
                mark = "🛡" if blocked else "✅"
                out.append(f"{mark} <code>{html.escape(src)}</code> — <code>{status}</code> {elapsed}s {size}B — <i>{html.escape(verdict or '')}</i>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "dashboard":
            s = self._stats
            sites = self._sites()
            alive = sum(1 for x in sites.values() if x.get("alive"))
            dead = sum(1 for x in sites.values() if x.get("alive") is False)
            dis = sum(1 for x in sites.values() if x.get("disabled"))
            total_fails = sum((s.get("per_source_fail") or {}).values())
            plugins_by_trust = {"sandboxed": 0, "trusted": 0, "privileged": 0}
            for v in self._plugins.values():
                t = v.get("trust_level", "sandboxed")
                plugins_by_trust[t] = plugins_by_trust.get(t, 0) + 1
            await self._respond(event, f"<blockquote><b>dashboard</b></blockquote>\n<b>queries:</b> <code>{s['total_queries']}</code>\n<b>sources hit:</b> <code>{s['total_sources_hit']}</code>\n<b>plugins:</b> <code>{len(self._plugins)}</code> (🔒{plugins_by_trust.get('sandboxed', 0)} 🔓{plugins_by_trust.get('trusted', 0)} 👑{plugins_by_trust.get('privileged', 0)})\n<b>sites total:</b> <code>{len(sites)}</code> (🟢{alive} 🔴{dead} ⏸{dis})\n<b>fails:</b> <code>{total_fails}</code>\n<b>dead services:</b> <code>{', '.join(self._dead_services) or '-'}</code>", parse_mode="html")
            return

        if action == "latency":
            percs = self._latency_percentiles()
            if not percs:
                await self._respond(event, "<blockquote><b>no latency data.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>latency</b></blockquote>"]
            rows = sorted(percs.items(), key=lambda kv: -kv[1]["p95"])
            for src, pp in rows[:20]:
                out.append(f"<code>{html.escape(src)}</code> — p50 <code>{pp['p50']:.2f}s</code> p95 <code>{pp['p95']:.2f}s</code> p99 <code>{pp['p99']:.2f}s</code> n=<code>{pp['n']}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "slow-source":
            percs = self._latency_percentiles()
            if not percs:
                await self._respond(event, "<blockquote><b>no latency data.</b></blockquote>", parse_mode="html")
                return
            rows = sorted(percs.items(), key=lambda kv: -kv[1]["p95"])[:15]
            out = ["<blockquote><b>slow sources</b></blockquote>"]
            for src, pp in rows:
                out.append(f"<code>{pp['p95']:.2f}s</code> p95 / <code>{pp['p50']:.2f}s</code> p50 — <code>{html.escape(src)}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "metrics":
            if len(parts) < 2 or parts[1].lower() != "export":
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat metrics export [--since=7d] [--format=csv|json]</code></blockquote>", parse_mode="html")
                return
            c = self._sqlite_conn()
            if c is None:
                await self._respond(event, "<blockquote><b>sqlite disabled.</b></blockquote>", parse_mode="html")
                return
            since = time.time() - 7 * 86400
            m = re.search(r"--since=(\d+)([dh])", args)
            if m:
                n = int(m.group(1))
                unit = m.group(2)
                since = time.time() - n * (86400 if unit == "d" else 3600)
            fmt = "csv"
            fm = re.search(r"--format=(\w+)", args)
            if fm:
                fmt = fm.group(1).lower()
            try:
                with self._sqlite_lock:
                    rows = c.execute("SELECT source, COUNT(*), SUM(blocked), AVG(elapsed), AVG(size) FROM fetches WHERE ts>? GROUP BY source", (since,)).fetchall()
            except Exception:
                rows = []
            if not rows:
                await self._respond(event, "<blockquote><b>no data.</b></blockquote>", parse_mode="html")
                return
            if fmt == "json":
                payload = json.dumps([{"source": r[0], "total": r[1], "blocked": r[2] or 0, "avg_elapsed": round(r[3] or 0, 3), "avg_size": round(r[4] or 0, 1)} for r in rows], ensure_ascii=False, indent=2).encode("utf-8")
                fname = "dontdothat_metrics.json"
            else:
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["source", "total", "blocked", "avg_elapsed", "avg_size"])
                for r in rows:
                    writer.writerow([r[0], r[1], r[2] or 0, round(r[3] or 0, 3), round(r[4] or 0, 1)])
                payload = buf.getvalue().encode("utf-8")
                fname = "dontdothat_metrics.csv"
            try:
                await event.client.send_file(event.chat_id, payload, file_name=fname)
            except Exception as e:
                await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
            return

        if action == "snapshot":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat snapshot &lt;name&gt; &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            query = parts[2].strip()
            site = self._sites().get(name)
            if not site:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            url = self._build_url(site, query)
            try:
                page, status, elapsed = await self._fetch_async(url)
                if self._is_cloudflare(page) or self._is_captcha(page):
                    await self._respond(event, "<blockquote><b>snapshot failed: page is blocked</b></blockquote>", parse_mode="html")
                    return
                self._sqlite_save_snapshot(name, query, url, page)
                await self._respond(event, f"<blockquote><b>snapshot saved</b>\n<code>{html.escape(name)}</code> / {html.escape(query)} / {len(page)}B</blockquote>", parse_mode="html")
            except Exception as e:
                await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
            return

        if action == "diff":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat diff &lt;name&gt; &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            c = self._sqlite_conn()
            if c is None:
                await self._respond(event, "<blockquote><b>sqlite disabled.</b></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            query = parts[2].strip()
            try:
                with self._sqlite_lock:
                    rows = c.execute("SELECT ts, html FROM snapshots WHERE source=? AND query=? ORDER BY ts DESC LIMIT 2", (name, query)).fetchall()
            except Exception:
                rows = []
            if len(rows) < 2:
                await self._respond(event, "<blockquote><b>need at least 2 snapshots.</b></blockquote>", parse_mode="html")
                return
            old_ts, old_html = rows[1]
            new_ts, new_html = rows[0]
            to, txo, _, _, _, _ = self._extract(old_html, "")
            tn, txn, _, _, _, _ = self._extract(new_html, "")
            added = len(txn) - len(txo)
            await self._respond(event, f"<blockquote><b>diff</b> {html.escape(name)} / {html.escape(query)}\n<b>old:</b> <code>{time.strftime('%Y-%m-%d %H:%M', time.localtime(old_ts))}</code> — {len(txo)}B\n<b>new:</b> <code>{time.strftime('%Y-%m-%d %H:%M', time.localtime(new_ts))}</code> — {len(txn)}B\n<b>delta:</b> <code>{'+' if added >= 0 else ''}{added}</code></blockquote>", parse_mode="html")
            return

        if action == "note":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat note add|remove &lt;url&gt; [text]</code></blockquote>", parse_mode="html")
                return
            sub = parts[1].lower()
            if sub == "add":
                if len(parts) < 3:
                    await self._respond(event, "<blockquote><b>need url + text</b></blockquote>", parse_mode="html")
                    return
                toks = parts[2].split(maxsplit=1)
                if len(toks) < 2:
                    await self._respond(event, "<blockquote><b>need url + text</b></blockquote>", parse_mode="html")
                    return
                url, text = toks[0], toks[1]
                notes = self.cfg.get("notes") or {}
                notes[url] = {"text": text, "ts": time.time(), "by": sender}
                self.cfg.set("notes", notes)
                await self._respond(event, f"<blockquote><b>note saved</b> for <code>{html.escape(url[:100])}</code></blockquote>", parse_mode="html")
                return
            if sub == "remove":
                if len(parts) < 3:
                    await self._respond(event, "<blockquote><b>need url</b></blockquote>", parse_mode="html")
                    return
                url = parts[2].strip()
                notes = self.cfg.get("notes") or {}
                if url in notes:
                    del notes[url]
                    self.cfg.set("notes", notes)
                await self._respond(event, f"<blockquote><b>removed:</b> <code>{html.escape(url[:100])}</code></blockquote>", parse_mode="html")
                return
            await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat note add|remove &lt;url&gt; [text]</code></blockquote>", parse_mode="html")
            return

        if action == "notes":
            notes = self.cfg.get("notes") or {}
            if not notes:
                await self._respond(event, "<blockquote><b>no notes.</b></blockquote>", parse_mode="html")
                return
            search = parts[1].lower() if len(parts) > 1 else ""
            out = ["<blockquote><b>notes</b></blockquote>"]
            shown = 0
            for url, data in list(notes.items()):
                txt = (url + " " + data.get("text", "")).lower()
                if search and search not in txt:
                    continue
                ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(data.get("ts", 0)))
                out.append(f"<code>{ts}</code> — {html.escape(url[:80])}\n<i>{html.escape(data.get('text', ''))}</i>")
                shown += 1
                if shown >= 20:
                    break
            if shown == 0:
                out.append("<i>no matches.</i>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "watch":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat watch add|list|remove|run &lt;...&gt;</code></blockquote>", parse_mode="html")
                return
            sub = parts[1].lower()
            tail = parts[2] if len(parts) > 2 else ""
            ws = self.cfg.get("watchers") or []
            if sub == "add":
                new_only = "--new-only" in tail
                changed_only = "--changed" in tail
                tail = re.sub(r"--\w+", "", tail).strip()
                m = re.match(r"(.+?)\s+every\s+(\d+)([smhd])$", tail)
                if not m:
                    await self._respond(event, "<blockquote><b>format: query every 1h</b></blockquote>", parse_mode="html")
                    return
                q, n, u = m.group(1).strip(), int(m.group(2)), m.group(3)
                mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}[u]
                wid = hashlib.sha1((q + str(time.time())).encode()).hexdigest()[:8]
                ws.append({"id": wid, "query": q, "interval": n * mult, "next_run": time.time() + n * mult, "seen": [], "new_only": new_only, "changed": changed_only})
                self.cfg.set("watchers", ws)
                await self._respond(event, f"<blockquote><b>watch added</b> <code>{html.escape(wid)}</code></blockquote>", parse_mode="html")
                return
            if sub == "list":
                if not ws:
                    await self._respond(event, "<blockquote><b>no watchers.</b></blockquote>", parse_mode="html")
                    return
                out = ["<blockquote><b>watchers</b></blockquote>"]
                for w in ws:
                    nxt = time.strftime("%Y-%m-%d %H:%M", time.localtime(w.get("next_run", 0)))
                    out.append(f"<code>{html.escape(w['id'])}</code> — <code>{html.escape(w['query'])}</code> — {nxt}")
                out.append("")
                out.append(f"<i>remove: <code>{html.escape(p)}dothat watch remove &lt;id&gt;</code> | run now: <code>{html.escape(p)}dothat watch run &lt;id&gt;</code> | run all: <code>{html.escape(p)}dothat watch run --all</code></i>")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return
            if sub == "remove":
                wid = tail.strip()
                new = [w for w in ws if w.get("id") != wid]
                self.cfg.set("watchers", new)
                await self._respond(event, f"<blockquote><b>removed:</b> <code>{html.escape(wid)}</code></blockquote>", parse_mode="html")
                return
            if sub == "run":
                tail_clean = tail.strip()
                if tail_clean in ("--all", "all"):
                    await self._respond(event, "<blockquote><b>running all..</b></blockquote>", parse_mode="html")
                    for w in ws:
                        w["next_run"] = 0
                    self.cfg.set("watchers", ws)
                    await self._watch_runner_once(None)
                    await self._respond(event, "<blockquote><b>done</b></blockquote>", parse_mode="html")
                    return
                wid = tail_clean
                if not wid:
                    await self._respond(event, "<blockquote><b>need id</b></blockquote>", parse_mode="html")
                    return
                await self._respond(event, f"<blockquote><b>running</b> <code>{html.escape(wid)}</code>..</blockquote>", parse_mode="html")
                await self._watch_runner_once(wid)
                await self._respond(event, "<blockquote><b>done</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>unknown watch subcommand.</b></blockquote>", parse_mode="html")
            return

        if action in ("all", "fast", "deep"):
            mode = action
            q = parts[1] if len(parts) > 1 else ""
            if not q:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat {mode} &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            if self._query_forbidden(q):
                await self._respond(event, "<blockquote><b>forbidden query</b></blockquote>", parse_mode="html")
                return
            await self._log_search(event, q)
            ok_limit, key = self._check_quota_pre(sender, "search")
            if not ok_limit:
                await self._respond(event, "<blockquote><b>quota exceeded</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>doing that..</b></blockquote>", parse_mode="html")
            ok, err = await self._search_everywhere(q, tag=tag_filter, mode=mode, actor=sender, chat_id=chat_id)
            if ok or err:
                self._check_quota_commit(sender, key)
            await self._send_result(event, q, ok, err)
            return

        if action == "search":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat search &lt;name&gt; &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            query = parts[2].strip()
            site = self._sites().get(name)
            if not site:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            await self._log_search(event, query)
            await self._respond(event, "<blockquote><b>doing that..</b></blockquote>", parse_mode="html")
            r = await self._search_site(name, site, query)
            if isinstance(r, dict) and "__error__" in r:
                await self._respond(event, f"<blockquote><b>failed..</b>\n<i>{html.escape(r.get('error', 'fetch failed'))}</i></blockquote>", parse_mode="html")
                return
            await self._respond(event, self._format_results(query, [r])[0], parse_mode="html")
            return

        if action == "raw":
            if len(parts) < 3:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat raw &lt;name&gt; &lt;query&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            query = parts[2].strip()
            site = self._sites().get(name)
            if not site:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            url = self._build_url(site, query)
            try:
                page, status, elapsed = await self._fetch_async(url)
            except Exception as e:
                await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
                return
            await self._respond(event, f"<blockquote><b>raw {html.escape(name)}</b>\n<b>status:</b> <code>{status}</code> | <b>elapsed:</b> <code>{elapsed}s</code>\n<b>size:</b> <code>{len(page)}B</code></blockquote>\n<pre>{html.escape(page[:3500])}</pre>", parse_mode="html")
            return

        if action == "retry":
            last = self._last_result.get("query") if self._last_result else None
            if not last:
                await self._respond(event, "<blockquote><b>nothing to retry.</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>retrying..</b></blockquote>", parse_mode="html")
            self._cache.pop(self._cache_key(last + "||normal", actor=sender), None)
            ok, err = await self._search_everywhere(last, actor=sender, chat_id=chat_id)
            await self._send_result(event, last, ok, err)
            return

        if action == "history":
            target_actor = None
            if len(parts) > 1 and self._role_gte(role, "admin"):
                target_actor = parts[1].strip()
            if not self._history:
                await self._respond(event, "<blockquote><b>no history.</b></blockquote>", parse_mode="html")
                return
            lines = ["<blockquote><b>recent queries</b></blockquote>"]
            for h in self._history[-20:][::-1]:
                if target_actor and h.get("actor") != target_actor:
                    continue
                ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(h["ts"]))
                actor_str = f" <code>{html.escape(h.get('actor', '?'))}</code>" if self._role_gte(role, "admin") else ""
                lines.append(f"<code>{ts}</code> — <code>{html.escape(h['query'])}</code> (<i>{h['hits']} hits, {h['errors']} err</i>){actor_str}")
            await self._respond(event, "\n".join(lines), parse_mode="html")
            return

        if action == "add":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><b>need name + url.</b>\n<code>{html.escape(p)}dothat add &lt;name&gt; &lt;url&gt; [--param=q] [--tag=x] [--priority=high]</code></blockquote>", parse_mode="html")
                return
            name = parts[1].strip().lower()
            tail = parts[2].strip() if len(parts) > 2 else ""
            tail, flags = self._parse_flags(tail)
            url = self._extract_url_from_text(tail)
            if not url:
                reply = None
                try:
                    reply = await event.get_reply_message()
                except Exception:
                    reply = None
                if reply is not None:
                    url = self._extract_url_from_text(getattr(reply, "raw_text", "") or "")
            if not url:
                await self._respond(event, "<blockquote><b>need url.</b></blockquote>", parse_mode="html")
                return
            if not url.startswith(("http://", "https://")) or not self._is_ssrf_safe(url):
                await self._respond(event, "<blockquote><b>nah.</b></blockquote>", parse_mode="html")
                return
            parsed = urlparse(url)
            if not parsed.netloc:
                await self._respond(event, "<blockquote><b>nah.</b></blockquote>", parse_mode="html")
                return
            entry = {"url": url, "host": parsed.netloc, "alive": None}
            if "param" in flags and isinstance(flags["param"], str):
                entry["param"] = flags["param"]
            if "tag" in flags and isinstance(flags["tag"], str):
                entry["tags"] = [flags["tag"]]
            if "priority" in flags and isinstance(flags["priority"], str):
                entry["priority"] = flags["priority"]
            ok_limit, reason = self._check_quota(sender, "add")
            if not ok_limit:
                await self._respond(event, f"<blockquote><b>{html.escape(reason or 'quota exceeded')}</b></blockquote>", parse_mode="html")
                return
            sites = self._sites()
            sites[name] = entry
            self._save_sites(sites)
            self._audit_log(sender, "add", f"{name} {url}")
            await self._run_hook("on_sites_change", {"action": "add", "name": name, "site": entry})
            await self._respond(event, f"<blockquote><b>source added: {html.escape(name)}</b>\n<b>url:</b> <code>{html.escape(url)}</code></blockquote>", parse_mode="html")
            return

        if action == "add-api":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><b>need name + preset|url</b>\npresets: {', '.join(API_PRESETS.keys())}</blockquote>", parse_mode="html")
                return
            name = parts[1].strip().lower()
            tail = parts[2].strip() if len(parts) > 2 else ""
            tail, flags = self._parse_flags(tail)
            if not tail and name in API_PRESETS:
                preset = copy.deepcopy(API_PRESETS[name])
                preset["host"] = urlparse(preset["url"]).netloc
                preset["alive"] = None
                preset["type"] = "api"
                preset["tags"] = ["api"]
                sites = self._sites()
                sites[name] = preset
                self._save_sites(sites)
                await self._run_hook("on_sites_change", {"action": "add", "name": name, "site": preset})
                await self._respond(event, f"<blockquote><b>api source added:</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
                return
            url = self._extract_url_from_text(tail)
            if not url.startswith(("http://", "https://")) or not self._is_ssrf_safe(url):
                await self._respond(event, "<blockquote><b>need valid http(s) url or preset</b></blockquote>", parse_mode="html")
                return
            parsed = urlparse(url)
            entry = {
                "url": url, "host": parsed.netloc, "alive": None,
                "type": "json",
                "path": flags.get("path") if isinstance(flags.get("path"), str) else None,
                "title_field": flags.get("title_field") if isinstance(flags.get("title_field"), str) else None,
                "url_field": flags.get("url_field") if isinstance(flags.get("url_field"), str) else None,
                "desc_field": flags.get("desc_field") if isinstance(flags.get("desc_field"), str) else None,
                "param": flags.get("param") if isinstance(flags.get("param"), str) else None,
                "tags": [flags["tag"]] if isinstance(flags.get("tag"), str) else ["api"],
            }
            sites = self._sites()
            sites[name] = entry
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "add", "name": name, "site": entry})
            await self._respond(event, f"<blockquote><b>api source added:</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
            return

        if action == "remove":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat remove &lt;name&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>nothing here.</b></blockquote>", parse_mode="html")
                return
            if trusted and self.cfg.get("require_approval_for_remove", True):
                pending = self.cfg.get("pending_actions", {}) or {}
                aid = hashlib.sha1((name + str(time.time())).encode()).hexdigest()[:8]
                pending[aid] = {"action": "remove", "name": name, "by": sender, "ts": time.time()}
                self.cfg.set("pending_actions", pending)
                await self._notify_owner_trusted(event, "remove-request", f"source: {name}")
                await self._respond(event, f"<blockquote><b>remove requested</b> <code>{aid}</code></blockquote>", parse_mode="html")
                return
            del sites[name]
            self._save_sites(sites)
            self._audit_log(sender, "remove", name)
            await self._run_hook("on_sites_change", {"action": "remove", "name": name})
            await self._respond(event, "<blockquote><b>gone.</b></blockquote>", parse_mode="html")
            return

        if action == "enable":
            name = parts[1].lower() if len(parts) > 1 else ""
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[name]["disabled"] = False
            self._stats["per_source_fail"][name] = 0
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "enable", "name": name})
            await self._respond(event, f"<blockquote><b>enabled:</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
            return

        if action == "disable":
            name = parts[1].lower() if len(parts) > 1 else ""
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[name]["disabled"] = True
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "disable", "name": name})
            await self._respond(event, f"<blockquote><b>disabled:</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
            return

        if action == "rename":
            tail = parts[1] if len(parts) == 2 else (f"{parts[1]} {parts[2]}" if len(parts) > 1 else "")
            names = tail.split()
            if len(names) < 2:
                await self._respond(event, "<blockquote><b>need old + new.</b></blockquote>", parse_mode="html")
                return
            old, new = names[0].lower(), names[1].lower()
            sites = self._sites()
            if old not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[new] = sites.pop(old)
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "rename", "old": old, "new": new})
            await self._respond(event, f"<blockquote><b>renamed:</b> <code>{html.escape(old)}</code> → <code>{html.escape(new)}</code></blockquote>", parse_mode="html")
            return

        if action == "clone":
            tail = parts[1] if len(parts) == 2 else (f"{parts[1]} {parts[2]}" if len(parts) > 1 else "")
            names = tail.split()
            if len(names) < 2:
                await self._respond(event, "<blockquote><b>need old + new.</b></blockquote>", parse_mode="html")
                return
            old, new = names[0].lower(), names[1].lower()
            sites = self._sites()
            if old not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[new] = copy.deepcopy(sites[old])
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "clone", "old": old, "new": new})
            await self._respond(event, f"<blockquote><b>cloned:</b> <code>{html.escape(old)}</code> → <code>{html.escape(new)}</code></blockquote>", parse_mode="html")
            return

        if action == "clear":
            self._save_sites({})
            self._audit_log(sender, "clear", "")
            await self._run_hook("on_sites_change", {"action": "clear"})
            await self._respond(event, "<blockquote><b>all sources cleared.</b></blockquote>", parse_mode="html")
            return

        if action == "tag":
            tail = parts[1] if len(parts) == 2 else (f"{parts[1]} {parts[2]}" if len(parts) > 1 else "")
            toks = tail.split()
            if len(toks) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat tag &lt;name&gt; [+|-]tag</code></blockquote>", parse_mode="html")
                return
            name, tag_spec = toks[0].lower(), toks[1]
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            tags = list(sites[name].get("tags") or [])
            if tag_spec.startswith("-"):
                tags = [x for x in tags if x != tag_spec[1:]]
            elif tag_spec.startswith("+"):
                if tag_spec[1:] not in tags:
                    tags.append(tag_spec[1:])
            else:
                if tag_spec not in tags:
                    tags.append(tag_spec)
            sites[name]["tags"] = tags
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "tag", "name": name, "tags": tags})
            await self._respond(event, f"<blockquote><b>{html.escape(name)}</b> tags: <code>{html.escape(','.join(tags) or '-')}</code></blockquote>", parse_mode="html")
            return

        if action == "priority":
            tail = parts[1] if len(parts) == 2 else (f"{parts[1]} {parts[2]}" if len(parts) > 1 else "")
            toks = tail.split()
            if len(toks) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat priority &lt;name&gt; high|normal|low</code></blockquote>", parse_mode="html")
                return
            name, level = toks[0].lower(), toks[1].lower()
            if level not in ("high", "normal", "low"):
                await self._respond(event, "<blockquote><b>level must be high|normal|low.</b></blockquote>", parse_mode="html")
                return
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[name]["priority"] = level
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "priority", "name": name, "priority": level})
            await self._respond(event, f"<blockquote><b>{html.escape(name)}</b> priority: <code>{html.escape(level)}</code></blockquote>", parse_mode="html")
            return

        if action == "weight":
            tail = parts[1] if len(parts) == 2 else (f"{parts[1]} {parts[2]}" if len(parts) > 1 else "")
            toks = tail.split()
            if len(toks) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat weight &lt;name&gt; &lt;float&gt;</code></blockquote>", parse_mode="html")
                return
            name = toks[0].lower()
            try:
                weight = float(toks[1])
            except ValueError:
                await self._respond(event, "<blockquote><b>bad weight</b></blockquote>", parse_mode="html")
                return
            sites = self._sites()
            if name not in sites:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            sites[name]["weight"] = weight
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "weight", "name": name, "weight": weight})
            await self._respond(event, f"<blockquote><b>{html.escape(name)}</b> weight: <code>{weight}</code></blockquote>", parse_mode="html")
            return

        if action == "tags":
            sites = self._sites()
            all_tags = {}
            for n, s in sites.items():
                for t in s.get("tags") or []:
                    all_tags.setdefault(t, []).append(n)
            if not all_tags:
                await self._respond(event, "<blockquote><b>no tags.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>tags</b></blockquote>"]
            for t, names in sorted(all_tags.items()):
                out.append(f"<code>{html.escape(t)}</code> — {', '.join(html.escape(n) for n in names)}")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "sites":
            page = 0
            if len(parts) > 1:
                try:
                    page = max(0, int(parts[1]) - 1)
                except ValueError:
                    pass
            await self._respond(event, self._sites_text(page), parse_mode="html")
            return

        if action == "info":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat info &lt;name&gt;</code></blockquote>", parse_mode="html")
                return
            name = parts[1].lower()
            site = self._sites().get(name)
            if not site:
                await self._respond(event, "<blockquote><b>404.</b></blockquote>", parse_mode="html")
                return
            param = site.get("param") or self.cfg.get("default_param", "q")
            alive = site.get("alive")
            mark = "🟢 alive" if alive else ("🔴 dead" if alive is False else "⚪ unknown")
            tags = ",".join(site.get("tags") or []) or "-"
            prio = site.get("priority") or "normal"
            dis = "yes" if site.get("disabled") else "no"
            weight = site.get("weight", 1.0)
            await self._respond(event, f"<blockquote><b>{html.escape(name)}</b></blockquote>\n<b>host:</b> <code>{html.escape(site.get('host', '?'))}</code>\n<b>url:</b> <code>{html.escape(site.get('url', ''))}</code>\n<b>param:</b> <code>{html.escape(param)}</code>\n<b>tags:</b> <code>{html.escape(tags)}</code>\n<b>priority:</b> <code>{html.escape(prio)}</code>\n<b>weight:</b> <code>{weight}</code>\n<b>disabled:</b> <code>{dis}</code>\n<b>status:</b> {mark}", parse_mode="html")
            return

        if action == "ping":
            sites = self._sites()
            if not sites:
                await self._respond(event, "<blockquote><b>empty af.</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>pinging..</b></blockquote>", parse_mode="html")
            rows = []
            sem = asyncio.Semaphore(5)

            async def check(name, site):
                async with sem:
                    started = time.time()
                    try:
                        alive = await asyncio.wait_for(asyncio.to_thread(self._ping, self._build_url(site, "test")), timeout=12)
                    except Exception:
                        alive = False
                    rows.append((name, alive, round(time.time() - started, 2)))

            await asyncio.gather(*(check(n, s) for n, s in sites.items()))
            rows.sort(key=lambda r: r[0])
            out = ["<blockquote><b>ping</b></blockquote>"]
            for name, alive, el in rows:
                out.append(f"{'🟢' if alive else '🔴'} <code>{html.escape(name)}</code> — {el}s")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action in ("heal", "doctor"):
            sites = self._sites()
            if not sites:
                await self._respond(event, "<blockquote><b>empty af.</b></blockquote>", parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>checking sources..</b></blockquote>", parse_mode="html")
            sem = asyncio.Semaphore(5)
            rows = []
            st = {"ch": False}

            async def probe(name, site):
                async with sem:
                    url = self._build_url(self._apply_site_override(name, site), "test")
                    started = time.time()
                    try:
                        page, status, _ = await self._fetch_async(url)
                        elapsed = round(time.time() - started, 2)
                        size = len(page)
                        if self._is_cloudflare(page):
                            verdict = "☁ cloudflare"
                            alive = False
                        elif self._is_captcha(page):
                            verdict = "🛡 captcha"
                            alive = True
                        elif self._looks_js_required(page, page):
                            verdict = "⚠ needs js"
                            alive = True
                        elif status >= 400:
                            verdict = f"🔴 http {status}"
                            alive = False
                        else:
                            verdict = "✅ ok"
                            alive = True
                    except Exception as e:
                        elapsed = round(time.time() - started, 2)
                        size = 0
                        verdict = f"🔴 {type(e).__name__}"
                        alive = False
                    if site.get("alive") != alive:
                        site["alive"] = alive
                        st["ch"] = True
                    rows.append((name, verdict, elapsed, size))

            await asyncio.gather(*(probe(n, s) for n, s in sites.items()))
            if st["ch"]:
                self._save_sites(sites)
            rows.sort(key=lambda r: r[0])
            out = [f"<blockquote><b>{action} report</b></blockquote>"]
            for name, verdict, elapsed, size in rows:
                out.append(f"{verdict} <code>{html.escape(name)}</code> — {elapsed}s, {size}B")
            if action == "doctor":
                deep = "--deep" in args
                if deep:
                    out.append("")
                    out.append("<blockquote><b>deep checks</b></blockquote>")
                    c = self._sqlite_conn()
                    if c is None:
                        out.append("❌ sqlite disabled")
                    else:
                        try:
                            with self._sqlite_lock:
                                c.execute("PRAGMA quick_check").fetchone()
                            out.append("✅ sqlite OK")
                        except Exception as e:
                            out.append(f"❌ sqlite: {html.escape(str(e))}")
                    deps = []
                    for nm, ok in (("curl_cffi", _HAS_CURL), ("httpx", _HAS_HTTPX), ("pymorphy2", _MORPH is not None)):
                        deps.append(f"{nm}={'✓' if ok else '✗'}")
                    out.append(f"deps: <code>{' '.join(deps)}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "dead":
            sites = self._sites()
            dead = [n for n, s in sites.items() if s.get("alive") is False]
            if not dead:
                await self._respond(event, "<blockquote><b>no dead sources.</b></blockquote>", parse_mode="html")
                return
            text = "<blockquote><b>dead sources:</b></blockquote>\n" + "\n".join(f"• <code>{html.escape(n)}</code>" for n in dead)
            text += f"\n\n<i>enable: <code>{html.escape(p)}dothat enable &lt;name&gt;</code></i>"
            await self._respond(event, text, parse_mode="html")
            return

        if action == "slow":
            sites = self._sites()
            if not sites:
                await self._respond(event, "<blockquote><b>empty.</b></blockquote>", parse_mode="html")
                return
            percs = self._latency_percentiles()
            if percs:
                out = ["<blockquote><b>slowest (by p95)</b></blockquote>"]
                for src, pp in sorted(percs.items(), key=lambda kv: -kv[1]["p95"])[:15]:
                    out.append(f"<code>{pp['p95']:.2f}s</code> (p50 {pp['p50']:.2f}s) — <code>{html.escape(src)}</code>")
                await self._respond(event, "\n".join(out), parse_mode="html")
                return
            await self._respond(event, "<blockquote><b>measuring..</b></blockquote>", parse_mode="html")
            sem = asyncio.Semaphore(5)
            rows = []

            async def measure(name, site):
                async with sem:
                    started = time.time()
                    try:
                        await self._fetch_async(self._build_url(site, "test"))
                        rows.append((name, round(time.time() - started, 2)))
                    except Exception:
                        rows.append((name, 999.0))

            await asyncio.gather(*(measure(n, s) for n, s in sites.items()))
            rows.sort(key=lambda r: -r[1])
            out = ["<blockquote><b>slowest</b></blockquote>"]
            for name, el in rows[:15]:
                out.append(f"<code>{el}s</code> — <code>{html.escape(name)}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "stat":
            s = self._stats
            top = sorted(s["top_queries"].items(), key=lambda x: -x[1])[:10]
            tl = "\n".join(f"• <code>{html.escape(q)}</code> — <code>{n}</code>" for q, n in top) or "<i>no queries yet</i>"
            per = sorted(s.get("per_source", {}).items(), key=lambda x: -x[1])[:10]
            pl = "\n".join(f"• <code>{html.escape(k)}</code> — <code>{v}</code>" for k, v in per) or "<i>-</i>"
            fails = s.get("per_source_fail", {})
            fails_total = sum(fails.values())
            await self._respond(event, f"<blockquote><b>stat</b></blockquote>\n<b>queries:</b> <code>{s['total_queries']}</code>\n<b>sources hit:</b> <code>{s['total_sources_hit']}</code>\n<b>fails:</b> <code>{fails_total}</code>\n<b>plugins:</b> <code>{len(self._plugins)}</code>\n<b>sites:</b> <code>{len(self._sites())}</code>\n<b>top queries:</b>\n{tl}\n<b>top sources:</b>\n{pl}", parse_mode="html")
            return

        if action == "top":
            per = sorted(self._stats.get("per_source", {}).items(), key=lambda x: -x[1])[:20]
            if not per:
                await self._respond(event, "<blockquote><b>no data.</b></blockquote>", parse_mode="html")
                return
            out = ["<blockquote><b>top sources</b></blockquote>"]
            for i, (k, v) in enumerate(per, 1):
                out.append(f"{i}. <code>{html.escape(k)}</code> — <code>{v}</code>")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "audit":
            if not self._audit:
                await self._respond(event, "<blockquote><b>no audit records.</b></blockquote>", parse_mode="html")
                return
            n = 30
            if len(parts) > 1:
                try:
                    n = max(1, min(200, int(parts[1])))
                except ValueError:
                    pass
            action_filter = None
            actor_filter = None
            af = re.search(r"--action=(\w+)", args)
            if af:
                action_filter = af.group(1)
            uf = re.search(r"--actor=(\S+)", args)
            if uf:
                actor_filter = uf.group(1)
            out = ["<blockquote><b>audit</b></blockquote>"]
            for rec in self._audit[-n:][::-1]:
                if action_filter and rec.get("action") != action_filter:
                    continue
                if actor_filter and rec.get("actor") != actor_filter:
                    continue
                ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(rec["ts"]))
                out.append(f"<code>{ts}</code> <b>{html.escape(rec['action'])}</b> by <code>{html.escape(rec['actor'])}</code> — {html.escape(rec['details'])}")
            await self._respond(event, "\n".join(out), parse_mode="html")
            return

        if action == "cfg":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat cfg &lt;key&gt; [value] | &lt;key&gt; --reset</code></blockquote>", parse_mode="html")
                return
            tail = parts[1] if len(parts) == 2 else f"{parts[1]} {parts[2]}"
            tail_clean, flags = self._parse_flags(tail)
            toks = tail_clean.split(maxsplit=1)
            key = toks[0]
            if flags.get("reset"):
                if not self._role_gte(role, "owner"):
                    await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                    return
                defaults = self.config.get(key)
                if defaults is None and key not in self.config:
                    await self._respond(event, "<blockquote><b>no default for key</b></blockquote>", parse_mode="html")
                    return
                self.cfg.set(key, defaults)
                self._audit_log(sender, "cfg_reset", key)
                await self._respond(event, f"<blockquote><b>{html.escape(key)}</b> reset to <code>{html.escape(json.dumps(defaults, ensure_ascii=False))}</code></blockquote>", parse_mode="html")
                return
            if len(toks) == 1 and not flags.get("json"):
                val = self.cfg.get(key)
                await self._respond(event, f"<blockquote><b>{html.escape(key)}</b> = <code>{html.escape(json.dumps(val, ensure_ascii=False))}</code></blockquote>", parse_mode="html")
                return
            if not self._role_gte(role, "owner"):
                await self._respond(event, "<blockquote><b>owner only</b></blockquote>", parse_mode="html")
                return
            raw = toks[1].strip() if len(toks) > 1 else ""
            try:
                parsed_val = json.loads(raw)
            except Exception:
                parsed_val = raw
            self.cfg.set(key, parsed_val)
            self._audit_log(sender, "cfg", f"{key}={raw[:100]}")
            if key == "plugins_repo":
                self._repo_index_cache = {}
            if key == "max_parallel":
                self._sem = None
                self._sem_limit = None
            await self._respond(event, f"<blockquote><b>{html.escape(key)}</b> set to <code>{html.escape(str(parsed_val))}</code></blockquote>", parse_mode="html")
            return

        if action == "export":
            fmt = "json"
            m = re.search(r"--format=(\w+)", args)
            if m:
                fmt = m.group(1).lower()
            sites = self._sites()
            if fmt == "json":
                data = json.dumps(sites, ensure_ascii=False, indent=2).encode("utf-8")
                fname = "dontdothat_sites.json"
            elif fmt == "jsonl":
                lines = [json.dumps({k: v}, ensure_ascii=False) for k, v in sites.items()]
                data = "\n".join(lines).encode("utf-8")
                fname = "dontdothat_sites.jsonl"
            elif fmt == "csv":
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["name", "url", "host", "param", "tags", "priority", "disabled", "type"])
                for n, s in sites.items():
                    writer.writerow([n, s.get("url", ""), s.get("host", ""), s.get("param", ""), "|".join(s.get("tags") or []), s.get("priority", ""), str(bool(s.get("disabled"))), s.get("type", "html")])
                data = buf.getvalue().encode("utf-8")
                fname = "dontdothat_sites.csv"
            elif fmt == "md":
                lines = ["# DontDoThat sources", ""]
                for n, s in sites.items():
                    lines += [f"## {n}", f"- url: `{s.get('url', '')}`", f"- host: `{s.get('host', '')}`", f"- tags: {', '.join(s.get('tags') or [])}", ""]
                data = "\n".join(lines).encode("utf-8")
                fname = "dontdothat_sites.md"
            elif fmt == "html":
                rows = "".join(f"<tr><td>{html.escape(n)}</td><td>{html.escape(s.get('url', ''))}</td><td>{html.escape(s.get('host', ''))}</td></tr>" for n, s in sites.items())
                data = f"<html><body><table border=1>{rows}</table></body></html>".encode("utf-8")
                fname = "dontdothat_sites.html"
            elif fmt == "misp":
                payload = {"Attribute": [{"type": "url", "value": s.get("url", "")} for s in sites.values()]}
                data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
                fname = "dontdothat_misp.json"
            else:
                await self._respond(event, "<blockquote><b>format must be json|jsonl|csv|md|html|misp</b></blockquote>", parse_mode="html")
                return
            try:
                if len(data) < 4000:
                    try:
                        await self._respond(event, f"<blockquote><b>export ({html.escape(fname)})</b></blockquote>\n<pre>{html.escape(data.decode('utf-8'))}</pre>", parse_mode="html")
                        return
                    except Exception:
                        pass
                await event.client.send_file(event.chat_id, data, file_name=fname)
            except Exception as e:
                await self._respond(event, f"<blockquote><b>export failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
            return

        if action == "import":
            if not self._role_gte(role, "superadmin"):
                await self._respond(event, "<blockquote><b>superadmin+</b></blockquote>", parse_mode="html")
                return
            reply = None
            try:
                reply = await event.get_reply_message()
            except Exception:
                reply = None
            if reply is None:
                await self._respond(event, "<blockquote><b>reply to a json file.</b></blockquote>", parse_mode="html")
                return
            try:
                data = await reply.download_media(bytes)
                parsed = json.loads(data.decode("utf-8"))
            except Exception as e:
                await self._respond(event, f"<blockquote><b>import failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
                return
            sites = self._sites()
            added = 0
            if isinstance(parsed, dict):
                for name, entry in parsed.items():
                    if isinstance(entry, dict) and "url" in entry and self._is_ssrf_safe(entry["url"]):
                        sites[name] = entry
                        added += 1
            elif isinstance(parsed, list):
                for entry in parsed:
                    if isinstance(entry, dict) and "url" in entry and "name" in entry and self._is_ssrf_safe(entry["url"]):
                        sites[entry["name"]] = entry
                        added += 1
            self._save_sites(sites)
            await self._run_hook("on_sites_change", {"action": "import", "count": added})
            await self._respond(event, f"<blockquote><b>imported:</b> <code>{added}</code></blockquote>", parse_mode="html")
            return

        if action == "test":
            if len(parts) < 2:
                await self._respond(event, f"<blockquote><code>{html.escape(p)}dothat test &lt;url&gt; [--param=q] [--save]</code></blockquote>", parse_mode="html")
                return
            tail = parts[1] if len(parts) == 2 else f"{parts[1]} {parts[2]}"
            tail, flags = self._parse_flags(tail)
            url = self._extract_url_from_text(tail)
            if not url.startswith(("http://", "https://")) or not self._is_ssrf_safe(url):
                await self._respond(event, "<blockquote><b>need a valid http(s) url.</b></blockquote>", parse_mode="html")
                return
            site = {"url": url}
            if "param" in flags and isinstance(flags["param"], str):
                site["param"] = flags["param"]
            test_url = self._build_url(site, "test")
            await self._respond(event, f"<blockquote><b>testing..</b>\n<code>{html.escape(test_url)}</code></blockquote>", parse_mode="html")
            started = time.time()
            try:
                page, status, _ = await self._fetch_async(test_url)
            except Exception as e:
                await self._respond(event, f"<blockquote><b>failed:</b> <code>{html.escape(str(e)[:200])}</code></blockquote>", parse_mode="html")
                return
            elapsed = round(time.time() - started, 2)
            size = len(page)
            if self._is_cloudflare(page):
                verdict = "☁ cloudflare (refused)"
                ok_flag = False
            elif self._is_captcha(page):
                verdict = "🛡 captcha"
                ok_flag = False
            elif self._looks_js_required(page, page):
                verdict = "⚠ needs js"
                ok_flag = False
            elif status >= 400:
                verdict = f"🔴 http {status}"
                ok_flag = False
            else:
                verdict = "✅ ok"
                ok_flag = True
            title, text, links, files, images, meta = self._extract(page, test_url)
            if flags.get("save") and ok_flag:
                name = re.sub(r"[^\w]+", "_", urlparse(test_url).netloc).strip("_").lower() or "test_src"
                sites = self._sites()
                entry = {"url": url, "host": urlparse(url).netloc, "alive": True, "priority": "normal", "tags": ["web"]}
                if "param" in flags and isinstance(flags["param"], str):
                    entry["param"] = flags["param"]
                sites[name] = entry
                self._save_sites(sites)
                await self._run_hook("on_sites_change", {"action": "add", "name": name, "site": entry})
                await self._respond(event, f"<blockquote><b>saved as</b> <code>{html.escape(name)}</code></blockquote>", parse_mode="html")
                return
            await self._respond(event, f"<blockquote><b>test result</b></blockquote>\n<b>url:</b> <code>{html.escape(test_url)}</code>\n<b>status:</b> <code>{status}</code>\n<b>elapsed:</b> <code>{elapsed}s</code>\n<b>size:</b> <code>{size}B</code>\n<b>title:</b> {html.escape(title or '-')}\n<b>links:</b> <code>{len(links)}</code> | <b>files:</b> <code>{len(files)}</code> | <b>images:</b> <code>{len(images)}</code>\n<b>verdict:</b> {verdict}\n<i>{html.escape(text[:400])}</i>", parse_mode="html")
            return

        sites = self._sites()
        if not sites:
            await self._respond(event, "<blockquote><b>empty af.</b>\n<i>no sources added.</i></blockquote>", parse_mode="html")
            return

        if self._query_forbidden(args):
            await self._respond(event, "<blockquote><b>forbidden query</b></blockquote>", parse_mode="html")
            return

        await self._log_search(event, args)
        self._audit_log(sender, "search", args)
        ok_limit, key = self._check_quota_pre(sender, "search")
        if not ok_limit:
            await self._respond(event, "<blockquote><b>quota exceeded</b></blockquote>", parse_mode="html")
            return
        await self._respond(event, "<blockquote><b>doing that..</b></blockquote>", parse_mode="html")
        ok, err = await self._search_everywhere(args, tag=tag_filter, actor=sender, chat_id=chat_id)
        if ok or err:
            self._check_quota_commit(sender, key)
        if to_chat:
            try:
                text, _ = self._format_results(args, ok)
                await event.client.send_message(to_chat, text if ok else self._no_result_text(err), parse_mode="html")
                await self._respond(event, "<blockquote><b>sent.</b></blockquote>", parse_mode="html")
            except Exception as e:
                await self._respond(event, f"<blockquote><b>send failed:</b> <code>{html.escape(str(e))}</code></blockquote>", parse_mode="html")
            return
        await self._send_result(event, args, ok, err)


module = DontDoThat