"""
Gemini AI-Powered Phishing Analyzer
Uses Google Gemini for intelligent semantic analysis of emails.
Complements the rule-based NLP analyzer with AI understanding.
"""

import os
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("[WARNING] google-generativeai not installed")


class GeminiAnalyzer:
    """
    AI-powered phishing analyzer using Google Gemini.
    Provides semantic understanding and zero-day pattern detection.
    """

    # Industry-standard phishing indicators (MITRE ATT&CK, APWG, CISA)
    PHISHING_INDICATORS = {
        'social_engineering': [
            'authority_exploitation',      # Impersonating boss/CEO/IT
            'urgency_pressure',           # Time-limited threats
            'scarcity_appeal',            # Limited offers
            'social_proof',               # "Others have done this"
            'reciprocity',                # "We did this for you"
            'fear_tactics',               # Threatening consequences
            'curiosity_exploitation',     # Enticing to click
            'trust_building',             # Building false rapport
        ],
        'credential_theft': [
            'login_request',
            'password_reset_lure',
            'account_verification',
            'mfa_bypass_attempt',
            'session_hijack_setup',
            'form_submission_request',
        ],
        'technical': [
            'sender_spoofing',
            'domain_typosquatting',
            'url_obfuscation',
            'attachment_malware',
            'header_manipulation',
            'link_text_mismatch',
        ],
        'content': [
            'grammatical_errors',
            'tone_mismatch',
            'brand_inconsistency',
            'unrealistic_promises',
            'threatening_language',
            'generic_greeting',
        ]
    }

    def __init__(self):
        """Initialize Gemini API connection."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.enabled = False
        self.model_name = None

        if not GENAI_AVAILABLE:
            print("[ERROR] google-generativeai package not available")
            return

        if not self.api_key:
            print("[WARNING] GEMINI_API_KEY not found in environment")
            return

        try:
            genai.configure(api_key=self.api_key)

            # Try different models (some may have separate quotas)
            # Prioritize lite models which have better quota availability
            model_options = [
                'gemini-2.5-flash-lite',  # Best quota availability
                'gemini-2.5-flash',       # Best quality
                'gemini-2.0-flash-lite',
                'gemini-2.0-flash',
                'gemini-flash-lite-latest',
                'gemini-flash-latest'
            ]

            for model_name in model_options:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    self.enabled = True
                    print(f"[INFO] GeminiAnalyzer initialized with {model_name}")
                    break
                except Exception as e:
                    print(f"[WARNING] Could not load {model_name}: {e}")
                    continue

            if not self.enabled:
                print("[ERROR] No Gemini model could be loaded")

        except Exception as e:
            print(f"[ERROR] GeminiAnalyzer initialization failed: {e}")

    def is_enabled(self) -> bool:
        """Check if Gemini analyzer is available."""
        return self.enabled

    def analyze_email(self, subject: str, body: str, sender: str,
                      patterns: List = None, language: str = 'auto') -> Dict:
        """
        Perform AI-powered phishing analysis.

        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address
            patterns: List of PhishingPattern objects for few-shot learning
            language: Language code or 'auto' for detection

        Returns:
            Dictionary with AI analysis results
        """
        if not self.enabled:
            return self._get_disabled_response()

        try:
            # Detect language if auto
            if language == 'auto':
                language = self._detect_language(f"{subject} {body}")

            # Build analysis prompt
            prompt = self._build_analysis_prompt(subject, body, sender, patterns, language)

            # Call Gemini API
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent analysis
                    max_output_tokens=2048,
                )
            )

            # Parse response
            return self._parse_response(response.text, language)

        except Exception as e:
            print(f"[ERROR] Gemini analysis failed: {e}")
            return self._get_error_response(str(e))

    def _build_analysis_prompt(self, subject: str, body: str, sender: str,
                                patterns: List = None, language: str = 'en') -> str:
        """Build world-class phishing detection prompt with deep threat intelligence."""

        # Build few-shot examples section
        few_shot_section = ""
        if patterns:
            few_shot_section = self._build_few_shot_examples(patterns)

        # Truncate body for token efficiency
        body_truncated = body[:4000] if len(body) > 4000 else body

        prompt = f"""You are an elite cybersecurity threat analyst with 20+ years of experience in email security, social engineering detection, and threat intelligence. You have trained security teams at Fortune 500 companies and government agencies. Your analysis has a 99.7% accuracy rate.

