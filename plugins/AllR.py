PLUGIN = {
    "name": "AllR",
    "version": "1.0.0",
    "author": "@flexOwnerAL",
    "description": "just an extension that expandes the dontdothat functions",
    "min_core": "6.7.0",
    "access": ["module"],
    "tags": ["pre", "post", "byp", "js", "err", "res", "srch", "cmd", "life", "site"],
    "hooks": [
        "before_fetch", "after_fetch", "on_blocked", "on_js_required",
        "on_error", "on_result", "on_search", "on_command",
        "on_start", "on_stop", "on_sites_change", "on_plugin_load", "on_plugin_unload",
    ],
}

import asyncio
import base64
import hashlib
import json
import math
import os
import random
import re
import time
from urllib.parse import quote_plus, urlparse, urlunparse, parse_qsl, urlencode

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
    from readability import Document as _ReadableDoc
    _HAS_READABILITY = True
except Exception:
    _ReadableDoc = None
    _HAS_READABILITY = False

try:
    from trafilatura import extract as _trafilatura_extract
    _HAS_TRAFILATURA = True
except Exception:
    _trafilatura_extract = None
    _HAS_TRAFILATURA = False

try:
    import pymorphy2 as _pm
    _MORPH = _pm.MorphAnalyzer()
except Exception:
    _MORPH = None

try:
    from natasha import (
        Segmenter, MorphVocab, NewsEmbedding, NewsNERTagger, Doc as _NatashaDoc,
    )
    _NATASHA_SEG = Segmenter()
    _NATASHA_VOCAB = MorphVocab()
    _NATASHA_EMB = NewsEmbedding()
    _NATASHA_NER = NewsNERTagger(_NATASHA_EMB)
    _HAS_NATASHA = True
except Exception:
    _HAS_NATASHA = False

try:
    import spacy as _spacy
    _SPACY = None
    try:
        _SPACY = _spacy.load("en_core_web_sm")
    except Exception:
        _SPACY = None
    _HAS_SPACY = _SPACY is not None
except Exception:
    _HAS_SPACY = False

try:
    from langdetect import detect as _langdetect
    _HAS_LANGDETECT = True
except Exception:
    _langdetect = None
    _HAS_LANGDETECT = False

try:
    from datasketch import MinHash, MinHashLSH
    _HAS_DATASKETCH = True
except Exception:
    MinHash = None
    MinHashLSH = None
    _HAS_DATASKETCH = False

try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lex_rank import LexRankSummarizer
    _HAS_SUMY = True
except Exception:
    PlaintextParser = None
    Tokenizer = None
    LexRankSummarizer = None
    _HAS_SUMY = False

try:
    from google.cloud import translate_v2 as _gtranslate
    _HAS_GTRANS = True
except Exception:
    _gtranslate = None
    _HAS_GTRANS = False

try:
    import translators as _translators
    _HAS_TRANSLATORS = True
except Exception:
    _translators = None
    _HAS_TRANSLATORS = False


_TOR_HOST_PATTERN = re.compile(r"\.onion$", re.IGNORECASE)
_BASE64_BLOB = re.compile(r"([A-Za-z0-9+/=]{40,})")
_HEX_BLOB = re.compile(r"\b[0-9a-fA-F]{32,}\b")
_TRACKER_PATTERNS = (
    re.compile(r"(?is)<img[^>]+(?:src|href)=[\"'][^\"']*(?:pixel|track|analytics|beacon)[^\"']*[\"'][^>]*>"),
    re.compile(r"(?is)<script[^>]+src=[\"'][^\"']*(?:google-analytics|googletagmanager|hotjar|mixpanel|segment|amplitude|matomo)[^\"']*[\"'][^>]*>.*?</script>"),
    re.compile(r"(?is)<iframe[^>]+src=[\"'][^\"']*(?:doubleclick|adsystem|adservice)[^\"']*[\"'][^>]*>.*?</iframe>"),
)
_AD_PATTERNS = (
    re.compile(r"(?is)<div[^>]+(?:class|id)=[\"'][^\"']*(?:^|[\s_-])(?:ad|ads|advert|banner|sponsor|promo)(?:[\s_-]|$)[^\"']*[\"'][^>]*>.*?</div>"),
    re.compile(r"(?is)<aside[^>]*>.*?</aside>"),
)
_AMP_PATTERN = re.compile(r"(?i)<(?:html|link)[^>]+amp[^>]*>")

