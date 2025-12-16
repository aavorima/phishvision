"""
IOC (Indicator of Compromise) Extractor Service
Extracts and sanitizes threat indicators from email analysis for public sharing
"""

import re
import hashlib
import string
import secrets
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse


class IOCExtractor:
    """Extract and sanitize IOCs from email content for threat intelligence sharing"""

    # Common first names to remove from subjects (expanded list)
    COMMON_NAMES = {
        'john', 'jane', 'mike', 'michael', 'david', 'james', 'robert', 'william',
        'richard', 'joseph', 'thomas', 'charles', 'christopher', 'daniel', 'matthew',
        'anthony', 'mark', 'donald', 'steven', 'paul', 'andrew', 'joshua', 'kenneth',
        'kevin', 'brian', 'george', 'timothy', 'ronald', 'edward', 'jason', 'jeffrey',
        'ryan', 'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry',
        'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'raymond', 'gregory',
        'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan',
        'jessica', 'sarah', 'karen', 'lisa', 'nancy', 'betty', 'margaret', 'sandra',
        'ashley', 'kimberly', 'emily', 'donna', 'michelle', 'dorothy', 'carol',
        'amanda', 'melissa', 'deborah', 'stephanie', 'rebecca', 'sharon', 'laura',
        'cynthia', 'kathleen', 'amy', 'angela', 'shirley', 'anna', 'brenda', 'pamela',
        'emma', 'nicole', 'helen', 'samantha', 'katherine', 'christine', 'debra',
        # Add Turkish/Azerbaijani common names
        'ahmet', 'mehmet', 'mustafa', 'ali', 'huseyin', 'hasan', 'ibrahim', 'ismail',
        'fatma', 'ayse', 'emine', 'hatice', 'zeynep', 'elif', 'meryem', 'sultan',
        'kemal', 'osman', 'yusuf', 'omer', 'bekir', 'recep', 'erdogan', 'suleyman'
    }

    # Brands to preserve in sanitized subjects
    KNOWN_BRANDS = {
        'microsoft', 'apple', 'google', 'amazon', 'facebook', 'meta', 'instagram',
        'whatsapp', 'netflix', 'spotify', 'paypal', 'venmo', 'cashapp', 'zelle',
        'chase', 'bank of america', 'wells fargo', 'citibank', 'capital one',
        'ebay', 'alibaba', 'walmart', 'target', 'fedex', 'ups', 'usps', 'dhl',
        'dropbox', 'docusign', 'adobe', 'zoom', 'slack', 'teams', 'linkedin',
        'twitter', 'tiktok', 'snapchat', 'office365', 'outlook', 'gmail',
        'icloud', 'itunes', 'youtube', 'coinbase', 'binance', 'crypto',
        # Banks from threat intel
        'southtrust', 'keybank', 'regions', 'fifth third', 'national city',
        'suntrust', 'citizens bank', 'charter one', 'td bank', 'pnc', 'truist'
    }

    # Suspicious TLDs that might indicate phishing
    SUSPICIOUS_TLDS = {
        '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click',
        '.link', '.info', '.biz', '.cc', '.ws', '.pw', '.buzz', '.icu',
        '.monster', '.cam', '.fun', '.space', '.site', '.online', '.live'
    }

    def __init__(self):
        pass

    def extract_all_iocs(self, email_from: str, email_subject: str,
                         email_body: str, url_analysis: dict = None) -> List[Dict]:
        """
        Extract all IOCs from email analysis

        Returns list of dicts with: type, value, context, risk_score
        """
        iocs = []

        # Extract sender domain
        sender_domain = self.extract_sender_pattern(email_from)
        if sender_domain:
            iocs.append({
                'type': 'sender_domain',
                'value': sender_domain,
                'context': 'sender',
                'risk_score': self._assess_domain_risk(sender_domain)
            })

        # Extract domains from body
        body_domains = self.extract_domains(email_body)
        for domain in body_domains[:10]:  # Limit to 10 domains
            iocs.append({
                'type': 'domain',
                'value': domain,
                'context': 'body',
                'risk_score': self._assess_domain_risk(domain)
            })

        # Extract and defang URLs
        urls = self.extract_urls(email_body)
        for url in urls[:10]:  # Limit to 10 URLs
            defanged = self.defang_url(url)
            iocs.append({
                'type': 'url',
                'value': defanged,
                'context': 'body',
                'risk_score': self._assess_url_risk(url)
            })

        # Extract IP addresses
        ips = self.extract_ips(email_body)
        for ip in ips[:5]:  # Limit to 5 IPs
            iocs.append({
                'type': 'ip',
                'value': ip,
                'context': 'body',
                'risk_score': 70.0  # IPs in emails are usually suspicious
            })

        # Add subject-based domain if present
        subject_domains = self.extract_domains(email_subject)
        for domain in subject_domains[:2]:
            if domain not in [ioc['value'] for ioc in iocs]:
                iocs.append({
                    'type': 'domain',
                    'value': domain,
                    'context': 'subject',
                    'risk_score': self._assess_domain_risk(domain)
                })

        return iocs

    def extract_domains(self, text: str) -> List[str]:
        """Extract domain names from text"""
        if not text:
            return []

        # Pattern for domains
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        domains = re.findall(domain_pattern, text.lower())

        # Filter out common non-domains and legitimate service domains
        excluded = {
            'example.com', 'test.com', 'localhost.com', 'domain.com',
            'email.com', 'mail.com', 'gmail.com', 'outlook.com', 'yahoo.com',
            'hotmail.com', 'icloud.com', 'protonmail.com'  # Legitimate email providers
        }

        # Deduplicate and filter
        seen = set()
        result = []
        for domain in domains:
            if domain not in seen and domain not in excluded:
                seen.add(domain)
                result.append(domain)

        return result

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        if not text:
            return []

        # Pattern for URLs
        url_pattern = r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        # Clean up URLs (remove trailing punctuation)
        cleaned = []
        for url in urls:
            url = url.rstrip('.,;:!?')
            if len(url) > 10:  # Minimum reasonable URL length
                cleaned.append(url)

        return list(set(cleaned))

    def extract_ips(self, text: str) -> List[str]:
        """Extract IP addresses from text"""
        if not text:
            return []

        # IPv4 pattern
        ip_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        ips = re.findall(ip_pattern, text)

        # Filter out private/localhost IPs
        public_ips = []
        for ip in ips:
            octets = ip.split('.')
            first = int(octets[0])
            second = int(octets[1])

            # Skip private ranges
            if first == 10:  # 10.x.x.x
                continue
            if first == 172 and 16 <= second <= 31:  # 172.16-31.x.x
                continue
            if first == 192 and second == 168:  # 192.168.x.x
                continue
            if first == 127:  # localhost
                continue
            if first == 0:  # 0.x.x.x
                continue

            public_ips.append(ip)

        return list(set(public_ips))

    def extract_sender_pattern(self, sender: str) -> Optional[str]:
        """
        Extract sender domain pattern (not full email)
        e.g., "john@suspicious-domain.com" -> "*@suspicious-domain.com"
        """
        if not sender:
            return None

        # Extract email from "Name <email>" format
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender)
        if email_match:
            email = email_match.group()
            domain = email.split('@')[-1].lower()
            return f"*@{domain}"

        return None

    def sanitize_subject(self, subject: str, detected_brands: List[str] = None) -> str:
        """
        Remove PII from subject line while preserving brand names and keywords

        Examples:
        - "John, Your Chase Account Alert" -> "Your Chase Account Alert"
        - "Invoice #12345 for john.smith@email.com" -> "Invoice #[REDACTED]"
        - "Dear John Smith - Urgent PayPal Notice" -> "Urgent PayPal Notice"
        """
        if not subject:
            return "No Subject"

        result = subject

        # Remove email addresses
        result = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL]', result)

        # Remove phone numbers
        result = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE]', result)

        # Remove invoice/order numbers (keep the word, replace the number)
        result = re.sub(r'(invoice|order|ticket|case|ref|confirmation)\s*#?\s*\d+', r'\1 #[REDACTED]', result, flags=re.IGNORECASE)

        # Remove common name patterns at the start
        # Pattern: "Name," or "Dear Name" or "Hi Name" or "Hello Name"
        result = re.sub(r'^(dear|hi|hello|hey)\s+\w+[\s,]+', '', result, flags=re.IGNORECASE)
        result = re.sub(r'^\w+,\s*', '', result)  # "John, Your..."

        # Remove full name patterns
        for name in self.COMMON_NAMES:
            # Case insensitive name removal (only at word boundaries)
            result = re.sub(rf'\b{name}\b', '', result, flags=re.IGNORECASE)

        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()

        # Remove leading/trailing punctuation
        result = result.strip(',-:;')

        # If result is too short, return generic
        if len(result) < 5:
            return "Suspicious Email"

        return result.strip()

    def defang_url(self, url: str) -> str:
        """
        Defang URL for safe sharing
        http:// -> hxxp://
        https:// -> hxxps://
        . in domain -> [.]
        """
        if not url:
            return url

        # Replace protocol
        defanged = url.replace('http://', 'hxxp://')
        defanged = defanged.replace('https://', 'hxxps://')
        defanged = defanged.replace('Http://', 'hxxp://')
        defanged = defanged.replace('Https://', 'hxxps://')

        # Replace dots in domain (but not in path)
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                defanged_domain = parsed.netloc.replace('.', '[.]')
                defanged = defanged.replace(parsed.netloc, defanged_domain, 1)
        except:
            pass

        return defanged

    def generate_threat_hash(self, iocs: List[Dict], detected_brands: List[str] = None,
                            threat_type: str = None) -> str:
        """
        Generate unique hash for deduplication
        Based on: sorted IOC values + brands + threat type
        """
        hash_components = []

        # Add sorted domain IOCs
        domains = sorted([ioc['value'].lower() for ioc in iocs
                         if ioc['type'] in ('domain', 'sender_domain')])
        hash_components.extend(domains[:5])  # Top 5 domains

        # Add URL paths (without full URLs for privacy)
        for ioc in iocs:
            if ioc['type'] == 'url':
                try:
                    # Extract just the path
                    url = ioc['value'].replace('hxxp://', 'http://').replace('hxxps://', 'https://')
                    url = url.replace('[.]', '.')
                    parsed = urlparse(url)
                    if parsed.path and parsed.path != '/':
                        hash_components.append(f"path:{parsed.path.lower()}")
                except:
                    pass

        # Add detected brands
        if detected_brands:
            hash_components.extend(sorted([b.lower() for b in detected_brands]))

        # Add threat type
        if threat_type:
            hash_components.append(f"type:{threat_type}")

        # Generate hash
        combined = '|'.join(hash_components)
        if not combined:
            # Fallback: use random hash if no IOCs
            combined = secrets.token_hex(16)

        return hashlib.sha256(combined.encode()).hexdigest()

    def generate_short_id(self, length: int = 10) -> str:
        """Generate URL-friendly short ID (like URLScan.io)"""
        # Use alphanumeric characters (no confusing chars like 0/O, 1/l)
        chars = string.ascii_lowercase + string.digits
        chars = chars.replace('0', '').replace('o', '').replace('l', '').replace('1', '')
        return ''.join(secrets.choice(chars) for _ in range(length))

    def detect_threat_type(self, subject: str, body: str, detected_brands: List[str] = None) -> str:
        """Detect the type of phishing threat"""
        text = f"{subject} {body}".lower()

        if any(word in text for word in ['password', 'login', 'credential', 'sign in', 'verify your account']):
            return 'credential_theft'
        elif any(word in text for word in ['wire transfer', 'ceo', 'cfo', 'urgent payment', 'invoice']):
            return 'bec'
        elif detected_brands:
            return 'brand_impersonation'
        elif any(word in text for word in ['package', 'delivery', 'shipment', 'ups', 'fedex', 'dhl']):
            return 'delivery_scam'
        elif any(word in text for word in ['winner', 'lottery', 'prize', 'inheritance', 'million']):
            return 'reward_scam'
        elif any(word in text for word in ['virus', 'infected', 'tech support', 'call us']):
            return 'tech_support_scam'
        elif any(word in text for word in ['bank', 'account', 'suspended', 'limited']):
            return 'credential_theft'
        else:
            return 'social_engineering'

    def detect_tactics(self, text: str) -> List[str]:
        """Detect social engineering tactics used"""
        text_lower = text.lower()
        tactics = []

        if any(w in text_lower for w in ['official', 'security team', 'admin', 'support team', 'department']):
            tactics.append('authority')
        if any(w in text_lower for w in ['urgent', 'immediately', 'asap', '24 hours', '48 hours', 'expire']):
            tactics.append('urgency')
        if any(w in text_lower for w in ['suspended', 'blocked', 'unauthorized', 'fraud', 'compromised', 'limited']):
            tactics.append('fear')
        if any(w in text_lower for w in ['winner', 'prize', 'reward', 'free', 'bonus', 'refund']):
            tactics.append('greed')
        if any(w in text_lower for w in ['click here', 'find out', 'see attachment', 'view details']):
            tactics.append('curiosity')
        if any(w in text_lower for w in ['dear customer', 'valued member', 'trusted', 'secure']):
            tactics.append('trust')

        return tactics

    def detect_brands(self, text: str, sender: str = None) -> List[str]:
        """Detect impersonated brands"""
        combined = f"{text} {sender or ''}".lower()
        detected = []

        for brand in self.KNOWN_BRANDS:
            if brand in combined:
                detected.append(brand)

        return detected

    def _assess_domain_risk(self, domain: str) -> float:
        """Assess risk score for a domain"""
        if not domain:
            return 50.0

        risk = 50.0  # Base risk

        # Check for suspicious TLDs
        for tld in self.SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                risk += 30.0
                break

        # Check for IP-like domain
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain):
            risk += 25.0

        # Check for long domain (potential DGA)
        if len(domain) > 30:
            risk += 15.0

        # Check for excessive subdomains
        if domain.count('.') > 3:
            risk += 20.0

        # Check for numbers in domain name
        domain_name = domain.split('.')[0]
        if re.search(r'\d{4,}', domain_name):
            risk += 15.0

        return min(100.0, risk)

    def _assess_url_risk(self, url: str) -> float:
        """Assess risk score for a URL"""
        if not url:
            return 50.0

        risk = 50.0  # Base risk

        # URL shortener detection
        shorteners = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly', 'is.gd', 'buff.ly']
        if any(s in url.lower() for s in shorteners):
            risk += 25.0

        # IP-based URL
        if re.search(r'://\d+\.\d+\.\d+\.\d+', url):
            risk += 35.0

        # Very long URL
        if len(url) > 150:
            risk += 15.0

        # Contains @ symbol (basic auth spoofing)
        if '@' in url:
            risk += 30.0

        # Encoded characters
        if url.count('%') > 5:
            risk += 20.0

        # Check for suspicious keywords in URL
        suspicious_keywords = ['login', 'signin', 'verify', 'secure', 'account', 'update', 'confirm']
        if any(kw in url.lower() for kw in suspicious_keywords):
            risk += 10.0

        return min(100.0, risk)