{few_shot_section}

═══════════════════════════════════════════════════════════════════════════════
                              EMAIL UNDER ANALYSIS
═══════════════════════════════════════════════════════════════════════════════
FROM: {sender}
SUBJECT: {subject}
BODY:
{body_truncated}
═══════════════════════════════════════════════════════════════════════════════

**YOUR MISSION:** Perform a deep forensic analysis of this email. Think like an attacker AND a defender. Consider what a sophisticated threat actor would do and what subtle signs they might leave.

**MULTI-LANGUAGE DETECTION:**
This email may be in ANY language (English, Spanish, French, German, Russian, Chinese, Japanese, Korean, Arabic, Turkish, Portuguese, Italian, Dutch, Polish, Vietnamese, Thai, Hindi, etc.). Analyze the content in its NATIVE language - do NOT require translation. Phishing attacks are GLOBAL.

═══════════════════════════════════════════════════════════════════════════════
                    COMPREHENSIVE THREAT ANALYSIS FRAMEWORK
═══════════════════════════════════════════════════════════════════════════════

**PHASE 1: SENDER FORENSICS (Critical)**
□ Domain Analysis:
  - Is the domain newly registered (DGA-style)?
  - Typosquatting detection (microsоft vs microsoft, amaz0n, g00gle)
  - Homoglyph/punycode attacks (Cyrillic а vs Latin a)
  - Subdomain abuse (login.microsoft.com.evil.com)
  - Free email services for corporate impersonation
  - Display name vs actual email mismatch
□ Sender Reputation:
  - Known spam/phishing sender patterns
  - Geographic anomalies (claimed US company, .ru domain)

**PHASE 2: PSYCHOLOGICAL MANIPULATION DETECTION (MITRE ATT&CK T1566)**
□ Authority Exploitation:
  - CEO/CFO impersonation (Business Email Compromise - BEC)
  - IT department impersonation
  - Government/law enforcement impersonation
  - Bank/financial institution impersonation
□ Urgency & Scarcity:
  - Artificial deadlines ("24 hours", "immediately", "expires today")
  - Limited availability ("only 3 spots left", "exclusive offer")
  - Consequences for inaction
□ Fear, Uncertainty, Doubt (FUD):
  - Account suspension threats
  - Legal action threats
  - Security breach warnings
  - Financial loss warnings
□ Greed & Reward:
  - Prize/lottery notifications
  - Unexpected inheritance
  - Job offers too good to be true
  - Investment opportunities with guaranteed returns
□ Curiosity & Trust:
  - Fake document sharing
  - "Someone shared a file with you"
  - Personal information as bait
  - Fake social proof

**PHASE 3: ATTACK VECTOR IDENTIFICATION**
□ Credential Harvesting:
  - Fake login pages (Microsoft 365, Google, banking)
  - Password reset requests
  - MFA/2FA bypass attempts (adversary-in-the-middle)
  - SSO token theft
□ Malware Delivery:
  - Suspicious attachments (.exe, .scr, .js, .vbs, .hta, .iso, .img)
  - Macro-enabled documents (.docm, .xlsm)
  - HTML smuggling
  - Password-protected archives
□ Financial Fraud:
  - Wire transfer requests
  - Invoice manipulation
  - Payment redirect scams
  - Money mule recruitment
□ Data Exfiltration:
  - Requests for sensitive documents
  - W-2/tax form phishing
  - HR data requests
  - Customer list requests

**PHASE 4: CONTENT DEEP ANALYSIS**
□ Linguistic Anomalies:
  - Grammar/spelling inconsistent with claimed sender
  - Machine translation artifacts
  - Unusual phrasing for the language
  - Formal/informal tone mismatch
□ Brand Impersonation:
  - Logo/branding inconsistencies
  - Wrong company name variations
  - Outdated templates
  - Missing standard footer elements
□ Link Analysis:
  - URL shorteners hiding destination
  - Misleading anchor text
  - Multiple redirects
  - Data: or javascript: URIs
  - QR codes (quishing)
