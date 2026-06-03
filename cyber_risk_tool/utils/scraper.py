import httpx
from bs4 import BeautifulSoup
from typing import Tuple, List, Optional
from urllib.parse import urlparse, urljoin
from utils.logger import get_logger
import asyncio

logger = get_logger(__name__)

def normalize_domain(domain: str) -> str:
    domain = domain.strip().lower()
    if not domain.startswith("http://") and not domain.startswith("https://"):
        domain = "http://" + domain
    
    parsed = urlparse(domain)
    netloc = parsed.netloc
    
    if netloc.startswith("www."):
        netloc = netloc[4:]
        
    return netloc

def build_url(domain: str, scheme: str = "https") -> str:
    return f"{scheme}://{normalize_domain(domain)}"

async def fetch_url(url: str, timeout: int = 10) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=timeout, headers=headers) as client:
            resp = await client.get(url)
            return resp.text, resp.status_code, str(resp.url)
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {url}")
        return None, None, None
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None, None, None

async def fetch_homepage(domain: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
    url = build_url(domain, "https")
    text, status, final_url = await fetch_url(url)
    if not text:
        url = build_url(domain, "http")
        text, status, final_url = await fetch_url(url)
    return text, status, final_url

def extract_text_from_html(html: str) -> str:
    if not html: return ""
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
    return soup.get_text(separator=' ', strip=True)

def extract_links(html: str, base_url: str) -> List[str]:
    if not html: return []
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        if href:
            links.append(urljoin(base_url, href))
    return list(set(links))

def find_candidate_pages(domain: str, keywords: List[str]) -> List[str]:
    return []