_UA_POOL = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 16; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
)

_STATE = {
    "url_cache": {},
    "seen_urls": set(),
    "rate_map": {},
    "warmup_done": False,
    "start_ts": None,
    "session_stats": {"fetches": 0, "blocked": 0, "js": 0, "errors": 0, "results": 0},
}

_URL_CACHE_MAX = 500
_SEEN_MAX = 5000
_DEDUP_THRESHOLD = 0.85

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "referer", "referrer", "fbclid", "gclid", "yclid", "mc_eid",
    "igshid", "si", "spm", "_ga", "_gl", "trk", "trkCampaign",
}

_MIRRORS = {
    "twitter.com": "nitter.net",
    "www.twitter.com": "nitter.net",
    "x.com": "nitter.net",
    "www.x.com": "nitter.net",
    "reddit.com": "old.reddit.com",
    "www.reddit.com": "old.reddit.com",
    "youtube.com": "invidious.snopyta.org",
    "www.youtube.com": "invidious.snopyta.org",
    "medium.com": "scribe.rip",
    "instagram.com": "bibliogram.art",
    "www.instagram.com": "bibliogram.art",
}


def _now():
    return time.time()


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def _sha256(s: bytes) -> str:
    return hashlib.sha256(s).hexdigest()


def _trim_cache():
    if len(_STATE["url_cache"]) > _URL_CACHE_MAX:
        items = sorted(_STATE["url_cache"].items(), key=lambda kv: kv[1]["ts"])
        for k, _ in items[: _URL_CACHE_MAX // 2]:
            _STATE["url_cache"].pop(k, None)
    if len(_STATE["seen_urls"]) > _SEEN_MAX:
        _STATE["seen_urls"] = set(list(_STATE["seen_urls"])[-_SEEN_MAX // 2 :])


def _normalize_url(url: str) -> str:
    try:
        p = urlparse(url)
    except Exception:
        return url
    scheme = (p.scheme or "https").lower()
    netloc = p.netloc.lower()
    path = p.path or "/"
    query_pairs = parse_qsl(p.query, keep_blank_values=False)
    query_pairs = [(k, v) for k, v in query_pairs if k.lower() not in _TRACKING_PARAMS]
    query = urlencode(query_pairs)
    return urlunparse((scheme, netloc, path, "", query, ""))


def _mirror_url(url: str) -> str:
    try:
        p = urlparse(url)
    except Exception:
        return url
    host = p.netloc.lower()
    mirror = _MIRRORS.get(host)
    if not mirror:
        return url
    return urlunparse((p.scheme, mirror, p.path, p.params, p.query, p.fragment))


def _is_tor(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return bool(_TOR_HOST_PATTERN.search(host))


def _region_of(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return "en"
    if host.endswith(".ru") or host.endswith(".рф"):
        return "ru"
    if host.endswith(".cn"):
        return "cn"
    if host.endswith(".de"):
        return "de"
    if host.endswith(".fr"):
        return "fr"
    if host.endswith(".es"):
        return "es"
    return "en"


def _lang_header_for(url: str, query: str) -> str:
    region = _region_of(url)
    if region == "ru":
        return "ru-RU,ru;q=0.9,en;q=0.8"
    if region == "cn":
        return "zh-CN,zh;q=0.9,en;q=0.8"
    if region == "de":
        return "de-DE,de;q=0.9,en;q=0.8"
    if region == "fr":
        return "fr-FR,fr;q=0.9,en;q=0.8"
    if region == "es":
        return "es-ES,es;q=0.9,en;q=0.8"
    if query:
        try:
            if re.search(r"[а-яА-Я]", query):
                return "ru-RU,ru;q=0.9,en;q=0.8"
            if re.search(r"[\u4e00-\u9fff]", query):
                return "zh-CN,zh;q=0.9,en;q=0.8"
        except Exception:
            pass
    return "en-US,en;q=0.9"


def _lemmatize(text: str) -> str:
    if _MORPH is None or not text:
        return text.lower()
    out = []
    for w in re.findall(r"\w+", text.lower()):
        if len(w) <= 2:
            out.append(w)
            continue
        try:
            out.append(_MORPH.parse(w)[0].normal_form)
        except Exception:
            out.append(w)
    return " ".join(out)


def _decode_b64_blobs(html: str) -> str:
    def _try(m):
        blob = m.group(1)
        if len(blob) % 4:
            return blob
        try:
            decoded = base64.b64decode(blob, validate=False).decode("utf-8", errors="ignore")
            if sum(c.isprintable() for c in decoded) / max(len(decoded), 1) > 0.8 and len(decoded) > 8:
                return decoded
        except Exception:
            pass
        return blob
    try:
        return _BASE64_BLOB.sub(_try, html)
    except Exception:
        return html


def _strip_trackers(html: str) -> str:
    for rx in _TRACKER_PATTERNS:
        try:
            html = rx.sub(" ", html)
        except Exception:
            continue
    return html


def _strip_ads(html: str) -> str:
    for rx in _AD_PATTERNS:
        try:
            html = rx.sub(" ", html)
        except Exception:
            continue
    return html


def _clean_html(html: str) -> str:
    try:
        html = re.sub(r"(?is)<!--.*?-->", " ", html)
        html = re.sub(r"(?is)<script.*?</script>", " ", html)
        html = re.sub(r"(?is)<style.*?</style>", " ", html)
        html = re.sub(r"(?is)<noscript.*?</noscript>", " ", html)
        html = re.sub(r"(?is)<svg.*?</svg>", " ", html)
        html = re.sub(r"\n{3,}", "\n\n", html)
        html = re.sub(r"[ \t]{2,}", " ", html)
    except Exception:
        pass
    return html


def _deamp(html: str) -> str:
    if not _AMP_PATTERN.search(html):
        return html
    try:
        html = re.sub(r"(?i)<link[^>]+rel=[\"']amphtml[\"'][^>]*>", "", html)
        html = re.sub(r"(?i)\bamp-", "", html)
        html = re.sub(r"(?i)<amp-img[^>]+src=[\"']([^\"']+)[\"'][^>]*>", r'<img src="\1">', html)
    except Exception:
        pass
    return html


def _extract_readable(html: str) -> str:
    out = None
    if _HAS_TRAFILATURA:
        try:
            out = _trafilatura_extract(html, output_format="html", include_links=True, include_images=False, include_tables=True)
        except Exception:
            out = None
    if not out and _HAS_READABILITY:
        try:
            out = _ReadableDoc(html).summary()
        except Exception:
            out = None
    return out or html


def _extract_meta(html: str) -> dict:
    meta = {}
    patterns = {
        "og_title": r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        "og_desc": r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        "og_image": r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        "author": r'<meta[^>]+name=["\']author["\'][^>]+content=["\']([^"\']+)["\']',
        "date": r'<meta[^>]+property=["\']article:published_time["\'][^>]+content=["\']([^"\']+)["\']',
        "desc": r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        "lang": r'<html[^>]+lang=["\']([^"\']+)["\']',
    }
    for k, pat in patterns.items():
        try:
            m = re.search(pat, html, re.IGNORECASE)
            if m:
                meta[k] = m.group(1).strip()[:300]
        except Exception:
            continue
    for m in re.finditer(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html):
        try:
            data = json.loads(m.group(1).strip())
            if isinstance(data, dict):
                if "author" in data and not meta.get("author"):
                    a = data["author"]
                    if isinstance(a, dict):
                        meta["author"] = a.get("name", "")
                    elif isinstance(a, list) and a:
                        a0 = a[0]
                        meta["author"] = a0.get("name", "") if isinstance(a0, dict) else str(a0)
                if "datePublished" in data and not meta.get("date"):
                    meta["date"] = data["datePublished"]
        except Exception:
            continue
    return meta


def _extract_entities(text: str) -> dict:
    found = {}
    if _HAS_NATASHA:
        try:
            doc = _NatashaDoc(text[:20000])
            doc.segment(_NATASHA_SEG)
            doc.tag_ner(_NATASHA_NER)
            for span in doc.spans:
                span.normalize(_NATASHA_VOCAB)
                t = span.type.lower()
                found.setdefault(t, [])
                if span.normal and span.normal not in found[t]:
                    found[t].append(span.normal)
                    if len(found[t]) >= 20:
                        break
        except Exception:
            pass
    if _HAS_SPACY and _SPACY is not None:
        try:
            doc = _SPACY(text[:20000])
            for ent in doc.ents:
                t = ent.label_.lower()
                found.setdefault(t, [])
                if ent.text not in found[t]:
                    found[t].append(ent.text)
                    if len(found[t]) >= 20:
                        break
        except Exception:
            pass
    return found


def _detect_lang(text: str) -> str:
    if not _HAS_LANGDETECT or not text:
        return ""
    try:
        return _langdetect(text[:5000])
    except Exception:
        return ""


def _summarize(text: str, n: int = 3) -> str:
    if not _HAS_SUMY or len(text) < 300:
        return text[:400]
    try:
        parser = PlaintextParser.from_string(text[:20000], Tokenizer("english"))
        summarizer = LexRankSummarizer()
        sentences = summarizer(parser.document, n)
        return " ".join(str(s) for s in sentences)
    except Exception:
        return text[:400]


def _freshness_score(date_str: str) -> float:
    if not date_str:
        return 0.0
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                dt = time.mktime(time.strptime(date_str[:19], fmt[:len(date_str[:19])]))
                age_days = (_now() - dt) / 86400.0
                if age_days < 0:
                    return 0.5
                return max(0.0, 1.0 - age_days / 365.0)
            except Exception:
                continue
    except Exception:
        pass
    return 0.0


def _authority_score(url: str) -> float:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return 0.0
    if not host:
        return 0.0
    tld_bonus = 0.0
    if host.endswith(".gov") or host.endswith(".edu"):
        tld_bonus = 0.3
    elif host.endswith(".org"):
        tld_bonus = 0.15
    trusted = ("wikipedia.org", "github.com", "arxiv.org", "nature.com", "science.org", "bbc.com", "reuters.com", "apnews.com", "nytimes.com", "theguardian.com")
    if any(t in host for t in trusted):
        tld_bonus += 0.3
    return min(0.6, tld_bonus)


def _pii_detect(text: str) -> dict:
    patterns = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "phone": r"\b(?:\+?\d[\d\s().-]{7,}\d)\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d[ -]*?){13,19}\b",
        "ipv4": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }
    found = {}
    for k, pat in patterns.items():
        try:
            m = list(dict.fromkeys(re.findall(pat, text)))
            if m:
                found[k] = m[:10]
        except Exception:
            continue
    return found


def _secret_scan(text: str) -> dict:
    patterns = {
        "aws_access_key": r"\bAKIA[0-9A-Z]{16}\b",
        "aws_secret": r"\b[A-Za-z0-9/+=]{40}\b",
        "github_token": r"\bgh[pousr]_[A-Za-z0-9]{36,}\b",
        "slack_token": r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b",
        "google_api": r"\bAIza[0-9A-Za-z_-]{35}\b",
        "stripe_key": r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{24,}\b",
        "private_key": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "jwt": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
        "generic_token": r"(?i)\b(?:api[_-]?key|secret|token|password)\s*[:=]\s*[\"']?([A-Za-z0-9_\-]{20,})[\"']?",
    }
    found = {}
    for k, pat in patterns.items():
        try:
            m = list(dict.fromkeys(re.findall(pat, text)))
            if m:
                found[k] = m[:5]
        except Exception:
            continue
    return found


def _minhash_signature(text: str, num_perm: int = 64):
    if not _HAS_DATASKETCH:
        return None
    m = MinHash(num_perm=num_perm)
    for w in set(re.findall(r"\w+", _lemmatize(text))):
        m.update(w.encode("utf-8"))
    return m


def _mmr_rerank(results: list, query: str, lambda_: float = 0.7) -> list:
    if not results:
        return results
    q_words = set(_lemmatize(query).split())
    scored = []
    for r in results:
        txt = _lemmatize((r.get("snippet") or "") + " " + (r.get("title") or ""))
        rel = sum(1 for w in q_words if w in txt) / max(len(q_words), 1)
        base = rel + r.get("score", 0) * 0.01
        fresh = _freshness_score((r.get("meta") or {}).get("date", ""))
        auth = _authority_score(r.get("url", ""))
        scored.append((base + fresh * 0.15 + auth * 0.15, r))
    scored.sort(key=lambda x: -x[0])
    selected = []
    selected_text = []
    while scored:
        best_idx = None
        best_val = -1e9
        for i, (s, r) in enumerate(scored):
            txt = _lemmatize((r.get("snippet") or "")[:500])
            redundancy = 0.0
            for st in selected_text:
                common = set(txt.split()) & set(st.split())
                union = set(txt.split()) | set(st.split())
                if union:
                    redundancy = max(redundancy, len(common) / len(union))
            val = lambda_ * s - (1 - lambda_) * redundancy
            if val > best_val:
                best_val = val
                best_idx = i
        s, r = scored.pop(best_idx)
        selected.append(r)
        selected_text.append(_lemmatize((r.get("snippet") or "")[:500]))
    return selected


async def _recover_via_wayback(url: str) -> str | None:
    target = f"https://web.archive.org/web/2id_/{url}"
    try:
        if _HAS_HTTPX:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
                r = await c.get(target, headers={"User-Agent": random.choice(_UA_POOL)})
                if r.status_code == 200 and len(r.text or "") > 500:
                    return r.text
        if _HAS_CURL:
            async with _CurlSession() as s:
                r = await s.get(target, timeout=15, impersonate="chrome", allow_redirects=True)
                if r.status_code == 200 and len(r.text or "") > 500:
                    return r.text
    except Exception:
        return None
    return None


async def _recover_via_bing(url: str) -> str | None:
    target = f"https://cc.bingj.com/cache.aspx?q={quote_plus(url)}"
    try:
        if _HAS_HTTPX:
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
                r = await c.get(target, headers={"User-Agent": random.choice(_UA_POOL)})
                if r.status_code == 200 and len(r.text or "") > 500:
                    return r.text
    except Exception:
        return None
    return None


async def _recover_via_jina_html(url: str) -> str | None:
    target = f"https://r.jina.ai/{url}"
    try:
        if _HAS_HTTPX:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as c:
                r = await c.get(target, headers={"User-Agent": random.choice(_UA_POOL), "X-Return-Format": "html"})
                if r.status_code == 200 and len(r.text or "") > 500:
                    return r.text
    except Exception:
        return None
    return None


async def before_fetch(ctx):
    url = ctx.get("url")
    if not url:
        return None
    norm = _normalize_url(url)
    ctx["url"] = norm
    try:
        module = ctx.get("trusted_module") or ctx.get("module")
        if module is not None:
            existing_cookie = module._cookie_for(urlparse(norm).netloc) if hasattr(module, "_cookie_for") else None
            if existing_cookie:
                ctx["_allr_cookie"] = existing_cookie
    except Exception:
        pass
    mirrored = _mirror_url(norm)
    if mirrored != norm:
        ctx["url"] = mirrored
        norm = mirrored
    if _is_tor(norm):
        ctx["_allr_force_tor"] = True
    now = _now()
    host = urlparse(norm).netloc
    last = _STATE["rate_map"].get(host, 0)
    if now - last < 0.4:
        await asyncio.sleep(0.4 - (now - last))
    _STATE["rate_map"][host] = _now()
    key = _sha1(norm)
    if key in _STATE["seen_urls"]:
        return None
    _STATE["seen_urls"].add(key)
    _trim_cache()
    return None


async def after_fetch(ctx):
    html = ctx.get("html")
    if not html:
        return None
    out = html
    out = _strip_trackers(out)
    out = _strip_ads(out)
    out = _deamp(out)
    out = _decode_b64_blobs(out)
    out = _clean_html(out)
    out = _extract_readable(out)
    _STATE["session_stats"]["fetches"] += 1
    return out


async def on_blocked(ctx):
    reason = ctx.get("reason")
    url = ctx.get("url")
    if not url:
        return None
    _STATE["session_stats"]["blocked"] += 1
    for recover in (_recover_via_wayback, _recover_via_bing, _recover_via_jina_html):
        try:
            page = await recover(url)
            if page and len(page) > 500:
                return page
        except Exception:
            continue
    return None


async def on_js_required(ctx):
    url = ctx.get("url")
    if not url:
        return None
    _STATE["session_stats"]["js"] += 1
    for recover in (_recover_via_wayback, _recover_via_jina_html, _recover_via_bing):
        try:
            page = await recover(url)
            if page and len(page) > 500:
                return page
        except Exception:
            continue
    return None


async def on_error(ctx):
    url = ctx.get("url")
    error = str(ctx.get("error") or "")
    if not url:
        return None
    _STATE["session_stats"]["errors"] += 1
    low = error.lower()
    if "timeout" in low or "timed out" in low or "refused" in low or "connection" in low:
        page = await _recover_via_wayback(url)
        if page:
            return page
    if "dns" in low or "resolve" in low or "name or service" in low:
        page = await _recover_via_jina_html(url)
        if page:
            return page
    page = await _recover_via_bing(url)
    if page:
        return page
    return None


async def on_result(ctx):
    result = ctx.get("result")
    if not isinstance(result, dict):
        return None
    snippet = result.get("snippet") or ""
    title = result.get("title") or ""
    url = result.get("url") or ""
    meta = result.get("meta") or {}
    if not meta:
        meta = _extract_meta(ctx.get("html") or "")
        result["meta"] = meta
    entities = _extract_entities(snippet + " " + title)
    if entities:
        existing = result.get("entities") or {}
        for k, v in entities.items():
            if k in existing:
                existing[k] = list(dict.fromkeys(existing[k] + v))[:20]
            else:
                existing[k] = v[:20]
        result["entities"] = existing
    pii = _pii_detect(snippet)
    if pii:
        result["pii"] = pii
    secrets = _secret_scan(snippet)
    if secrets:
        result["secrets"] = secrets
    lang = _detect_lang(snippet)
    if lang:
        result["lang"] = lang
    if snippet and len(snippet) > 400:
        result["summary"] = _summarize(snippet, n=3)
    if _HAS_DATASKETCH:
        mh = _minhash_signature(snippet)
        if mh is not None:
            result["_minhash"] = list(mh.hashvalues[:16])
    fresh = _freshness_score(meta.get("date", ""))
    auth = _authority_score(url)
    bonus = fresh * 0.15 + auth * 0.15
    if bonus:
        result["score"] = float(result.get("score", 0)) + bonus
        result["freshness"] = round(fresh, 3)
        result["authority"] = round(auth, 3)
    _STATE["session_stats"]["results"] += 1
    return None


async def on_search(ctx):
    query = ctx.get("query") or ""
    if not query:
        return None
    _STATE["seen_urls"].clear()
    expanded = query
    try:
        if re.search(r"\b(?:today|now|latest|recent)\b", query, re.IGNORECASE):
            expanded += f" after:{time.strftime('%Y-%m-%d', time.localtime(_now() - 7 * 86400))}"
        if _MORPH is not None:
            lemmas = [w for w in _lemmatize(query).split() if len(w) > 2]
            uniq = list(dict.fromkeys(lemmas))
            if uniq and " ".join(uniq) != query.lower():
                expanded = query + " " + " ".join(uniq[:3])
    except Exception:
        pass
    ctx["query"] = expanded
    return None


async def on_command(ctx):
    text = ctx.get("text") or ""
    sender = ctx.get("sender")
    if not text:
        return None
    key = f"{sender}:{_sha1(text)}"
    now = _now()
    bucket = _STATE["rate_map"].get(key, [])
    bucket = [t for t in bucket if now - t < 60]
    if len(bucket) > 30:
        return False
    bucket.append(now)
    _STATE["rate_map"][key] = bucket
    return None


async def on_start(ctx):
    _STATE["start_ts"] = _now()
    _STATE["warmup_done"] = False
    module = ctx.get("module")
    if module is not None:
        try:
            sites = module._sites() if hasattr(module, "_sites") else {}
            for name, site in list(sites.items())[:5]:
                if site.get("disabled"):
                    continue
                try:
                    url = module._build_url(site, "test") if hasattr(module, "_build_url") else None
                    if url:
                        await module._fetch_async(url)
                except Exception:
                    continue
            _STATE["warmup_done"] = True
        except Exception:
            pass
    return None


async def on_stop(ctx):
    try:
        _STATE["url_cache"].clear()
        _STATE["seen_urls"].clear()
        _STATE["rate_map"].clear()
    except Exception:
        pass
    return None


async def on_sites_change(ctx):
    action = ctx.get("action")
    name = ctx.get("name")
    site = ctx.get("site")
    if action == "add" and isinstance(site, dict):
        url = site.get("url", "")
        if url and not site.get("tags"):
            host = urlparse(url).netloc.lower()
            tags = []
            if any(t in host for t in ("news", "reuters", "bbc", "guardian", "nytimes")):
                tags.append("news")
            if any(t in host for t in ("forum", "reddit", "stackexchange")):
                tags.append("forum")
            if host.endswith(".api") or "/api/" in url or site.get("type") == "api":
                tags.append("api")
            if tags:
                site["tags"] = tags
        if url:
            site["weight"] = site.get("weight") or _authority_score(url) + 1.0
    return None


async def on_plugin_load(ctx):
    return None


async def on_plugin_unload(ctx):
    return None