□ Contextual Red Flags:
  - Unexpected communication
  - Request doesn't match sender's role
  - Information the sender should already have
  - Breaking normal communication patterns

**PHASE 5: EMERGING THREATS (2024-2025)**
□ AI-Generated Phishing:
  - Unusually polished content
  - Personalization without prior relationship
  - Context-aware social engineering
□ Callback Phishing (TOAD - Telephone-Oriented Attack Delivery):
  - Requests to call a phone number
  - Fake support/cancellation notices
□ QR Code Attacks (Quishing):
  - QR codes in emails
  - Bypassing email security filters
□ Multi-Channel Attacks:
  - Email + SMS + Voice coordination
  - Social media + email combination
□ Supply Chain Compromise:
  - Legitimate vendor account takeover
  - Thread hijacking

**PHASE 6: LEGITIMATE EMAIL INDICATORS**
□ Signs of Legitimacy:
  - Consistent sender history
  - Proper SPF/DKIM/DMARC (implied by domain)
  - Expected communication
  - Verifiable contact information
  - Unsubscribe options (marketing)
  - No urgency to click/act
  - Professional formatting
  - Links to official domains

═══════════════════════════════════════════════════════════════════════════════
                              DECISION MATRIX
═══════════════════════════════════════════════════════════════════════════════

MALICIOUS (70-100): Clear phishing attempt, credential theft, malware delivery, financial fraud, impersonation with malicious intent
SUSPICIOUS (30-69): Multiple red flags, unclear sender intent, potential social engineering, warrants caution
SAFE (0-29): Legitimate communication, expected sender, no manipulation tactics, verifiable source

═══════════════════════════════════════════════════════════════════════════════
                              OUTPUT REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

CRITICAL: Keep response CONCISE. Max 2-3 items per array. Short strings only.
Respond with ONLY valid JSON (no markdown, no code blocks):

{{
  "classification": "safe|suspicious|malicious",
  "risk_score": 0-100,
  "confidence": 0.0-1.0,
  "reasoning": "2 sentences max explaining classification",
  "tactics_detected": ["tactic1", "tactic2"],
  "indicators": {{
    "social_engineering": [],
    "credential_theft": [],
    "technical": [],
    "content": []
  }},
  "attack_type": "BEC|credential_phishing|malware_delivery|financial_fraud|advance_fee|lottery_scam|tech_support_scam|delivery_scam|romance_scam|job_scam|legitimate|unknown",
  "impersonated_entity": "brand or null",
  "is_novel_pattern": false,
  "novel_pattern_description": null,
  "language_detected": "ISO code",
  "recommendations": ["action1", "action2"]
}}"""

        return prompt

    def _build_few_shot_examples(self, patterns: List) -> str:
        """Build few-shot learning examples from known patterns."""
        if not patterns:
            return ""

        examples = []

        # Select top 5 most effective patterns
        sorted_patterns = sorted(
            [p for p in patterns if p.is_active],
            key=lambda p: p.effectiveness_score,
            reverse=True
        )[:5]

        for pattern in sorted_patterns:
            # Parse indicators
            try:
                indicators = json.loads(pattern.indicators) if pattern.indicators else []
            except:
                indicators = []

            example = f"""
**KNOWN PHISHING PATTERN ({pattern.pattern_type.upper()}):**
Subject example: {pattern.example_subject or 'N/A'}
Body snippet: {(pattern.example_body_snippet or 'N/A')[:200]}
Indicators: {', '.join(indicators[:5])}
Classification: malicious (confirmed phishing)
"""
            examples.append(example)

        if examples:
            return """
**LEARNED PATTERNS FROM CONFIRMED PHISHING:**
Use these examples to inform your analysis. Similar patterns should be classified as malicious.

