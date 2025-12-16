"""
Feedback Learning Service
Processes user feedback to create new phishing patterns and improve detection.
Implements the self-learning loop for zero-day phishing detection.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import func, and_, or_
from models import db, AnalysisFeedback, PhishingPattern, EmailAnalysis


class FeedbackLearner:
    """
    Self-learning system that processes user feedback to:
    1. Create new phishing patterns from confirmed attacks
    2. Adjust effectiveness scores of existing patterns
    3. Identify false positive patterns to deprecate
    4. Enable few-shot learning for Gemini AI
    """

    # Thresholds for pattern creation
    MIN_SIMILAR_REPORTS = 2  # Minimum similar false negatives to create pattern
    SIMILARITY_THRESHOLD = 0.6  # Text similarity threshold
    PATTERN_EFFECTIVENESS_DECAY = 0.95  # Daily decay rate for unused patterns
    FALSE_POSITIVE_PENALTY = 10  # Score reduction for false positives

    def __init__(self, gemini_analyzer=None):
        """
        Initialize with optional Gemini analyzer for AI-powered pattern extraction.
        """
        self.gemini = gemini_analyzer
        self.ai_enabled = gemini_analyzer and gemini_analyzer.is_enabled()

    def process_feedback(self, feedback: AnalysisFeedback) -> Dict:
        """
        Process a single piece of user feedback.

        Args:
            feedback: AnalysisFeedback instance with user correction

        Returns:
            Processing result with any new patterns created
        """
        result = {
            'processed': False,
            'pattern_created': False,
            'pattern_updated': False,
            'pattern_id': None,
            'action': None,
            'details': None
        }

        try:
            if feedback.feedback_type == 'false_negative':
                # User says it's phishing but we said safe
                result = self._handle_false_negative(feedback)

            elif feedback.feedback_type == 'false_positive':
                # User says it's safe but we said phishing
                result = self._handle_false_positive(feedback)

            elif feedback.feedback_type == 'correct':
                # Correct classification - reinforce patterns
                result = self._handle_correct(feedback)

            # Mark feedback as processed
            feedback.is_processed = True
            feedback.processed_at = datetime.utcnow()
            db.session.commit()

            result['processed'] = True

        except Exception as e:
            print(f"[ERROR] Feedback processing failed: {e}")
            db.session.rollback()
            result['error'] = str(e)

        return result

    def _handle_false_negative(self, feedback: AnalysisFeedback) -> Dict:
        """
        Handle case where we missed a phishing email.
        This is critical - we need to learn from these mistakes.
        """
        result = {
            'pattern_created': False,
            'pattern_updated': False,
            'pattern_id': None,
            'action': 'false_negative_processed'
        }

        # Get the original analysis
        analysis = EmailAnalysis.query.get(feedback.analysis_id)
        if not analysis:
            return result

        # Find similar false negative reports
        similar_reports = self._find_similar_false_negatives(
            analysis.email_subject,
            analysis.email_body,
            analysis.email_from
        )

        # If we have enough similar reports, create a new pattern
        if len(similar_reports) >= self.MIN_SIMILAR_REPORTS:
            pattern = self._create_pattern_from_feedback(analysis, similar_reports)
            if pattern:
                result['pattern_created'] = True
                result['pattern_id'] = pattern.id
                result['action'] = 'new_pattern_created'
                result['details'] = f"Created pattern '{pattern.pattern_type}' from {len(similar_reports)} similar reports"

                # Link feedback to the new pattern
                feedback.learned_pattern_id = pattern.id
        else:
            result['action'] = 'logged_for_future_learning'
            result['details'] = f"Report logged. Need {self.MIN_SIMILAR_REPORTS - len(similar_reports)} more similar reports to create pattern."

        return result

    def _handle_false_positive(self, feedback: AnalysisFeedback) -> Dict:
        """
        Handle case where we incorrectly flagged a safe email.
        Reduce effectiveness of patterns that triggered this false positive.
        """
        result = {
            'pattern_created': False,
            'pattern_updated': False,
            'pattern_id': None,
            'action': 'false_positive_processed'
        }

        # Get the original analysis
        analysis = EmailAnalysis.query.get(feedback.analysis_id)
        if not analysis:
            return result

        # Find patterns that may have caused this false positive
        affected_patterns = self._find_triggering_patterns(analysis)

        updated_count = 0
        for pattern in affected_patterns:
            # Reduce effectiveness score
            pattern.effectiveness_score = max(0, pattern.effectiveness_score - self.FALSE_POSITIVE_PENALTY)
            pattern.false_positive_count += 1

            # If pattern has too many false positives, deactivate it
            if pattern.false_positive_count > pattern.detection_count * 0.3:  # >30% FP rate
                pattern.is_active = False
                result['details'] = f"Pattern {pattern.id} deactivated due to high false positive rate"

            updated_count += 1

        if updated_count > 0:
            result['pattern_updated'] = True
            result['action'] = f'adjusted_{updated_count}_patterns'
            db.session.commit()

        return result

    def _handle_correct(self, feedback: AnalysisFeedback) -> Dict:
        """
        Handle correct classification - reinforce successful patterns.
        """
        result = {
            'pattern_created': False,
            'pattern_updated': False,
            'pattern_id': None,
            'action': 'correct_classification_logged'
        }

        # Get the original analysis
        analysis = EmailAnalysis.query.get(feedback.analysis_id)
        if not analysis:
            return result

        # If it was correctly identified as malicious, boost relevant patterns
        if feedback.user_classification == 'malicious':
            affected_patterns = self._find_triggering_patterns(analysis)

            for pattern in affected_patterns:
                # Boost effectiveness score
                pattern.effectiveness_score = min(100, pattern.effectiveness_score + 2)
                pattern.detection_count += 1

            if affected_patterns:
                result['pattern_updated'] = True
                result['action'] = f'reinforced_{len(affected_patterns)}_patterns'
                db.session.commit()

        return result

    def _find_similar_false_negatives(self, subject: str, body: str, sender: str,
                                       days: int = 30) -> List[EmailAnalysis]:
        """
        Find similar emails that were also reported as false negatives.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get recent false negative feedback
        false_negative_feedbacks = AnalysisFeedback.query.filter(
            AnalysisFeedback.feedback_type == 'false_negative',
            AnalysisFeedback.created_at >= cutoff
        ).all()

        similar = []
        subject_lower = subject.lower() if subject else ''
        body_lower = body.lower() if body else ''
        sender_domain = self._extract_domain(sender)

        for fb in false_negative_feedbacks:
            analysis = EmailAnalysis.query.get(fb.analysis_id)
            if not analysis:
                continue

            # Calculate similarity
            similarity = self._calculate_similarity(
                subject_lower, body_lower, sender_domain,
                (analysis.email_subject or '').lower(),
                (analysis.email_body or '').lower(),
                self._extract_domain(analysis.email_from)
            )

            if similarity >= self.SIMILARITY_THRESHOLD:
                similar.append(analysis)

        return similar

    def _calculate_similarity(self, subj1: str, body1: str, domain1: str,
                             subj2: str, body2: str, domain2: str) -> float:
        """
        Calculate similarity between two emails.
        Simple approach using keyword overlap and domain matching.
        """
        score = 0.0

        # Domain match is strong indicator
        if domain1 and domain2 and domain1 == domain2:
            score += 0.3

        # Subject similarity (keyword overlap)
        subj1_words = set(subj1.split())
        subj2_words = set(subj2.split())
        if subj1_words and subj2_words:
            overlap = len(subj1_words & subj2_words) / max(len(subj1_words), len(subj2_words))
            score += overlap * 0.3

        # Body similarity (key phrases)
        body1_words = set(body1.split())
        body2_words = set(body2.split())
        if body1_words and body2_words:
            overlap = len(body1_words & body2_words) / max(len(body1_words), len(body2_words))
            score += overlap * 0.4

        return min(1.0, score)

    def _extract_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not email or '@' not in email:
            return ''
        return email.split('@')[-1].lower()

    def _create_pattern_from_feedback(self, analysis: EmailAnalysis,
                                      similar_reports: List[EmailAnalysis]) -> Optional[PhishingPattern]:
        """
        Create a new PhishingPattern from user feedback.
        Uses AI if available for better categorization.
        """
        # Use AI to extract pattern details if available
        if self.ai_enabled:
            ai_pattern = self.gemini.analyze_for_pattern_extraction(
                analysis.email_subject or '',
                analysis.email_body or '',
                analysis.email_from or ''
            )
            if ai_pattern.get('success'):
                return self._create_pattern_from_ai(analysis, ai_pattern, similar_reports)

        # Fallback: Create pattern from heuristics
        return self._create_pattern_from_heuristics(analysis, similar_reports)

    def _create_pattern_from_ai(self, analysis: EmailAnalysis,
                                ai_result: Dict,
                                similar_reports: List[EmailAnalysis]) -> PhishingPattern:
        """Create pattern using AI-extracted information."""
        pattern = PhishingPattern(
            pattern_type=ai_result.get('pattern_type', 'unknown'),
            indicators=json.dumps(ai_result.get('indicators', [])),
            tactics=json.dumps(ai_result.get('tactics', {})),
            example_subject=analysis.email_subject,
            example_body_snippet=(analysis.email_body or '')[:500],
            effectiveness_score=70.0,  # Start with moderate effectiveness
            detection_count=len(similar_reports),
            false_positive_count=0,
            source='user_feedback',
            is_active=True,
            language=analysis.detected_language or 'en'
        )

        db.session.add(pattern)
        db.session.commit()

        # Link all similar reports to this pattern
        for fb in AnalysisFeedback.query.filter(
            AnalysisFeedback.analysis_id.in_([r.id for r in similar_reports])
        ).all():
            fb.learned_pattern_id = pattern.id

        db.session.commit()

        print(f"[INFO] Created new pattern {pattern.id} of type '{pattern.pattern_type}' from {len(similar_reports)} reports")
        return pattern

    def _create_pattern_from_heuristics(self, analysis: EmailAnalysis,
                                        similar_reports: List[EmailAnalysis]) -> PhishingPattern:
        """Create pattern using rule-based heuristics."""
        # Detect pattern type from content
        pattern_type = self._detect_pattern_type(analysis)

        # Extract indicators from text
        indicators = self._extract_indicators(analysis)

        # Detect tactics used
        tactics = self._detect_tactics(analysis)

        pattern = PhishingPattern(
            pattern_type=pattern_type,
            indicators=json.dumps(indicators),
            tactics=json.dumps(tactics),
            example_subject=analysis.email_subject,
            example_body_snippet=(analysis.email_body or '')[:500],
            effectiveness_score=60.0,  # Lower than AI-extracted
            detection_count=len(similar_reports),
            false_positive_count=0,
            source='user_feedback',
            is_active=True,
            language=analysis.detected_language or 'en'
        )

        db.session.add(pattern)
        db.session.commit()

        return pattern

    def _detect_pattern_type(self, analysis: EmailAnalysis) -> str:
        """Detect the type of phishing pattern from email content."""
        text = f"{analysis.email_subject or ''} {analysis.email_body or ''}".lower()

        # Pattern type detection rules
        patterns = {
            'credential_theft': ['password', 'login', 'sign in', 'verify account', 'confirm identity'],
            'bec': ['wire transfer', 'payment', 'invoice', 'ceo', 'urgent request'],
            'brand_impersonation': ['amazon', 'paypal', 'microsoft', 'apple', 'netflix', 'bank'],
            'delivery_scam': ['delivery', 'package', 'shipment', 'tracking', 'fedex', 'ups'],
            'reward_scam': ['winner', 'prize', 'lottery', 'gift card', 'free', 'congratulations'],
            'tech_support_scam': ['virus', 'infected', 'security alert', 'call us', 'tech support'],
            'invoice_scam': ['invoice', 'payment due', 'past due', 'billing'],
            'payment_redirect': ['bank details', 'new account', 'updated payment']
        }

        max_matches = 0
        detected_type = 'social_engineering'

        for ptype, keywords in patterns.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_type = ptype

        return detected_type

    def _extract_indicators(self, analysis: EmailAnalysis) -> List[str]:
        """Extract phishing indicators from email."""
        indicators = []
        text = f"{analysis.email_subject or ''} {analysis.email_body or ''}".lower()

        # Common indicator patterns
        indicator_checks = [
            ('urgency_language', ['urgent', 'immediately', 'asap', 'right now', 'within 24 hours']),
            ('threat_language', ['suspended', 'terminated', 'blocked', 'disabled', 'closed']),
            ('action_request', ['click here', 'click below', 'verify now', 'confirm now']),
            ('credential_request', ['password', 'username', 'ssn', 'credit card']),
            ('generic_greeting', ['dear customer', 'dear user', 'dear valued']),
            ('suspicious_sender', ['noreply', 'support@', 'security@', 'alert@']),
        ]

        for indicator_name, keywords in indicator_checks:
            if any(kw in text for kw in keywords):
                indicators.append(indicator_name)

        return indicators

    def _detect_tactics(self, analysis: EmailAnalysis) -> Dict[str, bool]:
        """Detect social engineering tactics used in email."""
        text = f"{analysis.email_subject or ''} {analysis.email_body or ''}".lower()

        tactics = {
            'authority': any(w in text for w in ['ceo', 'director', 'manager', 'official', 'government']),
            'urgency': any(w in text for w in ['urgent', 'immediately', 'expires', 'deadline', '24 hours']),
            'fear': any(w in text for w in ['suspended', 'blocked', 'legal action', 'penalty', 'arrest']),
            'greed': any(w in text for w in ['winner', 'prize', 'reward', 'free', 'bonus', '$']),
            'curiosity': any(w in text for w in ['see attached', 'click to view', 'exclusive', 'secret']),
            'trust': any(w in text for w in ['verified', 'secure', 'official', 'trusted', 'certified'])
        }

        return tactics

    def _find_triggering_patterns(self, analysis: EmailAnalysis) -> List[PhishingPattern]:
        """
        Find patterns that may have triggered the classification of this email.
        """
        if not analysis:
            return []

        text = f"{analysis.email_subject or ''} {analysis.email_body or ''}".lower()

        # Get active patterns
        patterns = PhishingPattern.query.filter_by(is_active=True).all()

        triggered = []
        for pattern in patterns:
            # Check if pattern indicators match
            try:
                indicators = json.loads(pattern.indicators) if pattern.indicators else []
                # If any indicator matches, this pattern might have triggered
                if any(ind.lower() in text for ind in indicators):
                    triggered.append(pattern)
            except:
                pass

        return triggered

    def batch_process_feedback(self, limit: int = 100) -> Dict:
        """
        Process multiple unprocessed feedback entries.
        Run this periodically (e.g., daily) to learn from accumulated feedback.
        """
        unprocessed = AnalysisFeedback.query.filter_by(is_processed=False)\
            .order_by(AnalysisFeedback.created_at)\
            .limit(limit)\
            .all()

        results = {
            'total': len(unprocessed),
            'processed': 0,
            'patterns_created': 0,
            'patterns_updated': 0,
            'errors': 0
        }

        for feedback in unprocessed:
            result = self.process_feedback(feedback)

            if result.get('processed'):
                results['processed'] += 1
            if result.get('pattern_created'):
                results['patterns_created'] += 1
            if result.get('pattern_updated'):
                results['patterns_updated'] += 1
            if result.get('error'):
                results['errors'] += 1

        return results

    def decay_pattern_scores(self) -> int:
        """
        Apply daily decay to pattern effectiveness scores.
        Patterns that aren't being used should gradually lose relevance.
        """
        updated = 0
        patterns = PhishingPattern.query.filter_by(is_active=True).all()

        for pattern in patterns:
            # Apply decay
            new_score = pattern.effectiveness_score * self.PATTERN_EFFECTIVENESS_DECAY
            pattern.effectiveness_score = max(10, new_score)  # Minimum score of 10
            updated += 1

        db.session.commit()
        return updated

    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning system."""
        total_patterns = PhishingPattern.query.count()
        active_patterns = PhishingPattern.query.filter_by(is_active=True).count()
        user_patterns = PhishingPattern.query.filter_by(source='user_feedback').count()

        total_feedback = AnalysisFeedback.query.count()
        processed_feedback = AnalysisFeedback.query.filter_by(is_processed=True).count()

        # Feedback type breakdown
        false_negatives = AnalysisFeedback.query.filter_by(feedback_type='false_negative').count()
        false_positives = AnalysisFeedback.query.filter_by(feedback_type='false_positive').count()
        correct = AnalysisFeedback.query.filter_by(feedback_type='correct').count()

        # Top effective patterns
        top_patterns = PhishingPattern.query.filter_by(is_active=True)\
            .order_by(PhishingPattern.effectiveness_score.desc())\
            .limit(5)\
            .all()

        return {
            'patterns': {
                'total': total_patterns,
                'active': active_patterns,
                'from_user_feedback': user_patterns,
                'top_patterns': [{
                    'id': p.id,
                    'type': p.pattern_type,
                    'effectiveness': p.effectiveness_score,
                    'detections': p.detection_count
                } for p in top_patterns]
            },
            'feedback': {
                'total': total_feedback,
                'processed': processed_feedback,
                'pending': total_feedback - processed_feedback,
                'breakdown': {
                    'false_negatives': false_negatives,
                    'false_positives': false_positives,
                    'correct': correct
                }
            }
        }


def create_feedback_learner():
    """Factory function to create FeedbackLearner with dependencies."""
    from services.gemini_analyzer import GeminiAnalyzer

    gemini = GeminiAnalyzer()
    return FeedbackLearner(gemini)
