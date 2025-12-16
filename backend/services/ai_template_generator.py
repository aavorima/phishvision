import os
import json
import re
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AITemplateGenerator:
    # Brand color database for accurate impersonation (faster than AI lookup)
    BRAND_COLORS = {
        "microsoft": {"primary": "#0078D4", "secondary": "#106EBE", "bg": "#FFFFFF", "text": "#252525", "button_radius": "0px"},
        "office365": {"primary": "#0078D4", "secondary": "#106EBE", "bg": "#FFFFFF", "text": "#252525", "button_radius": "0px"},
        "outlook": {"primary": "#0078D4", "secondary": "#106EBE", "bg": "#FFFFFF", "text": "#252525", "button_radius": "0px"},
        "google": {"primary": "#4285F4", "secondary": "#EA4335", "bg": "#FFFFFF", "text": "#202124", "button_radius": "4px"},
        "gmail": {"primary": "#4285F4", "secondary": "#EA4335", "bg": "#FFFFFF", "text": "#202124", "button_radius": "4px"},
        "apple": {"primary": "#000000", "secondary": "#555555", "bg": "#FFFFFF", "text": "#1D1D1F", "button_radius": "8px"},
        "icloud": {"primary": "#000000", "secondary": "#555555", "bg": "#FFFFFF", "text": "#1D1D1F", "button_radius": "8px"},
        "amazon": {"primary": "#FF9900", "secondary": "#232F3E", "bg": "#FFFFFF", "text": "#0F1111", "button_radius": "8px"},
        "aws": {"primary": "#FF9900", "secondary": "#232F3E", "bg": "#FFFFFF", "text": "#0F1111", "button_radius": "4px"},
        "linkedin": {"primary": "#0A66C2", "secondary": "#004182", "bg": "#F3F2EF", "text": "#000000", "button_radius": "24px"},
        "dropbox": {"primary": "#0061FF", "secondary": "#1E1919", "bg": "#FFFFFF", "text": "#1E1919", "button_radius": "8px"},
        "slack": {"primary": "#4A154B", "secondary": "#36C5F0", "bg": "#FFFFFF", "text": "#1D1C1D", "button_radius": "4px"},
        "zoom": {"primary": "#2D8CFF", "secondary": "#0B5CFF", "bg": "#FFFFFF", "text": "#232333", "button_radius": "8px"},
        "paypal": {"primary": "#003087", "secondary": "#009CDE", "bg": "#FFFFFF", "text": "#2C2E2F", "button_radius": "24px"},
        "docusign": {"primary": "#FFCC00", "secondary": "#1B1B1B", "bg": "#FFFFFF", "text": "#1B1B1B", "button_radius": "4px"},
        "salesforce": {"primary": "#00A1E0", "secondary": "#032D60", "bg": "#FFFFFF", "text": "#080707", "button_radius": "4px"},
        "adobe": {"primary": "#FA0F00", "secondary": "#2C2C2C", "bg": "#FFFFFF", "text": "#2C2C2C", "button_radius": "16px"},
        "netflix": {"primary": "#E50914", "secondary": "#141414", "bg": "#FFFFFF", "text": "#141414", "button_radius": "4px"},
        "spotify": {"primary": "#1DB954", "secondary": "#191414", "bg": "#FFFFFF", "text": "#191414", "button_radius": "24px"},
        "twitter": {"primary": "#1DA1F2", "secondary": "#14171A", "bg": "#FFFFFF", "text": "#14171A", "button_radius": "24px"},
        "facebook": {"primary": "#1877F2", "secondary": "#4267B2", "bg": "#FFFFFF", "text": "#1C1E21", "button_radius": "6px"},
        "instagram": {"primary": "#E4405F", "secondary": "#833AB4", "bg": "#FFFFFF", "text": "#262626", "button_radius": "8px"},
        "github": {"primary": "#24292E", "secondary": "#0366D6", "bg": "#FFFFFF", "text": "#24292E", "button_radius": "6px"},
        "stripe": {"primary": "#635BFF", "secondary": "#0A2540", "bg": "#FFFFFF", "text": "#0A2540", "button_radius": "6px"},
        "shopify": {"primary": "#96BF48", "secondary": "#5C6AC4", "bg": "#FFFFFF", "text": "#212B36", "button_radius": "4px"},
        "bank": {"primary": "#1A365D", "secondary": "#2D3748", "bg": "#FFFFFF", "text": "#1A202C", "button_radius": "4px"},
        "hr": {"primary": "#1E3A5F", "secondary": "#3182CE", "bg": "#F7FAFC", "text": "#2D3748", "button_radius": "6px"},
        "it": {"primary": "#1E3A5F", "secondary": "#3182CE", "bg": "#F7FAFC", "text": "#2D3748", "button_radius": "6px"},
        "internal": {"primary": "#1E3A5F", "secondary": "#2C5282", "bg": "#F7FAFC", "text": "#2D3748", "button_radius": "6px"},
        "default": {"primary": "#1E3A5F", "secondary": "#4A5568", "bg": "#FFFFFF", "text": "#2D3748", "button_radius": "6px"},
    }

    def __init__(self, api_key=None):
        # Use provided API key first, then fall back to .env
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)

                # List available models to find the right one
                print("[DEBUG] Listing available Gemini models...")
                try:
                    available_models = genai.list_models()
                    model_names = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
                    print(f"[DEBUG] Available models: {model_names}")

                    if model_names:
                        # Use the first available model that supports generateContent
                        model_name = model_names[0].replace('models/', '')
                        self.model = genai.GenerativeModel(model_name)
                        self.enabled = True
                        print(f"[INFO] AI Template Generator initialized with {model_name}")
                    else:
                        self.enabled = False
                        self.model = None
                        print("[WARNING] No models supporting generateContent found.")
                except Exception as e:
                    print(f"[WARNING] Could not list models: {e}")
                    # Fallback: try the most common working model names
                    fallback_models = ['gemini-2.5-flash', 'gemini-2.5-pro', 'gemini-2.0-flash']
                    self.model = None
                    for model_name in fallback_models:
                        try:
                            self.model = genai.GenerativeModel(model_name)
                            self.enabled = True
                            print(f"[INFO] AI Template Generator initialized with {model_name}")
                            break
                        except:
                            continue

                    if not self.model:
                        self.enabled = False
                        print("[WARNING] No compatible Gemini model found.")
            except Exception as e:
                self.enabled = False
                self.model = None
                print(f"[ERROR] Failed to initialize Gemini API: {e}")
        else:
            self.enabled = False
            self.model = None
            print("[WARNING] GEMINI_API_KEY not found. AI template generation disabled.")

    def _detect_brand(self, user_request: str) -> tuple:
        """
        Detect brand from user request and return brand name + colors.
        Fast lookup - no AI needed.
        """
        request_lower = user_request.lower()

        # Check for known brands in request
        for brand_key in self.BRAND_COLORS.keys():
            if brand_key in request_lower:
                return brand_key, self.BRAND_COLORS[brand_key]

        # Check for common variations
        brand_aliases = {
            "o365": "microsoft", "office 365": "microsoft", "ms ": "microsoft", "azure": "microsoft",
            "gsuite": "google", "g suite": "google", "workspace": "google",
            "itunes": "apple", "app store": "apple", "macbook": "apple",
            "prime": "amazon", "kindle": "amazon",
            "human resources": "hr", "policy": "hr", "benefits": "hr",
            "helpdesk": "it", "help desk": "it", "password": "it", "vpn": "it", "security": "it",
            "wire transfer": "bank", "payment": "bank", "invoice": "bank", "account": "bank",
        }

        for alias, brand in brand_aliases.items():
            if alias in request_lower:
                return brand, self.BRAND_COLORS[brand]

        # Default to internal/corporate style
        return "internal", self.BRAND_COLORS["default"]

    def _get_current_events_context(self) -> str:
        now = datetime.now()
        month = now.month
        weekday = now.strftime('%A')

        events_calendar = {
            1: ["New Year period", "Q4 earnings reports", "Tax season preparation"],
            2: ["Valentine's Day promotions", "Presidents' Day"],
            3: ["End of Q1", "Daylight saving begins"],
            4: ["Tax deadline (US)", "Easter", "Q1 closeout"],
            5: ["Mother's Day", "Memorial Day"],
            6: ["Father's Day", "Mid-year reviews"],
            7: ["Independence Day (US)", "Q2 close"],
            8: ["Back-to-school season"],
            9: ["Labor Day", "Q3 planning"],
            10: ["Cybersecurity Awareness Month", "Open enrollment", "Halloween"],
            11: ["Thanksgiving", "Black Friday/Cyber Monday", "Year-end planning"],
            12: ["Holiday season", "Year-end reviews", "W-2/1099 preparation"]
        }

        context = [
            f"Current date: {now.strftime('%B %d, %Y')}",
            f"Day: {weekday}",
            f"Relevant events: {', '.join(events_calendar.get(month, ['Standard business month']))}"
        ]
        if weekday == "Friday":
            context.append("Weekend approaching - natural urgency trigger")
        if now.day > 25:
            context.append("End-of-month deadlines approaching")

        return " | ".join(context)

    def generate_template(self, description, category='IT', difficulty='medium', company_name=''):
        """
        Generate realistic phishing simulation template for security awareness training.

        ETHICAL USE ONLY: For authorized training programs to teach employees
        how to recognize and report phishing attempts.
        """
        if not self.enabled:
            return self._get_advanced_fallback_template(description, category, company_name, difficulty)

        try:
            current_context = self._get_current_events_context()

            # Detect brand from user request (fast lookup, no AI needed)
            detected_brand, brand_colors = self._detect_brand(description)

            difficulty_guidelines = {
                'easy': """
                EASY - Beginner Training:
                - Include obvious red flags: spelling errors, generic greetings ("Dear Customer")
                - Suspicious sender address visible
                - Overly urgent/threatening language
                - Educational: Teaches basic phishing recognition
                """,
                'medium': """
                MEDIUM - Intermediate Training:
                - Professional appearance with subtle flaws
                - Realistic but slightly off branding
                - Moderate urgency, plausible scenario
                - Educational: Teaches attention to detail
                """,
                'hard': """
                HARD - Advanced Training:
                - Near-perfect brand mimicry
                - Contextually relevant (current events, business cycles)
                - Sophisticated social engineering
                - Educational: Teaches advanced threat recognition
                """
            }

            prompt = f"""You are a professional cybersecurity awareness specialist creating highly realistic phishing simulation email templates for AUTHORIZED employee training programs only.

**USER REQUEST**: {description}

**DETECTED BRAND**: {detected_brand.upper()}
**EXACT BRAND COLORS TO USE** (DO NOT CHANGE THESE):
- Primary: {brand_colors['primary']}
- Secondary: {brand_colors['secondary']}
- Background: {brand_colors['bg']}
- Text: {brand_colors['text']}
- Button Border Radius: {brand_colors['button_radius']}

**TEMPLATE PARAMETERS**:
- Difficulty: {difficulty}
- Category: {category}
- Organization Context: {company_name or detected_brand.title()}
- Current Context: {current_context}

**DIFFICULTY LEVEL**:
{difficulty_guidelines.get(difficulty, difficulty_guidelines['medium'])}

**CRITICAL DESIGN RULES** (MUST FOLLOW):
1. Use EXACTLY the brand colors specified above - no random colors
2. Match the real {detected_brand.title()} email style as closely as possible
3. Use table-based layout for Outlook compatibility
4. Button must use primary color ({brand_colors['primary']}) with border-radius: {brand_colors['button_radius']}
5. Header should be clean, matching real {detected_brand.title()} emails
6. Footer should mimic real corporate footers (legal text, unsubscribe, address)
7. Logo placeholder: https://via.placeholder.com/180x50/{brand_colors['primary'].replace('#', '')}/FFFFFF?text={detected_brand.title()}

**REQUIRED TEMPLATE VARIABLES** (use double braces):
{{{{full_name}}}}, {{{{first_name}}}}, {{{{last_name}}}}, {{{{email}}}}, {{{{company}}}}, {{{{department}}}}, {{{{tracking_link}}}}, {{{{current_date}}}}, {{{{current_time}}}}

**HTML REQUIREMENTS**:
- Complete HTML5 with <!DOCTYPE html>
- ALL CSS inline (no <style> blocks)
- Table-based layout for email client compatibility
- Mobile responsive (max-width: 600px)
- Web-safe fonts: Arial, Helvetica, sans-serif
- Professional spacing and alignment

**OUTPUT FORMAT** (STRICT JSON ONLY - no markdown, no extra text):
{{
  "name": "Short descriptive name (max 60 chars)",
  "subject": "Realistic subject line with {{{{first_name}}}} if appropriate",
  "html_content": "Complete HTML email matching {detected_brand.title()} brand exactly",
  "metadata": {{
    "difficulty": "{difficulty}",
    "impersonated_brand": "{detected_brand}",
    "brand_colors": {{"primary": "{brand_colors['primary']}", "secondary": "{brand_colors['secondary']}", "bg": "{brand_colors['bg']}"}},
    "scenario_type": "password_reset | document_share | policy_update | payment | account_verify | security_alert",
    "primary_trigger": "urgency | authority | fear | curiosity | compliance",
    "red_flags": [
      "Specific indicator 1 employees should notice",
      "Specific indicator 2",
      "Specific indicator 3",
      "Specific indicator 4"
    ],
    "training_notes": "Why this simulation is effective and what it teaches",
    "detection_tips": [
      "How to verify this is fake",
      "What to check before clicking"
    ]
  }}
}}

CRITICAL: Create a template that looks EXACTLY like a real {detected_brand.title()} email. Use the EXACT colors provided. This is for authorized security training only."""

            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Clean JSON
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'\s*```', '', text)
            text = text.strip()
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                text = json_match.group(0)

            template_data = json.loads(text)

            required = ['name', 'subject', 'html_content']
            if not all(k in template_data for k in required):
                raise ValueError("Missing required fields")

            template_data.setdefault('metadata', {})
            template_data['generated_at'] = datetime.now().isoformat()

            print(f"[SUCCESS] Generated {difficulty.upper()} {detected_brand.upper()} template: {template_data['name']}")
            return template_data

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"[WARNING] Gemini API quota exceeded. Using fallback template. Quota resets in 24 hours.")
            else:
                print(f"[ERROR] AI generation failed: {e}")
            return self._get_advanced_fallback_template(description, category, company_name, difficulty)

    def _get_advanced_fallback_template(self, description, category, company_name, difficulty='medium'):
        """
        Advanced fallback templates with realistic corporate styling and educational metadata
        """
        company = company_name or "Your Organization"
        now = datetime.now()

        # Template library by difficulty
        templates = {
            'easy': self._get_easy_template(description, category, company, now),
            'medium': self._get_medium_template(description, category, company, now),
            'hard': self._get_hard_template(description, category, company, now),
            'expert': self._get_expert_template(description, category, company, now)
        }

        return templates.get(difficulty, templates['medium'])

    def _get_easy_template(self, description, category, company, now):
        return {
            'name': f"{category} Alert - {description.title()} [EASY]",
            'subject': f"URGENT!!! {{{{first_name}}}} ACTION NEEDED!!!",
            'html_content': f"""<!DOCTYPE html>
<html><body style="font-family:Arial;background:#fff;padding:20px;">
<div style="max-width:600px;margin:0 auto;">
  <h1 style="color:red;">⚠️ URGENT SECURITY ALERT!!!</h1>
  <p>Dear {{{{full_name}}}},</p>
  <p>Your account has been SUSPENDED due to suspicious activity!</p>
  <p>Click here IMMEDIATELY to verify: <a href="{{{{tracking_link}}}}" style="color:blue;">CLICK HERE NOW</a></p>
  <p><b>WARNING:</b> Failure to respond within 24 HOURS will result in PERMANENT account deletion!</p>
  <p>Sincerely,<br>{company} Security Team</p>
</div></body></html>""",
            'metadata': {
                'difficulty': 'easy',
                'primary_trigger': 'Fear + Urgency',
                'red_flags': [
                    'Excessive use of ALL CAPS and exclamation marks',
                    'Generic "suspicious activity" claim with no specifics',
                    'Threatens permanent deletion to create panic',
                    'Poor professional formatting',
                    'No official branding or signatures'
                ],
                'training_notes': 'Teaches employees to recognize obvious phishing indicators: aggressive language, threats, and unprofessional formatting',
                'detection_tips': [
                    'Legitimate companies never use excessive caps/exclamation marks',
                    'Real security alerts provide specific details',
                    'Verify by contacting company directly, never click links in suspicious emails'
                ]
            }
        }

    def _get_medium_template(self, description, category, company, now):
        return {
            'name': f"{category} Security Notice - {description.title()} [MEDIUM]",
            'subject': f"Action Required: {{{{first_name}}}}, {description}",
            'html_content': f"""<!DOCTYPE html>
<html><body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:20px;">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
  <div style="background:linear-gradient(135deg,#1e3a8a 0%,#3b82f6 100%);color:#fff;padding:30px;text-align:center;">
    <h1 style="margin:0;font-size:22px;">{company}</h1>
    <p style="margin:5px 0 0;font-size:13px;opacity:0.9;">{category} Department</p>
  </div>
  <div style="padding:35px 30px;">
    <p style="font-size:14px;color:#374151;line-height:1.6;">Dear {{{{full_name}}}},</p>
    <p style="font-size:14px;color:#374151;line-height:1.6;">Our automated systems have detected an issue: <strong>{description}</strong>.</p>
    <p style="font-size:14px;color:#374151;line-height:1.6;">To maintain uninterrupted access to your account, please verify your credentials.</p>
    <div style="text-align:center;margin:30px 0;">
      <a href="{{{{tracking_link}}}}" style="background:#3b82f6;color:#fff;padding:14px 35px;text-decoration:none;border-radius:6px;font-weight:600;display:inline-block;">Verify Account</a>
    </div>
    <div style="background:#fef3c7;border-left:4px solid#f59e0b;padding:15px;margin:25px 0;">
      <p style="margin:0;color:#92400e;font-size:13px;"><strong>⚠️ Important:</strong> Please complete verification by {{{{current_date}}}} to avoid account restrictions.</p>
    </div>
    <p style="font-size:13px;color:#6b7280;margin-top:25px;">If you did not request this, please contact our support team.</p>
  </div>
  <div style="background:#f9fafb;padding:20px;text-align:center;border-top:1px solid #e5e7eb;font-size:11px;color:#9ca3af;">
    <p style="margin:0;">© {now.year} {company}. All rights reserved.<br>This is an automated notification. Please do not reply.</p>
  </div>
</div></body></html>""",
            'metadata': {
                'difficulty': 'medium',
                'primary_trigger': 'Urgency + Authority',
                'red_flags': [
                    'Generic "issue detected" without specific details',
                    'Requests credential verification via email link',
                    'Creates artificial urgency with arbitrary deadline',
                    'Vague "automated systems" claim',
                    'No incident number or reference ID'
                ],
                'training_notes': 'Teaches employees to question generic security notifications and verify through official channels',
                'detection_tips': [
                    'Legitimate IT never asks for credential verification via email',
                    'Hover over links to check actual destination before clicking',
                    'Contact IT department directly using known contact info',
                    'Check for official incident ticket numbers'
                ]
            }
        }

    def _get_hard_template(self, description, category, company, now):
        incident_id = f"SEC-{now.year}-{now.strftime('%m%d%H%M')}"
        return {
            'name': f"{category} Critical Alert - {description.title()} [HARD]",
            'subject': f"[{incident_id}] Security Review Required - {{{{first_name}}}} {{{{last_name}}}}",
            'html_content': f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f3f4f6;margin:0;padding:0;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f3f4f6;padding:20px;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.08);">
      <tr><td style="background:linear-gradient(135deg,#0f172a 0%,#1e40af 100%);padding:25px 35px;text-align:center;">
        <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600;letter-spacing:-0.5px;">{company}</h1>
        <p style="margin:8px 0 0;color:#93c5fd;font-size:12px;text-transform:uppercase;letter-spacing:1px;">{category} Security Operations</p>
      </td></tr>
      <tr><td style="background:#dbeafe;border-left:4px solid #3b82f6;padding:15px 35px;">
        <p style="margin:0;color:#1e40af;font-size:13px;"><strong>🔒 Incident ID:</strong> {incident_id}</p>
        <p style="margin:4px 0 0;color:#1e3a8a;font-size:12px;">Priority: <span style="color:#dc2626;font-weight:600;">HIGH</span> | Detected: {{{{current_time}}}} UTC</p>
      </td></tr>
      <tr><td style="padding:35px;">
        <p style="margin:0 0 16px;color:#111827;font-size:14px;line-height:1.6;">Dear {{{{full_name}}}},</p>
        <p style="margin:0 0 16px;color:#374151;font-size:14px;line-height:1.6;">Our Security Information and Event Management (SIEM) system flagged your account for mandatory security review: <strong>{description}</strong>.</p>
        <p style="margin:0 0 16px;color:#374151;font-size:14px;line-height:1.6;">As part of our {now.strftime('%B')} security compliance audit, all {{{{department}}}} employees must complete two-factor authentication verification.</p>
        <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;padding:20px;margin:25px 0;">
          <p style="margin:0 0 12px;color:#111827;font-size:13px;font-weight:600;">📋 Required Actions:</p>
          <ol style="margin:0;padding-left:20px;color:#4b5563;font-size:13px;line-height:1.8;">
            <li>Verify your identity using the secure portal below</li>
            <li>Review recent account activity</li>
            <li>Update security preferences if needed</li>
          </ol>
        </div>
        <div style="text-align:center;margin:30px 0;">
          <a href="{{{{tracking_link}}}}" style="background:#3b82f6;color:#fff;padding:14px 40px;text-decoration:none;border-radius:6px;font-weight:600;font-size:14px;display:inline-block;box-shadow:0 4px 10px rgba(59,130,246,0.3);">Begin Security Review</a>
        </div>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#fef2f2;border:1px solid #fecaca;border-radius:6px;margin:25px 0;">
          <tr><td style="padding:16px;">
            <p style="margin:0;color:#991b1b;font-size:12px;"><strong>⏰ Deadline:</strong> {now.strftime('%B %d, %Y at 11:59 PM')} ({(now.day + 2) % 30 if now.day > 25 else now.day + 2} days remaining)</p>
            <p style="margin:8px 0 0;color:#7f1d1d;font-size:11px;">Non-compliance may result in temporary account restrictions per policy SEC-{now.year}-02.</p>
          </td></tr>
        </table>
        <p style="margin:25px 0 0;color:#6b7280;font-size:12px;line-height:1.6;">For assistance, contact the IT Service Desk at ext. 4500 or email support@{company.lower().replace(' ','')}.com</p>
      </td></tr>
      <tr><td style="background:#f9fafb;padding:25px 35px;border-top:1px solid #e5e7eb;">
        <p style="margin:0 0 10px;color:#111827;font-size:11px;font-weight:600;">{company} Information Security</p>
        <p style="margin:0 0 15px;color:#6b7280;font-size:10px;line-height:1.5;">This message was sent to {{{{email}}}} as part of your employment security requirements. Incident reference: {incident_id}</p>
        <p style="margin:0;color:#9ca3af;font-size:9px;text-align:center;">© {now.year} {company}. All rights reserved. | <a href="#" style="color:#3b82f6;text-decoration:none;">Privacy Policy</a> | <a href="#" style="color:#3b82f6;text-decoration:none;">Security Guidelines</a></p>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{{{{tracking_pixel}}}}" width="1" height="1" alt="" style="display:block;">