""" + "\n".join(examples) + "\n"

        return ""

    def _parse_response(self, response_text: str, language: str = 'en') -> Dict:
        """Parse Gemini's JSON response."""
        try:
            # Clean response - remove markdown code blocks if present
            text = response_text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            # Find JSON object
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate and normalize response
                return {
                    'success': True,
                    'classification': self._validate_classification(result.get('classification', 'suspicious')),
                    'risk_score': self._validate_score(result.get('risk_score', 50)),
                    'confidence': self._validate_confidence(result.get('confidence', 0.5)),
                    'reasoning': result.get('reasoning', 'Analysis completed'),
                    'tactics_detected': result.get('tactics_detected', []),
                    'indicators': result.get('indicators', {}),
                    'is_novel_pattern': result.get('is_novel_pattern', False),
                    'novel_pattern_description': result.get('novel_pattern_description'),
                    'language_detected': result.get('language_detected', language),
                    'recommendations': self._ensure_list(result.get('recommendations', []))
                }

        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse error: {e}")
            print(f"[DEBUG] Raw response: {response_text[:500]}")
        except Exception as e:
            print(f"[ERROR] Response parsing failed: {e}")

        return self._get_error_response("Failed to parse AI response")

    def _validate_classification(self, classification: str) -> str:
        """Validate classification value."""
        valid = ['safe', 'suspicious', 'malicious']
        return classification.lower() if classification.lower() in valid else 'suspicious'

    def _validate_score(self, score) -> float:
        """Validate and clamp risk score."""
        try:
            score = float(score)
            return max(0, min(100, score))
        except:
            return 50.0

    def _validate_confidence(self, confidence) -> float:
        """Validate confidence score."""
        try:
            conf = float(confidence)
            return max(0.0, min(1.0, conf))
        except:
            return 0.5

    def _ensure_list(self, value) -> List:
        """Ensure value is a list."""
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        return []

    def _detect_language(self, text: str) -> str:
        """Detect language of email content."""
        # Turkish specific characters
        turkish_chars = set('ğüşöçıİĞÜŞÖÇ')
        # Azerbaijani specific characters
        azerbaijani_chars = set('əƏ')
        # Russian/Cyrillic
        cyrillic_chars = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
        # Arabic
        arabic_range = range(0x0600, 0x06FF)

        text_chars = set(text)

        if text_chars & azerbaijani_chars:
            return 'az'
        if text_chars & turkish_chars:
            return 'tr'
        if text_chars & cyrillic_chars:
            return 'ru'
        if any(ord(c) in arabic_range for c in text):
            return 'ar'

        return 'en'

    def _get_disabled_response(self) -> Dict:
        """Return response when AI is disabled."""
        return {
            'success': False,
            'error': 'AI analyzer disabled (no API key or model unavailable)',
            'classification': None,
            'risk_score': None,
            'confidence': None,
            'reasoning': None,
            'tactics_detected': [],
            'indicators': {},
            'is_novel_pattern': False,
            'novel_pattern_description': None,
            'language_detected': None,
            'recommendations': []
        }

    def _get_error_response(self, error: str) -> Dict:
        """Return error response."""
        return {
            'success': False,
            'error': error,
            'classification': None,
            'risk_score': None,
            'confidence': None,
            'reasoning': None,
            'tactics_detected': [],
            'indicators': {},
            'is_novel_pattern': False,
            'novel_pattern_description': None,
            'language_detected': None,
            'recommendations': []
        }

    def analyze_for_pattern_extraction(self, subject: str, body: str, sender: str) -> Dict:
        """
        Analyze email specifically to extract pattern information for learning.
        Used when creating new PhishingPattern from feedback.
        """
        if not self.enabled:
            return {'success': False, 'error': 'AI not available'}

        prompt = f"""Analyze this confirmed phishing email and extract the attack pattern:

From: {sender}
Subject: {subject}
Body: {body[:2000]}

Return JSON with:
{{
  "pattern_type": "social_engineering|credential_theft|bec|spear_phishing|delivery_scam|tech_support_scam|reward_scam|brand_impersonation|invoice_scam|payment_redirect",
  "indicators": ["indicator1", "indicator2", "indicator3"],
  "tactics": {{
    "authority": true|false,
    "urgency": true|false,
    "fear": true|false,
    "greed": true|false,
    "curiosity": true|false,
    "trust": true|false
  }},
  "key_phrases": ["phrase that makes this phishing"],
  "target_action": "what the attacker wants victim to do"
}}

JSON only, no markdown:"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'\s*```$', '', text)

            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group(0))
                return {'success': True, **result}

        except Exception as e:
            print(f"[ERROR] Pattern extraction failed: {e}")

        return {'success': False, 'error': 'Pattern extraction failed'}
