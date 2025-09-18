#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Taiwan Law History MCP Server

Provides multiple functions for scraping Taiwan law information:
- search_law: Search for laws by name
- get_law_history: Get complete history of a law
- get_law_articles: Get current articles of a law
- parse_law_text: Parse and normalize law text
- convert_dates: Convert ROC dates to western dates
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional, Tuple
import ssl
import os
import re
import urllib3
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# SSL configuration for legacy sites
os.environ['OPENSSL_CONF'] = ''

# Patch SSL for compatibility
_old_create_default_context = ssl.create_default_context

def _patched_create_default_context(*args, **kwargs):
    ctx = _old_create_default_context(*args, **kwargs)
    for opt_name in ['OP_LEGACY_SERVER_CONNECT', 'OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION']:
        if hasattr(ssl, opt_name):
            ctx.options |= getattr(ssl, opt_name)

    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
    except:
        try:
            ctx.set_ciphers('ALL:!EXPORT:!aNULL:!eNULL:!SSLv2')
        except:
            pass

    return ctx

ssl.create_default_context = _patched_create_default_context

def create_legacy_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for opt_name in ['OP_LEGACY_SERVER_CONNECT', 'OP_ALLOW_UNSAFE_LEGACY_RENEGOTIATION']:
        if hasattr(ssl, opt_name):
            ctx.options |= getattr(ssl, opt_name)

    try:
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
    except:
        pass

    return ctx

try:
    urllib3.util.ssl_.DEFAULT_SSL_CONTEXT = create_legacy_ssl_context()
except Exception:
    pass

# Constants
BASE_URL = "https://lis.ly.gov.tw"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}

# Chinese number conversion
_CN_DIGITS = {
    "零": 0, "〇": 0, "○": 0,
    "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
    "兩": 2,
}

_CN_UNITS = {"十": 10, "百": 100, "千": 1000}

def cn_small_to_int(s: str) -> int:
    """Convert small Chinese numbers (0-999) to integers"""
    s = s.strip()
    if not s:
        return 0
    if s.isdigit():
        return int(s)

    total = 0
    num = 0
    unit = 1

    for ch in reversed(s):
        if ch in _CN_DIGITS:
            num = _CN_DIGITS[ch]
            total += num * unit
        elif ch in _CN_UNITS:
            unit = _CN_UNITS[ch]
            if num == 0:
                total += unit
            num = 0

    return total

def normalize_article_no(artino_text: str) -> str:
    """Normalize article numbers from Chinese to Arabic format"""
    t = artino_text.strip().replace(" ", "")
    m = re.match(r"^第(.+?)條(.*)$", t)
    if not m:
        return t

    base_cn = m.group(1)
    suffix = m.group(2)

    base = cn_small_to_int(base_cn)

    if not suffix:
        return str(base)

    parts = [p for p in re.split(r"之", suffix) if p]
    nums = [str(cn_small_to_int(p)) for p in parts]
    return f"{base}-" + "-".join(nums)

def parse_roc_date_and_type(s: str) -> Tuple[str, str]:
    """Parse ROC date and modification type"""
    s = s.strip()
    if not s:
        return "", ""

    parts = s.split()
    roc = parts[0]
    kind = parts[1] if len(parts) > 1 else ""

    if not roc.isdigit() or len(roc) < 7:
        return "", kind

    roc_year = int(roc[:3])
    month = roc[3:5]
    day = roc[5:7]
    ad_year = roc_year + 1911

    return f"{ad_year}-{month}-{day}", kind

def clean_text(x: str) -> str:
    """Clean and normalize text"""
    x = x.replace("\u3000", " ").replace("\xa0", " ")
    x = re.sub(r"[ \t]+", " ", x)
    x = re.sub(r"\s*\n\s*", "\n", x).strip()
    return x

def pick_parser():
    """Choose the best available HTML parser"""
    try:
        import html5lib
        return "html5lib"
    except ImportError:
        try:
            import lxml
            return "lxml"
        except ImportError:
            return "html.parser"

class LegacySSLAdapter(requests.adapters.HTTPAdapter):
    """Custom SSL adapter for legacy sites"""
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = create_legacy_ssl_context()
        return super().init_poolmanager(*args, **kwargs)

