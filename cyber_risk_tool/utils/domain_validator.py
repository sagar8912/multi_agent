import re
from typing import Tuple

def validate_domain(domain: str) -> Tuple[bool, str]:
    """
    Validates a domain name. Returns (is_valid, error_message).
    """
    if not domain or not isinstance(domain, str):
        return False, "Domain is empty or not a string."
        
    domain_str = domain.strip()
    
    # Remove protocol
    if domain_str.startswith("http://"):
        domain_str = domain_str[7:]
    elif domain_str.startswith("https://"):
        domain_str = domain_str[8:]
        
    # Remove trailing slash
    if domain_str.endswith("/"):
        domain_str = domain_str[:-1]
        
    if "@" in domain_str:
        return False, "Domain contains invalid character @"
        
    if " " in domain_str:
        return False, "Domain contains spaces"
        
    if ".." in domain_str:
        return False, "Domain contains consecutive dots"
        
    if "." not in domain_str:
        if domain_str != "localhost":
            return False, "Domain must contain a dot (e.g. .com)"
            
    # Basic regex for valid domain
    # This checks for alphanumeric, hyphens, and dots.
    if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain_str):
        if domain_str != "localhost":
            return False, "Invalid domain format"
            
    return True, ""