</body></html>""",
            'metadata': {
                'difficulty': 'hard',
                'primary_trigger': 'Authority + Compliance + Urgency',
                'red_flags': [
                    'Pressures action with compliance/policy references',
                    'Uses realistic incident ID format but unverifiable',
                    'Mentions specific departments/systems (SIEM) for credibility',
                    'Creates urgency with countdown and policy citations',
                    'Professional design masks suspicious request',
                    'Links to "secure portal" instead of known company URL'
                ],
                'training_notes': 'Advanced template teaching recognition of sophisticated social engineering: authority exploitation, compliance pressure, and professional presentation',
                'detection_tips': [
                    'Verify incident IDs through official IT portal or phone',
                    'Check if mentioned policies actually exist',
                    'Legitimate compliance requests come through known channels',
                    'Hover links to verify they point to actual company domains',
                    'Contact IT Service Desk using known number, not email links'
                ]
            }
        }

    def _get_expert_template(self, description, category, company, now):
        ticket_id = f"INC{now.year}{now.strftime('%m%d')}{now.hour:02d}{now.minute:02d}"
        return {
            'name': f"{category} Executive Notice - {description.title()} [EXPERT]",
            'subject': f"[TICKET:{ticket_id}] Mandatory Compliance Action - {{{{department}}}} Division",
            'html_content': f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Security Compliance Notice</title></head>
<body style="font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;background:#f8fafc;margin:0;padding:0;-webkit-font-smoothing:antialiased;">
<!--[if mso]><table width="100%" cellpadding="0" cellspacing="0"><tr><td><![endif]-->
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;padding:30px 0;">
  <tr><td align="center">
    <table width="650" cellpadding="0" cellspacing="0" style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;">
      <tr><td style="background:linear-gradient(to right,#0f172a,#1e3a8a,#1e40af);padding:2px 40px 18px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td width="70%">
              <h1 style="margin:15px 0 5px;color:#fff;font-size:18px;font-weight:600;">{company}</h1>
              <p style="margin:0;color:#cbd5e1;font-size:11px;text-transform:uppercase;letter-spacing:0.5px;">{category} & Compliance Division</p>
            </td>
            <td width="30%" align="right">
              <img src="https://via.placeholder.com/120x40/1e40af/ffffff?text={company[:3].upper()}" alt="Logo" style="height:40px;"/>
            </td>
          </tr>
        </table>
      </td></tr>
      <tr><td style="background:linear-gradient(to right,#eff6ff,#dbeafe);border-bottom:3px solid #3b82f6;padding:14px 40px;">
        <table width="100%"><tr>
          <td width="70%">
            <p style="margin:0;color:#1e40af;font-size:11px;font-weight:600;">Incident Tracking Number</p>
            <p style="margin:3px 0 0;color:#1e3a8a;font-size:13px;font-weight:700;">{ticket_id}</p>
          </td>
          <td width="30%" align="right">
            <span style="background:#dc2626;color:#fff;padding:4px 10px;border-radius:4px;font-size:10px;font-weight:700;text-transform:uppercase;">Action Required</span>
          </td>
        </tr></table>
      </td></tr>
      <tr><td style="padding:35px 40px;">
        <p style="margin:0 0 18px;color:#0f172a;font-size:14px;line-height:1.6;">Dear {{{{full_name}}}} ({{{{job_title}}}}),</p>
        <p style="margin:0 0 18px;color:#334155;font-size:14px;line-height:1.7;">This notice concerns: <strong style="color:#1e40af;">{description}</strong>, flagged during our quarterly SOC 2 Type II compliance audit cycle.</p>
        <p style="margin:0 0 18px;color:#334155;font-size:14px;line-height:1.7;">Per Executive Order {now.year}-{now.month:02d} and in accordance with our Information Security Management System (ISMS) framework, all {{{{department}}}} personnel must complete mandatory identity verification before {now.strftime('%B')} {(now.day + 3) % 30 if now.day > 27 else now.day + 3}.</p>

        <div style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:6px;padding:22px;margin:28px 0;">
          <p style="margin:0 0 14px;color:#0f172a;font-size:13px;font-weight:700;">📊 Compliance Requirements:</p>
          <table width="100%" cellpadding="8" cellspacing="0" style="font-size:12px;">
            <tr style="background:#f1f5f9;">
              <td style="color:#475569;padding:10px;">Multi-Factor Authentication Setup</td>
              <td align="right" style="color:#dc2626;font-weight:600;padding:10px;">Pending</td>
            </tr>
            <tr>
              <td style="color:#475569;padding:10px;">Security Awareness Certification</td>
              <td align="right" style="color:#16a34a;font-weight:600;padding:10px;">Completed</td>
            </tr>
            <tr style="background:#f1f5f9;">
              <td style="color:#475569;padding:10px;">Access Control Review</td>
              <td align="right" style="color:#dc2626;font-weight:600;padding:10px;">Required</td>
            </tr>
          </table>
        </div>

        <p style="margin:0 0 18px;color:#334155;font-size:14px;line-height:1.7;">Click below to access the secure compliance portal (SSO-enabled):</p>

        <div style="text-align:center;margin:32px 0;">
          <a href="{{{{tracking_link}}}}" style="background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:#fff;padding:15px 42px;text-decoration:none;border-radius:6px;font-weight:600;font-size:14px;display:inline-block;box-shadow:0 6px 20px rgba(37,99,235,0.35);border:1px solid #1d4ed8;">Access Compliance Portal →</a>
        </div>

        <table width="100%" cellpadding="0" cellspacing="0" style="background:linear-gradient(to bottom,#fef2f2,#fee2e2);border:1px solid #fca5a5;border-radius:6px;margin:28px 0;">
          <tr><td style="padding:18px 20px;">
            <p style="margin:0 0 8px;color:#991b1b;font-size:12px;font-weight:700;">⏰ Compliance Deadline</p>
            <p style="margin:0 0 10px;color:#7f1d1d;font-size:13px;line-height:1.5;">{now.strftime('%A, %B %d, %Y at 5:00 PM')} ({(now.day + 3) % 30 if now.day > 27 else now.day + 3} business days remaining)</p>
            <p style="margin:0;color:#7f1d1d;font-size:11px;line-height:1.5;"><strong>Non-Compliance Impact:</strong> Access to internal systems, email, and VPN may be temporarily restricted per corporate policy SEC-GOV-{now.year}-003 until verification is complete.</p>
          </td></tr>
        </table>

        <div style="background:#f8fafc;border-left:4px solid #3b82f6;padding:16px 20px;margin:25px 0;">
          <p style="margin:0 0 10px;color:#0f172a;font-size:12px;font-weight:600;">📌 Important Notes:</p>
          <ul style="margin:0;padding-left:18px;color:#475569;font-size:11px;line-height:1.8;">
            <li>This is a system-generated notification tied to your employee ID: EMP{{{{employee_id}}}}</li>
            <li>Your manager ({{{{manager_name}}}}) has been CC'd on this compliance requirement</li>
            <li>Questions? Contact InfoSec via ServiceNow ticket or ext. 5200</li>
          </ul>
        </div>

        <p style="margin:25px 0 0;color:#64748b;font-size:11px;line-height:1.6;padding-top:20px;border-top:1px solid #e2e8f0;">This notification was automatically generated by {company} Identity & Access Management (IAM) platform. For security purposes, this email cannot accept replies. Contact your IT Service Desk for assistance.</p>
      </td></tr>
      <tr><td style="background:#f1f5f9;padding:28px 40px;border-top:1px solid #cbd5e1;">
        <table width="100%"><tr>
          <td width="70%">
            <p style="margin:0 0 6px;color:#0f172a;font-size:11px;font-weight:700;">{company} Information Security & Compliance</p>
            <p style="margin:0 0 4px;color:#64748b;font-size:10px;">1234 Enterprise Blvd, Suite 500 | Corporate HQ</p>
            <p style="margin:0;color:#64748b;font-size:10px;">Phone: +1 (555) 123-4500 | Fax: +1 (555) 123-4501</p>
          </td>
          <td width="30%" align="right" valign="top">
            <p style="margin:0;color:#94a3b8;font-size:9px;">Ticket: {ticket_id}</p>
            <p style="margin:4px 0 0;color:#94a3b8;font-size:9px;">Sent: {{{{current_date}}}}</p>
          </td>
        </tr></table>
        <hr style="border:none;border-top:1px solid #cbd5e1;margin:18px 0;"/>
        <p style="margin:0;color:#94a3b8;font-size:9px;line-height:1.6;text-align:center;">© {now.year} {company}. All rights reserved. Confidential and proprietary information.<br/>
        Sent to {{{{email}}}} | Employee ID: EMP{{{{employee_id}}}} | Department: {{{{department}}}}<br/>
        <a href="#" style="color:#64748b;text-decoration:none;">Privacy Policy</a> | <a href="#" style="color:#64748b;text-decoration:none;">Security Center</a> | <a href="#" style="color:#64748b;text-decoration:none;">Unsubscribe from non-critical notifications</a></p>
      </td></tr>
    </table>
  </td></tr>
</table>
<img src="{{{{tracking_pixel}}}}" width="1" height="1" alt="" style="display:block;margin:20px auto 0;"/>
<!--[if mso]></td></tr></table><![endif]-->
</body></html>""",
            'metadata': {
                'difficulty': 'expert',
                'primary_trigger': 'Authority + Compliance + Social Proof + Urgency',
                'red_flags': [
                    'Sophisticated but unverifiable ticket/incident numbers',
                    'References specific policies and executive orders (fictional)',
                    'Mentions manager and employee ID to create urgency',
                    'Uses compliance jargon (SOC 2, ISMS) for credibility',
                    'Professional design with gradient headers and tables',
                    'Creates fear of access restriction without verification',
                    'SSO claim but link goes to external tracking URL'
                ],
                'training_notes': 'Expert-level template demonstrating APT-style social engineering: perfect corporate mimicry, authority exploitation through policy references, and multi-layered psychological manipulation. Teaches employees to verify even the most professional-looking emails.',
                'detection_tips': [
                    'Verify ticket numbers through official ServiceNow/ITSM portal',
                    'Check if referenced policies (SEC-GOV-{now.year}-003) actually exist in company intranet',
                    'Contact manager directly to verify "CC" claim',
                    'Legitimate SSO portals use company domain, not tracking links',
                    'Call IT Service Desk using known number to verify any compliance requirements',
                    'Check email headers for actual sender domain (not just display name)',
                    'Beware of emails that reference specific employee data - could indicate prior breach'
                ]
            }
        }

    def improve_template(self, current_subject, current_html, improvement_notes, increase_difficulty=False):
        if not self.enabled:
            return {'subject': current_subject, 'html_content': current_html, 'changes_made': []}

        try:
            prompt = f"""Improve the following phishing simulation template for authorized security training.

Current Subject: {current_subject}
Current HTML: {current_html}

Improvement Request: {improvement_notes}
{"Increase overall sophistication and difficulty level." if increase_difficulty else ""}

Preserve all template variables exactly: {{{{first_name}}}}, {{{{tracking_link}}}}, etc.
Maintain full HTML compatibility and inline CSS.

Return only valid JSON:
{{
  "subject": "improved subject",
  "html_content": "full improved HTML",
  "changes_made": ["bullet list of improvements applied"]
}}
"""

            response = self.model.generate_content(prompt)
            text = re.sub(r'```json\s*', '', response.text.strip())
            text = re.sub(r'\s*```', '', text)
            text = re.search(r'\{.*\}', text, re.DOTALL).group(0)

            result = json.loads(text)
            print("[SUCCESS] Template improved")
            return result

        except Exception as e:
            print(f"[ERROR] Improvement failed: {e}")
            return {'subject': current_subject, 'html_content': current_html, 'changes_made': []}


# Example usage
if __name__ == "__main__":
    generator = AITemplateGenerator()

    template = generator.generate_template(
        description="Urgent VPN certificate renewal required before access is revoked",
        category="IT",
        difficulty="expert",
        company_name="Acme Global Technologies"
    )

    print("\n=== GENERATED TEMPLATE ===")
    print("Name:", template['name'])
    print("Subject:", template['subject'])
    print("Difficulty:", template['metadata'].get('difficulty'))
    print("Red Flags:", " | ".join(template['metadata'].get('red_flags', [])))