def get_session():
    """Create a session with custom SSL configuration"""
    s = requests.Session()
    s.headers.update(HEADERS)
    s.mount("https://", LegacySSLAdapter())
    return s

def _collect_form_payload(soup):
    """Collect form payload from search page"""
    form = soup.find("form")
    if not form:
        raise RuntimeError("找不到查詢表單 form。")

    action = form.get("action") or "/lglawc/lglawkm"
    payload = {}
    submit_name = None

    for inp in form.select("input[name]"):
        name = inp.get("name")
        typ = (inp.get("type") or "").lower()
        val = inp.get("value") or ""

        if typ in ("checkbox", "radio"):
            if inp.has_attr("checked"):
                payload[name] = val
        else:
            payload[name] = val

        if typ == "image" and ("檢索" in name or "search" in name.lower()):
            submit_name = name

    return action, payload, submit_name

def _retry_if_timeout(session, html, entry_url, referer_headers):
    """Retry if timeout.html is encountered"""
    if "timeout.html" in html:
        session.get(urljoin(BASE_URL, "/lglawc/lglawkm"), headers=referer_headers, timeout=20, verify=False)
        r = session.get(entry_url, headers=referer_headers, timeout=20, verify=False)
        r.encoding = r.apparent_encoding or "utf-8"
        return BeautifulSoup(r.text, "lxml")
    return BeautifulSoup(html, "lxml")

# Initialize the MCP server
server = Server("law-history-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_law",
            description="Search for laws by name and get basic information",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_name": {
                        "type": "string",
                        "description": "Name of the law to search for"
                    }
                },
                "required": ["law_name"]
            }
        ),
        Tool(
            name="get_law_history",
            description="Get complete history of a specific law including all amendments",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_name": {
                        "type": "string",
                        "description": "Exact name of the law"
                    }
                },
                "required": ["law_name"]
            }
        ),
        Tool(
            name="get_law_articles",
            description="Get current articles of a specific law",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_name": {
                        "type": "string",
                        "description": "Exact name of the law"
                    }
                },
                "required": ["law_name"]
            }
        ),
        Tool(
            name="parse_law_text",
            description="Parse and normalize law text, converting Chinese numbers to Arabic",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Law text to parse and normalize"
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="convert_dates",
            description="Convert ROC (Republic of China) dates to Western dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "roc_date": {
                        "type": "string",
                        "description": "ROC date in format like '1110520' or '1110520 修正'"
                    }
                },
                "required": ["roc_date"]
            }
        ),
        Tool(
            name="normalize_article_number",
            description="Convert Chinese article numbers to Arabic format",
            inputSchema={
                "type": "object",
                "properties": {
                    "article_text": {
                        "type": "string",
                        "description": "Article number text like '第十九條' or '第二十條之一'"
                    }
                },
                "required": ["article_text"]
            }
        ),
        Tool(
            name="get_specific_article",
            description="Get history of a specific article only, saving AI tokens by not fetching all articles",
            inputSchema={
                "type": "object",
                "properties": {
                    "law_name": {
                        "type": "string",
                        "description": "Exact name of the law"
                    },
                    "article_number": {
                        "type": "string",
                        "description": "Article number (supports Chinese like '第一條' or Arabic like '1' or compound like '1-1')"
                    }
                },
                "required": ["law_name", "article_number"]
            }
        ),
        Tool(
            name="update_packages",
            description="Update all required Python packages for the law scraper",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""

    if name == "search_law":
        return await search_law(arguments["law_name"])

    elif name == "get_law_history":
        return await get_law_history(arguments["law_name"])

    elif name == "get_law_articles":
        return await get_law_articles(arguments["law_name"])

    elif name == "parse_law_text":
        return await parse_law_text(arguments["text"])

    elif name == "convert_dates":
        return await convert_dates(arguments["roc_date"])

    elif name == "normalize_article_number":
        return await normalize_article_number(arguments["article_text"])

    elif name == "get_specific_article":
        return await get_specific_article(arguments["law_name"], arguments["article_number"])

    elif name == "update_packages":
        return await update_packages()

    else:
        raise ValueError(f"Unknown tool: {name}")

async def search_law(law_name: str) -> List[TextContent]:
    """Search for laws by name"""
    try:
        session = get_session()

        entry_url = f"{BASE_URL}/lglawc/lglawkm"
        referer_headers = {
            "Referer": entry_url,
            "Content-Type": "application/x-www-form-urlencoded",
            **HEADERS
        }

        # Get form page
        r0 = session.get(entry_url, headers=HEADERS, timeout=20, verify=False)
        r0.encoding = r0.apparent_encoding or "utf-8"
        soup0 = _retry_if_timeout(session, r0.text, entry_url, HEADERS)

        # Extract form data
        action_path, payload, submit_name = _collect_form_payload(soup0)

        # Fill in law name
        payload["_1_6_T"] = law_name
        payload.setdefault("@_1_6_T", "T_LN/LW")

        # Submit search
        if submit_name:
            payload[submit_name + ".x"] = "38"
            payload[submit_name + ".y"] = "12"

        post_url = urljoin(BASE_URL, action_path)
        r1 = session.post(post_url, data=payload, headers=referer_headers, timeout=30, verify=False)
        r1.encoding = r1.apparent_encoding or "utf-8"
        soup = _retry_if_timeout(session, r1.text, entry_url, referer_headers)

        # Parse results
        sumtab = soup.select_one("table.sumtab")
        if not sumtab:
            return [TextContent(type="text", text=f"未找到法律: {law_name}")]

        results = []
        for row in sumtab.select("tr"):
            a = row.select_one("td.sumtd2_TI a[href]")
            if a:
                title = a.get_text(strip=True)
                href = urljoin(BASE_URL, a["href"])
                results.append({
                    "title": title,
                    "url": href
                })

        return [TextContent(
            type="text",
            text=json.dumps({
                "search_term": law_name,
                "results": results
            }, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"搜尋錯誤: {str(e)}")]

async def get_law_history(law_name: str) -> List[TextContent]:
    """Get complete history of a law"""
    try:
        session = get_session()

        # First search for the law
        lawsingle_url = await _search_law_page(session, law_name)

        # Get the law page
        resp = session.get(lawsingle_url, timeout=30, verify=False)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, pick_parser())

        # Find history link
        history_url = _extract_history_link(soup)

        if not history_url:
            return [TextContent(type="text", text=f"未找到 {law_name} 的法條沿革")]

        # Get history page
        r2 = session.get(history_url, timeout=30, verify=False)
        r2.encoding = r2.apparent_encoding or "utf-8"

        # Parse history
        hist_data = _parse_history(r2.text, law_name)
        items = _postprocess_items(hist_data.get("items", []))

        result = {
            "law_name": law_name,
            "history_url": history_url,
            "source_url": lawsingle_url,
            "items": items
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"取得法條沿革錯誤: {str(e)}")]

