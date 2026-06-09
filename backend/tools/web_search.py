import sys
import subprocess

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("[Web Search] Installing missing dependency: beautifulsoup4...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

import requests
import urllib.parse

def web_search(query: str, num_results: int = 3) -> list[dict]:
    """
    Search the web using DuckDuckGo HTML parser (requires no API keys).
    Filters search terms to prioritize official government traffic sites.
    """
    # Prioritize official domains
    search_query = f"{query} site:gov.in OR site:nic.in OR site:in"
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            # DuckDuckGo HTML result snippets list
            snippets = soup.find_all("a", class_="result__snippet")
            for snippet_elem in snippets[:num_results]:
                parent = snippet_elem.find_parent("div", class_="result__body")
                if parent:
                    title_elem = parent.find("a", class_="result__url")
                    title = title_elem.get_text(strip=True) if title_elem else "Search Result"
                    href = title_elem["href"] if title_elem and "href" in title_elem.attrs else ""
                    
                    # Clean DuckDuckGo redirect link
                    if href.startswith("//duckduckgo.com/l/?uddg="):
                        href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                    elif href.startswith("/l/?uddg="):
                        href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                        
                    snippet = snippet_elem.get_text(strip=True)
                    results.append({
                        "title": title,
                        "url": href,
                        "snippet": snippet
                    })
    except Exception as e:
        print(f"[Web Search Tool] Search failed: {e}")
    return results

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "helmet fine West Bengal"
    print(f"Searching web for: '{q}'...")
    res = web_search(q)
    for idx, r in enumerate(res):
        print(f"\n[{idx+1}] {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}")
