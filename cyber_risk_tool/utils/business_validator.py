from typing import Tuple

def check_business_validity(html_text: str) -> Tuple[bool, str]:
    """
    Checks if a given website text appears to be a placeholder or generic domain.
    Returns (is_placeholder, reason)
    """
    if not html_text or not isinstance(html_text, str):
        return True, "No content to analyze."

    text_lower = html_text.lower()
    
    placeholder_phrases = [
        "example domain",
        "this domain is for use in illustrative examples",
        "parked domain",
        "domain for sale",
        "coming soon",
        "under construction",
        "default page",
        "index of /"
    ]
    
    for phrase in placeholder_phrases:
        if phrase in text_lower:
            return True, f"Found placeholder/generic phrase: '{phrase}'"
            
    # Check if text is extremely short (e.g., less than 50 words)
    words = text_lower.split()
    if len(words) < 50:
        return True, "Website content is extremely short and lacks business context."
        
    return False, "Business identity appears valid."