async def get_law_articles(law_name: str) -> List[TextContent]:
    """Get current articles of a law"""
    try:
        session = get_session()

        # Search for the law
        lawsingle_url = await _search_law_page(session, law_name)

        # Get the law page
        resp = session.get(lawsingle_url, timeout=30, verify=False)
        resp.encoding = resp.apparent_encoding or "utf-8"

        # Parse articles
        parsed = _parse_articles(resp.text, law_name)
        items = _postprocess_items(parsed.get("items", []))

        result = {
            "law_name": law_name,
            "source_url": lawsingle_url,
            "history_url": parsed.get("history_url"),
            "items": items
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"取得法條內容錯誤: {str(e)}")]

async def parse_law_text(text: str) -> List[TextContent]:
    """Parse and normalize law text"""
    try:
        cleaned = clean_text(text)

        # Find article numbers and normalize them
        article_pattern = re.compile(r'第[^條]+條(?:之[^條]*)?')
        articles = article_pattern.findall(text)

        normalized_articles = {}
        for art in articles:
            normalized = normalize_article_no(art)
            normalized_articles[art] = normalized

        result = {
            "original_text": text,
            "cleaned_text": cleaned,
            "found_articles": normalized_articles
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"解析文本錯誤: {str(e)}")]

async def convert_dates(roc_date: str) -> List[TextContent]:
    """Convert ROC dates to Western dates"""
    try:
        western_date, modification_type = parse_roc_date_and_type(roc_date)

        result = {
            "original_date": roc_date,
            "western_date": western_date,
            "modification_type": modification_type
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"轉換日期錯誤: {str(e)}")]

