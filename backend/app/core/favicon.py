"""
favicon.py — 按优先级顺序自动获取网站 Favicon 并转换为 Base64 Data URI 的工具函数。

获取策略（按顺序，前一步失败才执行下一步）：
  1. https://{domain}/favicon.ico
  2. https://{domain}/favicon.png
  3. https://{domain}/favicon.jpg
  4. https://{domain}/favicon.jpeg
  5. 抓取网页 HTML，解析 <link rel="icon"> 标签并下载
  6. 抓取网页 HTML，解析 <link rel="logo"> 标签并下载

全部失败则返回 None。
"""

import base64
from urllib.parse import urlparse, urljoin
from typing import Optional

import httpx
from bs4 import BeautifulSoup


# 超时设置（秒）
_TIMEOUT = httpx.Timeout(connect=5.0, read=8.0, write=5.0, pool=5.0)

# 请求头，模拟普通浏览器，避免被某些站点拦截
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}


def _extract_domain(href: str) -> Optional[str]:
    """从完整 URL 中解析出协议+域名部分，如 https://example.com"""
    try:
        parsed = urlparse(href)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass
    return None


def download_and_convert_to_base64(url: str, client: Optional[httpx.Client] = None) -> Optional[str]:
    """
    下载指定的 URL 图片资源，并将其转换为 base64 Data URI 格式。
    """
    def _do_download(c: httpx.Client) -> Optional[str]:
        try:
            resp = c.get(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
            if resp.status_code == 200 and resp.content:
                content_type = resp.headers.get("content-type", "").split(";")[0].strip()
                # 如果没有提供合适的主流图片 Content-Type，则通过后缀推断
                if not content_type.startswith("image/"):
                    lower_url = url.lower()
                    if lower_url.endswith(".png"):
                        content_type = "image/png"
                    elif lower_url.endswith(".jpg") or lower_url.endswith(".jpeg"):
                        content_type = "image/jpeg"
                    elif lower_url.endswith(".gif"):
                        content_type = "image/gif"
                    elif lower_url.endswith(".svg"):
                        content_type = "image/svg+xml"
                    else:
                        content_type = "image/x-icon"
                b64_data = base64.b64encode(resp.content).decode("utf-8")
                return f"data:{content_type};base64,{b64_data}"
        except Exception:
            pass
        return None

    if client:
        return _do_download(client)
    else:
        with httpx.Client() as c:
            return _do_download(c)


def _fetch_html(url: str, client: httpx.Client) -> Optional[str]:
    """GET 请求获取网页 HTML 文本，失败返回 None"""
    try:
        resp = client.get(url, headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True)
        if resp.status_code < 400:
            return resp.text
    except Exception:
        pass
    return None


def _extract_link_rel(html: str, base_url: str, rel: str) -> Optional[str]:
    """
    解析 HTML 中 <link rel="{rel}"> 标签 of href 属性。
    支持相对路径，会自动拼接为绝对 URL。
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        tags = soup.find_all("link", rel=lambda r: r and rel in " ".join(r).lower())
        for tag in tags:
            href = tag.get("href", "").strip()
            if href:
                return urljoin(base_url, href)
    except Exception:
        pass
    return None


def fetch_favicon(href: str) -> Optional[str]:
    """
    按六步策略依次尝试获取并下载书签 URL 的 Favicon，返回 Base64 Data URI。

    Args:
        href: 书签的完整 URL，如 https://www.example.com/some/page

    Returns:
        Base64 Data URI 字符串，或 None（全部策略均失败时）
    """
    domain = _extract_domain(href)
    if not domain:
        return None

    with httpx.Client() as client:
        # --- 步骤 1~4：直接尝试常见 favicon 文件路径并尝试下载 ---
        for ext in ("ico", "png", "jpg", "jpeg"):
            candidate = f"{domain}/favicon.{ext}"
            data_uri = download_and_convert_to_base64(candidate, client)
            if data_uri:
                return data_uri

        # --- 步骤 5~6：抓取网页 HTML 解析 <link> 标签并下载 ---
        html = _fetch_html(href, client)
        if html:
            # 步骤 5：<link rel="icon">
            icon_url = _extract_link_rel(html, href, "icon")
            if icon_url:
                data_uri = download_and_convert_to_base64(icon_url, client)
                if data_uri:
                    return data_uri

            # 步骤 6：<link rel="logo">
            logo_url = _extract_link_rel(html, href, "logo")
            if logo_url:
                data_uri = download_and_convert_to_base64(logo_url, client)
                if data_uri:
                    return data_uri

    return None
