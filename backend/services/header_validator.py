import dns.resolver
import re
from typing import Dict, Optional

class HeaderValidator:
    """
    Validate email headers including SPF, DKIM, and DMARC
    """

    def __init__(self):
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 5
        self.resolver.lifetime = 5

    def validate_headers(self, headers: str, sender_email: str) -> Dict:
        """
        Validate email authentication headers
        """
        # Parse headers into dict
        header_dict = self._parse_headers(headers)

        # Extract domain from sender email
        domain = self._extract_domain(sender_email)

        # Check SPF
        spf_status = self._check_spf(header_dict, domain)

        # Check DKIM
        dkim_status = self._check_dkim(header_dict)

        # Check DMARC
        dmarc_status = self._check_dmarc(header_dict, domain)

        return {
            'spf_status': spf_status,
            'dkim_status': dkim_status,
            'dmarc_status': dmarc_status
        }

    def _parse_headers(self, headers: str) -> Dict:
        """
        Parse email headers into dictionary
        """
        header_dict = {}
        if not headers:
            return header_dict

        lines = headers.split('\n')
        current_header = None
        current_value = []

        for line in lines:
            if line and (line[0] == ' ' or line[0] == '\t'):
                # Continuation of previous header
                if current_header:
                    current_value.append(line.strip())
            else:
                # New header
                if current_header:
                    header_dict[current_header.lower()] = ' '.join(current_value)

                if ':' in line:
                    parts = line.split(':', 1)
                    current_header = parts[0].strip()
                    current_value = [parts[1].strip()] if len(parts) > 1 else []

        # Don't forget the last header
        if current_header:
            header_dict[current_header.lower()] = ' '.join(current_value)

        return header_dict

    def _extract_domain(self, email: str) -> str:
        """
        Extract domain from email address
        """
        match = re.search(r'@([a-zA-Z0-9.-]+)', email)
        return match.group(1) if match else ''

    def _check_spf(self, headers: Dict, domain: str) -> str:
        """
        Check SPF (Sender Policy Framework) status
        """
        # Look for SPF results in headers
        spf_header = headers.get('received-spf', '')

        if 'pass' in spf_header.lower():
            return 'pass'
        elif 'fail' in spf_header.lower():
            return 'fail'
        elif 'softfail' in spf_header.lower():
            return 'softfail'
        elif 'neutral' in spf_header.lower():
            return 'neutral'

        # Try to lookup SPF record
        if domain:
            try:
                txt_records = self.resolver.resolve(domain, 'TXT')
                for record in txt_records:
                    record_str = str(record)
                    if 'v=spf1' in record_str:
                        # SPF record exists but we can't validate without server IP
                        return 'record_found'
            except Exception:
                pass

        return 'none'

    def _check_dkim(self, headers: Dict) -> str:
        """
        Check DKIM (DomainKeys Identified Mail) status
        """
        # Look for DKIM signature header
        dkim_signature = headers.get('dkim-signature', '')

        if dkim_signature:
            # Look for validation results
            auth_results = headers.get('authentication-results', '')

            if 'dkim=pass' in auth_results.lower():
                return 'pass'
            elif 'dkim=fail' in auth_results.lower():
                return 'fail'
            else:
                # Signature present but status unknown
                return 'present'

        return 'none'

    def _check_dmarc(self, headers: Dict, domain: str) -> str:
        """
        Check DMARC (Domain-based Message Authentication) status
        """
        # Look for DMARC results in headers
        auth_results = headers.get('authentication-results', '')

        if 'dmarc=pass' in auth_results.lower():
            return 'pass'
        elif 'dmarc=fail' in auth_results.lower():
            return 'fail'

        # Try to lookup DMARC record
        if domain:
            try:
                dmarc_domain = f'_dmarc.{domain}'
                txt_records = self.resolver.resolve(dmarc_domain, 'TXT')
                for record in txt_records:
                    record_str = str(record)
                    if 'v=DMARC1' in record_str:
                        return 'record_found'
            except Exception:
                pass

        return 'none'