async def normalize_article_number(article_text: str) -> List[TextContent]:
    """Normalize article numbers"""
    try:
        normalized = normalize_article_no(article_text)

        result = {
            "original": article_text,
            "normalized": normalized
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"標準化條號錯誤: {str(e)}")]

async def get_specific_article(law_name: str, article_number: str) -> List[TextContent]:
    """Get history of a specific article only, saving AI tokens"""
    try:
        session = get_session()

        # Search for the law
        lawsingle_url = await _search_law_page(session, law_name)

        # Get the law page
        resp = session.get(lawsingle_url, timeout=30, verify=False)
        resp.encoding = resp.apparent_encoding or "utf-8"
        soup = BeautifulSoup(resp.text, pick_parser())

        # Find history link
        history_url = _extract_history_link(soup)

        if not history_url:
            return [TextContent(type="text", text=f"未找到 {law_name} 的法條沿革")]

        # Get history page
        r2 = session.get(history_url, timeout=30, verify=False)
        r2.encoding = r2.apparent_encoding or "utf-8"

        # Parse history
        hist_data = _parse_history(r2.text, law_name)
        all_items = _postprocess_items(hist_data.get("items", []))

        # Normalize the input article number
        if article_number.startswith("第") and article_number.endswith("條"):
            normalized_input = normalize_article_no(article_number)
        else:
            normalized_input = article_number

        # Filter for the specific article
        filtered_items = []
        for item in all_items:
            if item.get("條號") == normalized_input:
                filtered_items.append(item)

        if not filtered_items:
            return [TextContent(
                type="text",
                text=f"在 {law_name} 中未找到條號 {normalized_input} 的資料"
            )]

        result = {
            "law_name": law_name,
            "history_url": history_url,
            "source_url": lawsingle_url,
            "article_number": normalized_input,
            "items": filtered_items
        }

        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"取得特定條文錯誤: {str(e)}")]

async def update_packages() -> List[TextContent]:
    """Update all required Python packages"""
    try:
        import subprocess
        import sys

        packages = [
            "requests",
            "beautifulsoup4",
            "html5lib",
            "lxml",
            "urllib3",
            "mcp"
        ]

        results = []
        results.append("正在更新套件...")

        for package in packages:
            try:
                results.append(f"更新 {package}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", package],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode == 0:
                    results.append(f"✓ {package} 更新完成")
                else:
                    results.append(f"✗ {package} 更新失敗: {result.stderr}")

            except subprocess.TimeoutExpired:
                results.append(f"✗ {package} 更新超時")
            except Exception as e:
                results.append(f"✗ {package} 更新時發生錯誤: {str(e)}")

        results.append("套件更新完成！")

        return [TextContent(
            type="text",
            text="\n".join(results)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"更新套件錯誤: {str(e)}")]

# Helper functions
async def _search_law_page(session: requests.Session, law_name: str) -> str:
    """Search for law page URL"""
    entry_url = f"{BASE_URL}/lglawc/lglawkm"
    referer_headers = {
        "Referer": entry_url,
        "Content-Type": "application/x-www-form-urlencoded",
        **HEADERS
    }

    r0 = session.get(entry_url, headers=HEADERS, timeout=20, verify=False)
    r0.encoding = r0.apparent_encoding or "utf-8"
    soup0 = _retry_if_timeout(session, r0.text, entry_url, HEADERS)

    action_path, payload, submit_name = _collect_form_payload(soup0)

    payload["_1_6_T"] = law_name
    payload.setdefault("@_1_6_T", "T_LN/LW")

    if submit_name:
        payload[submit_name + ".x"] = "38"
        payload[submit_name + ".y"] = "12"

    post_url = urljoin(BASE_URL, action_path)
    r1 = session.post(post_url, data=payload, headers=referer_headers, timeout=30, verify=False)
    r1.encoding = r1.apparent_encoding or "utf-8"
    soup = _retry_if_timeout(session, r1.text, entry_url, referer_headers)

    sumtab = soup.select_one("table.sumtab")
    if not sumtab:
        raise RuntimeError("找不到檢索結果表格")

    target_a = None
    for row in sumtab.select("tr"):
        a = row.select_one("td.sumtd2_TI a[href]")
        if not a:
            continue
        if a.get_text(strip=True) == law_name:
            target_a = a
            break

    if not target_a:
        for a in sumtab.select("a[href]"):
            if law_name in a.get_text(strip=True):
                target_a = a
                break

    if not target_a:
        raise RuntimeError(f"查無完全相同的法名稱：{law_name}")

    return urljoin(BASE_URL, target_a["href"])

