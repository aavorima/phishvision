"""
Hybrid Phishing Analyzer
Combines rule-based NLP analysis with AI-powered Gemini analysis.
Uses intelligent routing to minimize API costs while maximizing accuracy.
"""

import json
from typing import Dict, List, Optional, Tuple
from models import PhishingPattern, db


class HybridAnalyzer:
    """
    Hybrid analyzer that combines NLP and AI analysis.

    Routing Logic:
    - NLP score < 15 (clear safe) → Return NLP only
    - NLP score > 80 (clear malicious) → Return NLP only
    - 15-80 (uncertain zone) → Use AI for verification
    - Always use AI for novel pattern detection if score > 25
    """

    # Thresholds for AI routing
    # Set to 0/100 to ALWAYS use AI until system learns enough patterns
    SAFE_THRESHOLD = 0        # Always use AI (was 15)
    MALICIOUS_THRESHOLD = 100 # Always use AI (was 80)
    UNCERTAIN_LOW = 25        # Below this in uncertain zone, likely safe but check
    UNCERTAIN_HIGH = 70       # Above this in uncertain zone, likely malicious but check

    def __init__(self, nlp_analyzer, gemini_analyzer):
        """
        Initialize with both analyzers.

        Args:
            nlp_analyzer: NLPAnalyzer instance
            gemini_analyzer: GeminiAnalyzer instance
        """
        self.nlp = nlp_analyzer
        self.ai = gemini_analyzer
        self.ai_enabled = gemini_analyzer.is_enabled() if gemini_analyzer else False

    def analyze_email(self, subject: str, body: str, sender: str,
                     attachments: List[str] = None, headers: str = "",
                     force_ai: bool = False, user_id: int = None) -> Dict:
        """
        Perform hybrid analysis on an email.

        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address
            attachments: List of attachment filenames
            headers: Email headers (optional)
            force_ai: Force AI analysis regardless of NLP score
            user_id: User ID for pattern relevance (optional)

        Returns:
            Comprehensive analysis result dictionary
        """
        # Step 1: Run NLP analysis (always - it's fast and free)
        nlp_result = self.nlp.analyze_email(
            subject=subject,
            body=body,
            sender=sender,
            attachments=attachments or [],
            headers=headers
        )

        nlp_score = nlp_result.get('risk_score', 50)
        nlp_classification = nlp_result.get('classification', 'suspicious')

        # Step 2: Determine if AI analysis is needed
        should_use_ai, ai_reason = self._should_use_ai(nlp_score, force_ai)

        # Step 3: If AI not needed or not available, return NLP-only result
        if not should_use_ai or not self.ai_enabled:
            return self._build_nlp_only_result(nlp_result, ai_reason)

        # Step 4: Get relevant patterns for few-shot learning
        patterns = self._get_relevant_patterns(subject, body, sender)

        # Step 5: Run AI analysis
        ai_result = self.ai.analyze_email(
            subject=subject,
            body=body,
            sender=sender,
            patterns=patterns
        )

        # Step 6: Combine results
        if ai_result.get('success'):
            return self._combine_results(nlp_result, ai_result, ai_reason)
        else:
            # AI failed, fall back to NLP only
            return self._build_nlp_only_result(nlp_result, 'AI analysis failed, using NLP only')

    def _should_use_ai(self, nlp_score: float, force_ai: bool) -> Tuple[bool, str]:
        """
        Determine whether to use AI analysis.

        Returns:
            Tuple of (should_use, reason)
        """
        if force_ai:
            return True, 'User requested AI analysis'

        if not self.ai_enabled:
            return False, 'AI analyzer not available'

        # Clear safe zone
        if nlp_score < self.SAFE_THRESHOLD:
            return False, f'NLP score {nlp_score:.1f} below safe threshold ({self.SAFE_THRESHOLD})'

        # Clear malicious zone
        if nlp_score > self.MALICIOUS_THRESHOLD:
            return False, f'NLP score {nlp_score:.1f} above malicious threshold ({self.MALICIOUS_THRESHOLD})'

        # Uncertain zone - use AI for verification
        if self.SAFE_THRESHOLD <= nlp_score <= self.MALICIOUS_THRESHOLD:
            return True, f'NLP score {nlp_score:.1f} in uncertain zone ({self.SAFE_THRESHOLD}-{self.MALICIOUS_THRESHOLD}), using AI verification'

        return False, 'Default: no AI needed'

    def _get_relevant_patterns(self, subject: str, body: str, sender: str,
                               limit: int = 5) -> List[PhishingPattern]:
        """
        Get relevant learned patterns for few-shot learning.

        Prioritizes:
        1. High effectiveness patterns
        2. Recently successful patterns
        3. Patterns matching similar indicators
        """
        try:
            # Get top effective active patterns
            patterns = PhishingPattern.query.filter_by(is_active=True)\
                .order_by(PhishingPattern.effectiveness_score.desc())\
                .limit(limit)\
                .all()

            return patterns
        except Exception as e:
            print(f"[WARNING] Failed to fetch patterns: {e}")
            return []

    def _build_nlp_only_result(self, nlp_result: Dict, reason: str) -> Dict:
        """Build result when only NLP analysis is used."""
        return {
            # NLP Results
            'risk_score': nlp_result.get('risk_score', 50),
            'classification': nlp_result.get('classification', 'suspicious'),
            'explanation': nlp_result.get('explanation', ''),
            'recommendations': nlp_result.get('recommendations', '[]'),

            # NLP Details
            'suspicious_keywords': nlp_result.get('suspicious_keywords', '{}'),
            'url_analysis': nlp_result.get('url_analysis', '{}'),
            'urgency_score': nlp_result.get('urgency_score', 0),
            'attachment_analysis': nlp_result.get('attachment_analysis', '{}'),
            'encoding_analysis': nlp_result.get('encoding_analysis', '{}'),
            'brand_impersonation': nlp_result.get('brand_impersonation', '{}'),
            'phishing_phrases_detected': nlp_result.get('phishing_phrases_detected', '[]'),
            'newsletter_context': nlp_result.get('newsletter_context'),

            # AI Results (empty for NLP-only)
            'ai_risk_score': None,
            'ai_classification': None,
            'ai_reasoning': None,
            'ai_tactics_detected': None,
            'ai_confidence': None,

            # Hybrid Results
            'hybrid_risk_score': nlp_result.get('risk_score', 50),
            'hybrid_classification': nlp_result.get('classification', 'suspicious'),
            'analysis_method': 'nlp',
            'routing_reason': reason,

            # Novel Pattern Detection
            'is_novel_pattern': False,
            'novel_pattern_description': None,

            # Language
            'detected_language': None
        }

    def _combine_results(self, nlp_result: Dict, ai_result: Dict, routing_reason: str) -> Dict:
        """
        Combine NLP and AI results with weighted scoring.

        AI weight is dynamic based on confidence:
        - Base weight: 0.4
        - Adjusted by confidence: 0.4 + (confidence * 0.3) → 0.4-0.7 range
        """
        nlp_score = nlp_result.get('risk_score', 50)
        ai_score = ai_result.get('risk_score', 50)
        ai_confidence = ai_result.get('confidence', 0.5)

        # Calculate dynamic AI weight based on confidence
        # Higher confidence = more weight on AI
        ai_weight = 0.4 + (ai_confidence * 0.3)  # Range: 0.4 - 0.7
        nlp_weight = 1.0 - ai_weight

        # Calculate hybrid score
        hybrid_score = (nlp_score * nlp_weight) + (ai_score * ai_weight)

        # Determine hybrid classification
        hybrid_classification = self._classify_hybrid_score(hybrid_score, ai_result)

        # Combine explanations
        combined_explanation = self._combine_explanations(nlp_result, ai_result)

        # Combine recommendations
        combined_recommendations = self._combine_recommendations(nlp_result, ai_result)

        return {
            # NLP Results
            'risk_score': nlp_score,
            'classification': nlp_result.get('classification', 'suspicious'),
            'explanation': combined_explanation,
            'recommendations': json.dumps(combined_recommendations),

            # NLP Details
            'suspicious_keywords': nlp_result.get('suspicious_keywords', '{}'),
            'url_analysis': nlp_result.get('url_analysis', '{}'),
            'urgency_score': nlp_result.get('urgency_score', 0),
            'attachment_analysis': nlp_result.get('attachment_analysis', '{}'),
            'encoding_analysis': nlp_result.get('encoding_analysis', '{}'),
            'brand_impersonation': nlp_result.get('brand_impersonation', '{}'),
            'phishing_phrases_detected': nlp_result.get('phishing_phrases_detected', '[]'),
            'newsletter_context': nlp_result.get('newsletter_context'),

            # AI Results
            'ai_risk_score': ai_result.get('risk_score'),
            'ai_classification': ai_result.get('classification'),
            'ai_reasoning': ai_result.get('reasoning'),
            'ai_tactics_detected': json.dumps(ai_result.get('tactics_detected', [])),
            'ai_confidence': ai_confidence,

            # Hybrid Results
            'hybrid_risk_score': round(hybrid_score, 2),
            'hybrid_classification': hybrid_classification,
            'analysis_method': 'hybrid',
            'routing_reason': routing_reason,
            'ai_weight': round(ai_weight, 2),
            'nlp_weight': round(nlp_weight, 2),

            # Novel Pattern Detection
            'is_novel_pattern': ai_result.get('is_novel_pattern', False),
            'novel_pattern_description': ai_result.get('novel_pattern_description'),

            # Language
            'detected_language': ai_result.get('language_detected'),

            # AI Indicators
            'ai_indicators': json.dumps(ai_result.get('indicators', {}))
        }

    def _classify_hybrid_score(self, score: float, ai_result: Dict) -> str:
        """
        Classify the hybrid score, considering AI insights.
        """
        ai_classification = ai_result.get('classification', 'suspicious')
        ai_confidence = ai_result.get('confidence', 0.5)

        # If AI is highly confident about malicious, trust it
        if ai_classification == 'malicious' and ai_confidence > 0.8:
            return 'malicious'

        # Score-based classification
        if score >= 70:
            return 'malicious'
        elif score >= 40:
            return 'suspicious'
        else:
            return 'safe'

    def _combine_explanations(self, nlp_result: Dict, ai_result: Dict) -> str:
        """Combine NLP and AI explanations into a coherent summary."""
        nlp_explanation = nlp_result.get('explanation', '')
        ai_reasoning = ai_result.get('reasoning', '')

        parts = []

        if nlp_explanation:
            parts.append(f"**Rule-based Analysis:** {nlp_explanation}")

        if ai_reasoning:
            parts.append(f"**AI Analysis:** {ai_reasoning}")

        # Add tactics if detected
        tactics = ai_result.get('tactics_detected', [])
        if tactics:
            parts.append(f"**Detected Tactics:** {', '.join(tactics)}")

        return '\n\n'.join(parts) if parts else 'Analysis completed.'

    def _combine_recommendations(self, nlp_result: Dict, ai_result: Dict) -> List[str]:
        """Combine and deduplicate recommendations from both analyzers."""
        recommendations = set()

        # Parse NLP recommendations
        try:
            nlp_recs = nlp_result.get('recommendations', '[]')
            if isinstance(nlp_recs, str):
                nlp_recs = json.loads(nlp_recs)
            if isinstance(nlp_recs, list):
                recommendations.update(nlp_recs)
        except:
            pass

        # Add AI recommendations
        ai_recs = ai_result.get('recommendations', [])
        if isinstance(ai_recs, list):
            recommendations.update(ai_recs)

        return list(recommendations)[:10]  # Limit to 10 recommendations

    def analyze_with_feedback_context(self, subject: str, body: str, sender: str,
                                      user_id: int = None,
                                      similar_feedback: List = None) -> Dict:
        """
        Analyze email with context from similar user feedback.

        This method considers past user feedback on similar emails
        to improve accuracy over time.
        """
        # Get base analysis
        result = self.analyze_email(
            subject=subject,
            body=body,
            sender=sender,
            force_ai=True,
            user_id=user_id
        )

        # If we have similar feedback indicating this type was misclassified before
        if similar_feedback:
            # Count feedback types
            false_negatives = sum(1 for f in similar_feedback if f.feedback_type == 'false_negative')
            false_positives = sum(1 for f in similar_feedback if f.feedback_type == 'false_positive')

            # Adjust confidence if we've seen similar false classifications
            if false_negatives > false_positives and false_negatives >= 2:
                # Similar emails were marked as phishing by users but we said safe
                # Increase risk score
                adjustment = min(false_negatives * 5, 20)  # Max +20 adjustment
                result['hybrid_risk_score'] = min(100, result['hybrid_risk_score'] + adjustment)
                result['feedback_adjustment'] = f'+{adjustment} (similar emails reported as phishing)'

            elif false_positives > false_negatives and false_positives >= 2:
                # Similar emails were marked as safe by users but we said phishing
                # Decrease risk score
                adjustment = min(false_positives * 5, 20)  # Max -20 adjustment
                result['hybrid_risk_score'] = max(0, result['hybrid_risk_score'] - adjustment)
                result['feedback_adjustment'] = f'-{adjustment} (similar emails reported as safe)'

        return result


def create_hybrid_analyzer():
    """
    Factory function to create a HybridAnalyzer with initialized dependencies.
    """
    from services.nlp_analyzer import NLPAnalyzer
    from services.gemini_analyzer import GeminiAnalyzer

    nlp = NLPAnalyzer()
    ai = GeminiAnalyzer()

    return HybridAnalyzer(nlp, ai)
