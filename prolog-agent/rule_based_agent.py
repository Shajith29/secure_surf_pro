def explain_url(url):
    reasons = []

    # Rule 1: Suspicious keywords
    suspicious_keywords = ["login", "verify", "account", "secure", "update"]
    if any(keyword in url.lower() for keyword in suspicious_keywords):
        reasons.append("Uses suspicious keywords like login, verify, or account.")

    # Rule 2: Too many subdomains
    try:
        domain = url.split("//")[-1].split("/")[0]
        subdomains = domain.split(".")
        if len(subdomains) >= 4:
            reasons.append("Contains too many subdomains, which is common in fake sites.")
    except:
        pass

    # Rule 3: Misleading brand names
    trusted_brands = ["paypal", "google", "apple", "facebook", "microsoft"]
    for brand in trusted_brands:
        if brand in url.lower() and f"https://{brand}.com" not in url.lower():
            reasons.append(f"Includes brand name '{brand}' in a misleading position.")
            break

    # Rule 4: Suspicious TLD
    suspicious_tlds = [".ru", ".cc", ".tk", ".ml", ".gq"]
    if any(url.lower().endswith(tld) for tld in suspicious_tlds):
        reasons.append("Ends with suspicious top-level domain like .ru, .cc, etc.")

    # Rule 5: IP Address instead of domain
    import re
    ip_pattern = re.compile(r"http[s]?://\d+\.\d+\.\d+\.\d+")
    if ip_pattern.match(url):
        reasons.append("Uses an IP address instead of a domain name.")

    # Rule 6: No HTTPS
    if not url.startswith("https://"):
        reasons.append("Doesn't use HTTPS, which may be insecure.")

    if not reasons:
        return "This URL appears safe based on current heuristics."

    return " | ".join(reasons)