def _extract_history_link(soup: BeautifulSoup) -> Optional[str]:
    """Extract history link from law page"""
    a = soup.find("a", string=re.compile(r"法條沿革"))
    if a and a.get("href"):
        return urljoin(BASE_URL, a["href"])
    return None

def _parse_history(html: str, law_name: str) -> Dict:
    """Parse law history page"""
    soup = BeautifulSoup(html, pick_parser())

    title_node = soup.select_one(".law_n")
    page_law_name = title_node.get_text(strip=True) if title_node else law_name

    items = []

    for block in soup.select("table"):
        artino = block.select_one("font.artino")
        if not artino:
            continue
        article_no = artino.get_text(strip=True)

        dates_raw = [clean_text(f.get_text(strip=True)).strip("()")
                     for f in block.select("font.upddate")]
        texts = [clean_text(td.get_text("\n", strip=True))
                 for td in block.select("td.artiupd_TH_2")]
        reasons = [clean_text(td.get_text("\n", strip=True))
                   for td in block.select("td.artiupd_RS_2")]

        n = min(len(dates_raw), len(texts), len(reasons) if reasons else len(texts))

        if n == 0 and texts:
            for txt in texts:
                items.append({
                    "條號": article_no,
                    "時間": "",
                    "條文": txt,
                    "理由": reasons[0] if reasons else ""
                })
            continue

        for i in range(n):
            items.append({
                "條號": article_no,
                "時間": dates_raw[i] if i < len(dates_raw) else "",
                "條文": texts[i] if i < len(texts) else "",
                "理由": reasons[i] if i < len(reasons) else ""
            })

    return {
        "law_name": page_law_name,
        "items": items
    }

def _parse_articles(html: str, law_name: str) -> Dict:
    """Parse law articles page"""
    soup = BeautifulSoup(html, "html5lib")

    title_node = soup.select_one(".law_n")
    page_law_name = title_node.get_text(strip=True) if title_node else law_name

    history_url = _extract_history_link(soup)

    def norm_text(x: str) -> str:
        x = x.replace("\u3000", " ").replace("\xa0", " ")
        x = x.replace("\r\n", "\n").replace("\r", "\n")
        x = re.sub(r'<br\s*/?>', '\n', x, flags=re.I)
        x = re.sub(r'[ \t]+', ' ', x)
        x = re.sub(r'\s*\n\s*', '\n', x)
        return x.strip()

    items = []

    for art in soup.find_all("font", class_="artino"):
        article_no = art.get_text(strip=True)
        container = art.find_parent("table")
        if not container:
            continue

        dates = [norm_text(f.get_text(strip=True)).strip("()")
                 for f in container.find_all("font", class_="upddate")]
        texts = [norm_text(str(td)) for td in container.select("td.artiupd_TH_2")]
        reasons = [norm_text(str(td)) for td in container.select("td.artiupd_RS_2")]

        texts = [norm_text(re.sub(r'<[^>]+>', '', t)) for t in texts]
        reasons = [norm_text(re.sub(r'<[^>]+>', '', r)) for r in reasons]

        n = max(len(dates), len(texts), len(reasons))
        for i in range(n):
            items.append({
                "條號": article_no,
                "時間": dates[i] if i < len(dates) else "",
                "條文": texts[i] if i < len(texts) else "",
                "理由": reasons[i] if i < len(reasons) else ""
            })

    return {
        "law_name": page_law_name,
        "history_url": history_url,
        "items": items
    }

def _postprocess_items(items: List[Dict]) -> List[Dict]:
    """Postprocess items to normalize format"""
    out = []
    for it in items:
        artino_raw = it.get("條號", "").strip()
        time_raw = it.get("時間", "").strip()

        new_no = normalize_article_no(artino_raw)
        ym, kind = parse_roc_date_and_type(time_raw)

        new_item = {
            "條號": new_no,
            "時間": ym,
            "類型": kind,
            "條文": it.get("條文", ""),
            "理由": it.get("理由", ""),
        }
        out.append(new_item)
    return out

async def main():
    """Main entry point for the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="law-history-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )
        )

def cli_main():
    """CLI entry point that runs the async main function"""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()