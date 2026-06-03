from typing import List

def safe_lower(text: str) -> str:
    return text.lower() if text else ""

def count_keywords(text: str, keywords: List[str]) -> int:
    text_lower = safe_lower(text)
    return sum(1 for kw in keywords if kw.lower() in text_lower)

def find_keywords(text: str, keywords: List[str]) -> List[str]:
    text_lower = safe_lower(text)
    return [kw for kw in keywords if kw.lower() in text_lower]
