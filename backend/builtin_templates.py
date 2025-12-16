"""
Professional Built-in Phishing Templates for PhishVision
These templates are designed to closely mimic real corporate emails for security training purposes.
"""

BUILTIN_TEMPLATES = [
    # ============ MICROSOFT 365 ============
    {
        "name": "Microsoft 365 - Password Expiration",
        "category": "IT",
        "subject": "Action Required: Your password will expire in 24 hours",
        "html_content": """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<title>Microsoft Account</title>
</head>
<body style="margin:0;padding:0;word-spacing:normal;background-color:#f2f2f2;">
<div role="article" aria-roledescription="email" style="text-size-adjust:100%;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;background-color:#f2f2f2;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 0;">
<table role="presentation" style="width:94%;max-width:600px;border:none;border-spacing:0;text-align:left;font-family:'Segoe UI',Tahoma,Verdana,Arial,sans-serif;font-size:15px;line-height:22px;color:#363636;">
<tr><td style="padding:30px 40px;background-color:#ffffff;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td style="padding-bottom:25px;">
<svg xmlns="http://www.w3.org/2000/svg" width="108" height="24" viewBox="0 0 108 24"><path fill="#f25022" d="M0 0h11v11H0z"/><path fill="#00a4ef" d="M0 12h11v11H0z"/><path fill="#7fba00" d="M12 0h11v11H12z"/><path fill="#ffb900" d="M12 12h11v11H12z"/><path fill="#737373" d="M27 6h2.9v12H27zm13.6 0l-4.8 12h-2.6l4.8-12zm-4.6 12l-4.9-12h2.8l3.6 9.2 3.5-9.2h2.7l-4.9 12zM49 6h2.9v12H49zm7.5 3.5c.8-.8 1.9-1.3 3.1-1.3 2.5 0 4.1 1.8 4.1 4.4v5.5h-2.8v-5.2c0-1.4-.7-2.3-2-2.3-1.4 0-2.4 1-2.4 2.5v5h-2.8V8.3h2.8zm14.3 8.8c-3.3 0-5.6-2.4-5.6-6.2 0-3.7 2.4-6.1 5.7-6.1 3.4 0 5.7 2.4 5.7 6.1 0 3.8-2.4 6.2-5.8 6.2zm0-2.4c1.8 0 2.8-1.4 2.8-3.8s-1-3.7-2.8-3.7c-1.7 0-2.7 1.4-2.7 3.7 0 2.4 1 3.8 2.7 3.8zm11.9 2.4c-2 0-3.5-1-4.1-2.6l2.4-1c.3.9 1 1.4 1.9 1.4.8 0 1.4-.4 1.4-1 0-.7-.6-1-1.7-1.4l-.7-.3c-1.8-.7-3-1.6-3-3.4 0-2 1.7-3.5 4-3.5 1.7 0 3 .7 3.7 2.1l-2.2 1c-.4-.7-.9-1.1-1.6-1.1-.7 0-1.2.4-1.2.9 0 .6.4.9 1.4 1.3l.7.3c2.1.8 3.4 1.7 3.4 3.6-.1 2.2-1.9 3.7-4.4 3.7zm10.7 0c-3.3 0-5.6-2.4-5.6-6.2 0-3.7 2.4-6.1 5.7-6.1 3.4 0 5.7 2.4 5.7 6.1 0 3.8-2.4 6.2-5.8 6.2zm0-2.4c1.8 0 2.8-1.4 2.8-3.8s-1-3.7-2.8-3.7c-1.7 0-2.7 1.4-2.7 3.7 0 2.4 1 3.8 2.7 3.8zm9.4 2.1V11h-1.7V8.7h1.7V6h2.8v2.7h2.1V11h-2.1v4.8c0 .8.4 1.2 1.2 1.2h1v2.4h-1.5c-2.2-.1-3.5-1.2-3.5-3.3z"/></svg>
</td></tr>
<tr><td style="padding-bottom:20px;">
<h1 style="margin:0;font-size:21px;font-weight:600;color:#1b1b1b;">Your password is about to expire</h1>
</td></tr>
<tr><td style="padding-bottom:15px;">
<p style="margin:0;color:#363636;">Hi {{first_name}},</p>
</td></tr>
<tr><td style="padding-bottom:20px;">
<p style="margin:0;color:#363636;">Your Microsoft 365 password will expire in <strong>24 hours</strong>. After your password expires, you won't be able to sign in to your account or access your email, files, and other Microsoft services.</p>
</td></tr>
<tr><td style="padding-bottom:20px;">
<p style="margin:0;color:#363636;">To avoid any interruption, please update your password now.</p>
</td></tr>
<tr><td style="background-color:#f5f5f5;border-radius:4px;padding:20px;margin-bottom:20px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td style="color:#5e5e5e;font-size:13px;padding-bottom:8px;">Account</td></tr>
<tr><td style="color:#1b1b1b;font-weight:600;padding-bottom:12px;">{{email}}</td></tr>
<tr><td style="color:#5e5e5e;font-size:13px;padding-bottom:8px;">Password expires</td></tr>
<tr><td style="color:#c50f1f;font-weight:600;">{{date}} at 11:59 PM UTC</td></tr>
</table>
</td></tr>
<tr><td style="padding:25px 0;">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0067b8;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:12px 24px;border-radius:2px;">Update password</a>
</td></tr>
<tr><td style="padding-top:20px;border-top:1px solid #e5e5e5;">
<p style="margin:0;font-size:12px;color:#5e5e5e;">If you didn't request this email, someone may be trying to access your account. Visit the <a href="#" style="color:#0067b8;text-decoration:none;">Microsoft Account Security</a> page to review your recent activity.</p>
</td></tr>
</table>
</td></tr>
<tr><td style="padding:30px 40px;background-color:#f5f5f5;">
<p style="margin:0;font-size:11px;color:#5e5e5e;text-align:center;">This is a mandatory service communication from Microsoft. To set your contact preferences for other communications, visit the <a href="#" style="color:#5e5e5e;">Promotional Communications Manager</a>.</p>
<p style="margin:15px 0 0;font-size:11px;color:#5e5e5e;text-align:center;">Microsoft Corporation, One Microsoft Way, Redmond, WA 98052 USA</p>
</td></tr>
</table>
</td></tr>
</table>
</div>
</body>
</html>""",
        "difficulty": "medium",
        "description": "Authentic Microsoft 365 password expiration notice with Microsoft branding",
        "language": "EN",
        "is_builtin": True
    },
    # ============ GOOGLE WORKSPACE ============
    {
        "name": "Google - Critical Security Alert",
        "category": "IT",
        "subject": "Critical security alert for your Google Account",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#ffffff;font-family:Google Sans,Roboto,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#ffffff;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:500px;border:none;border-spacing:0;">
<tr><td style="padding-bottom:24px;">
<img src="https://www.gstatic.com/images/branding/googlelogo/2x/googlelogo_color_74x24dp.png" alt="Google" style="height:24px;width:auto;">
</td></tr>
<tr><td style="padding-bottom:24px;">
<h1 style="margin:0;font-size:24px;font-weight:400;color:#202124;line-height:32px;">Someone has your password</h1>
</td></tr>
<tr><td style="padding-bottom:24px;">
<p style="margin:0;font-size:14px;color:#5f6368;line-height:20px;">Hi {{first_name}},</p>
</td></tr>
<tr><td style="padding-bottom:24px;">
<p style="margin:0;font-size:14px;color:#5f6368;line-height:20px;">Google detected that someone has your password for <strong style="color:#202124;">{{email}}</strong>. Your password was likely exposed in a third-party data breach.</p>
</td></tr>
<tr><td style="background-color:#fce8e6;border-radius:8px;padding:16px;margin-bottom:24px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td style="width:24px;vertical-align:top;padding-right:12px;">
<svg width="24" height="24" viewBox="0 0 24 24" fill="#c5221f"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
</td><td style="font-size:14px;color:#c5221f;line-height:20px;">
<strong>Change your password immediately</strong><br>
Someone may be able to access your account.
</td></tr>
</table>
</td></tr>
<tr><td style="padding:24px 0;">
<p style="margin:0 0 16px;font-size:14px;color:#5f6368;line-height:20px;"><strong style="color:#202124;">Sign-in attempt details:</strong></p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;color:#5f6368;">
<tr><td style="padding:8px 0;border-bottom:1px solid #e8eaed;">Date &amp; time</td><td style="padding:8px 0;border-bottom:1px solid #e8eaed;text-align:right;color:#202124;">{{date}}</td></tr>
<tr><td style="padding:8px 0;border-bottom:1px solid #e8eaed;">Device</td><td style="padding:8px 0;border-bottom:1px solid #e8eaed;text-align:right;color:#202124;">Windows computer</td></tr>
<tr><td style="padding:8px 0;">Location</td><td style="padding:8px 0;text-align:right;color:#202124;">Unknown location</td></tr>
</table>
</td></tr>
<tr><td style="padding-bottom:32px;">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#1a73e8;color:#ffffff;font-size:14px;font-weight:500;text-decoration:none;padding:10px 24px;border-radius:4px;">Change password</a>
</td></tr>
<tr><td style="border-top:1px solid #e8eaed;padding-top:24px;">
<p style="margin:0;font-size:12px;color:#5f6368;line-height:18px;">You can also see security activity at<br><a href="#" style="color:#1a73e8;text-decoration:none;">https://myaccount.google.com/notifications</a></p>
</td></tr>
<tr><td style="padding-top:32px;">
<p style="margin:0;font-size:11px;color:#5f6368;line-height:18px;">You received this email to let you know about important changes to your Google Account and services.<br>© {{year}} Google LLC, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "Critical Google security alert mimicking real breach notification",
        "language": "EN",
        "is_builtin": True
    },
    # ============ SLACK ============
    {
        "name": "Slack - Workspace Invitation",
        "category": "IT",
        "subject": "{{first_name}}, you've been invited to join a Slack workspace",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f4ede4;font-family:Slack-Lato,Lato,appleLogo,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:45px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;">
<tr><td style="background-color:#4a154b;padding:32px 48px;text-align:center;">
<img src="https://a.slack-edge.com/80588/marketing/img/icons/icon_slack_hash_colored.png" alt="Slack" style="height:36px;width:auto;">
</td></tr>
<tr><td style="padding:48px;">
<h1 style="margin:0 0 24px;font-size:28px;font-weight:700;color:#1d1c1d;text-align:center;">Join your team on Slack</h1>
<p style="margin:0 0 24px;font-size:16px;color:#454245;line-height:24px;text-align:center;">{{first_name}}, <strong>Sarah Johnson</strong> has invited you to join the <strong>Acme Corporation</strong> workspace on Slack.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f8f8f8;border-radius:8px;margin-bottom:32px;">
<tr><td style="padding:24px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:48px;vertical-align:top;">
<div style="width:48px;height:48px;background-color:#4a154b;border-radius:8px;display:flex;align-items:center;justify-content:center;">
<span style="color:#ffffff;font-size:20px;font-weight:700;">A</span>
</div>
</td>
<td style="padding-left:16px;vertical-align:top;">
<p style="margin:0;font-size:18px;font-weight:700;color:#1d1c1d;">Acme Corporation</p>
<p style="margin:4px 0 0;font-size:14px;color:#616061;">1,247 members</p>
</td>
</tr>
</table>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#4a154b;color:#ffffff;font-size:16px;font-weight:700;text-decoration:none;padding:16px 32px;border-radius:4px;">Join Now</a>
</td></tr>
</table>
<p style="margin:32px 0 0;font-size:13px;color:#616061;text-align:center;">This invitation will expire in 7 days.</p>
</td></tr>
<tr><td style="background-color:#f8f8f8;padding:24px 48px;text-align:center;">
<p style="margin:0;font-size:12px;color:#696969;">Made with 💜 by Slack Technologies, LLC<br>500 Howard Street, San Francisco, CA 94105</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "easy",
        "description": "Realistic Slack workspace invitation email",
        "language": "EN",
        "is_builtin": True
    },
    # ============ CHASE BANK ============
    {
        "name": "Chase - Suspicious Activity Alert",
        "category": "Banking",
        "subject": "Alert: Unusual activity on your Chase account",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:0;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;">
<!-- Header -->
<tr><td style="background-color:#0060af;padding:20px 30px;">
<img src="https://static.chasecdn.com/content/dam/nextgen/global/icons/chase-logo-white.svg" alt="CHASE" style="height:32px;">
</td></tr>
<!-- Alert Banner -->
<tr><td style="background-color:#c41230;padding:12px 30px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:24px;vertical-align:middle;padding-right:10px;">
<span style="color:#ffffff;font-size:20px;">⚠</span>
</td>
<td style="color:#ffffff;font-size:14px;font-weight:bold;">
Security Alert: Unusual Account Activity
</td>
</tr>
</table>
</td></tr>
<!-- Content -->
<tr><td style="background-color:#ffffff;padding:30px;">
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:22px;">Dear {{first_name}},</p>
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:22px;">We detected unusual activity on your Chase account that requires your immediate attention.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f7f7f7;margin-bottom:20px;">
<tr><td style="padding:20px;">
<p style="margin:0 0 15px;font-size:14px;color:#666666;font-weight:bold;text-transform:uppercase;letter-spacing:0.5px;">Transaction Details</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:8px 0;color:#666666;border-bottom:1px solid #e5e5e5;">Amount</td><td style="padding:8px 0;color:#c41230;font-weight:bold;text-align:right;border-bottom:1px solid #e5e5e5;">$2,847.00</td></tr>
<tr><td style="padding:8px 0;color:#666666;border-bottom:1px solid #e5e5e5;">Merchant</td><td style="padding:8px 0;color:#333333;text-align:right;border-bottom:1px solid #e5e5e5;">ELECTRONICS-ONLINE.NET</td></tr>
<tr><td style="padding:8px 0;color:#666666;border-bottom:1px solid #e5e5e5;">Date</td><td style="padding:8px 0;color:#333333;text-align:right;border-bottom:1px solid #e5e5e5;">{{date}}</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Card ending in</td><td style="padding:8px 0;color:#333333;text-align:right;">****4892</td></tr>
</table>
</td></tr>
</table>
<p style="margin:0 0 25px;font-size:15px;color:#333333;line-height:22px;">If you don't recognize this transaction, please verify your account immediately to prevent unauthorized access.</p>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0060af;color:#ffffff;font-size:14px;font-weight:bold;text-decoration:none;padding:14px 28px;border-radius:3px;">Verify Account Activity</a>
</td></tr>
</table>
<p style="margin:25px 0 0;font-size:13px;color:#666666;line-height:20px;">If you did authorize this transaction, no action is needed.</p>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#f7f7f7;padding:25px 30px;">
<p style="margin:0 0 10px;font-size:11px;color:#666666;line-height:16px;">This is an automated message from Chase. Please do not reply to this email.</p>
<p style="margin:0;font-size:11px;color:#666666;line-height:16px;">© 2024 JPMorgan Chase &amp; Co. Member FDIC</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "Authentic Chase Bank fraud alert with transaction details",
        "language": "EN",
        "is_builtin": True
    },
    # ============ PAYPAL ============
    {
        "name": "PayPal - Account Limitation",
        "category": "Banking",
        "subject": "Your PayPal account has been limited",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f5f7fa;font-family:PayPalSansSmall,Helvetica Neue,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:30px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:16px;overflow:hidden;">
<tr><td style="padding:32px 40px;text-align:center;border-bottom:1px solid #eaeced;">
<img src="https://www.paypalobjects.com/digitalassets/c/website/logo/full-text/pp_fc_hl.svg" alt="PayPal" style="height:28px;">
</td></tr>
<tr><td style="padding:40px;">
<h1 style="margin:0 0 20px;font-size:24px;font-weight:500;color:#001c64;text-align:center;">Your account access is limited</h1>
<p style="margin:0 0 24px;font-size:16px;color:#2c2e2f;line-height:24px;">Hi {{first_name}},</p>
<p style="margin:0 0 24px;font-size:16px;color:#2c2e2f;line-height:24px;">We've noticed unusual activity in your PayPal account and have temporarily limited what you can do until you confirm it's really you.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#fff8e6;border:1px solid #f5c242;border-radius:12px;margin-bottom:24px;">
<tr><td style="padding:20px;">
<p style="margin:0;font-size:14px;color:#6c5300;line-height:20px;"><strong>What's limited:</strong><br>• Sending money<br>• Withdrawing funds<br>• Removing bank accounts or cards</p>
</td></tr>
</table>
<p style="margin:0 0 32px;font-size:16px;color:#2c2e2f;line-height:24px;">To restore full access, please verify your identity by providing the requested information.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0070ba;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;padding:14px 32px;border-radius:24px;">Restore Access</a>
</td></tr>
</table>
<p style="margin:32px 0 0;font-size:13px;color:#687173;line-height:20px;text-align:center;">If you don't complete this verification within 48 hours, your account access may be further restricted.</p>
</td></tr>
<tr><td style="background-color:#f5f7fa;padding:24px 40px;text-align:center;">
<p style="margin:0 0 8px;font-size:12px;color:#687173;">Help &amp; Contact | Security | Apps</p>
<p style="margin:0;font-size:11px;color:#687173;">PayPal is committed to preventing fraudulent emails. Emails from PayPal will always contain your full name.<br>© 2024 PayPal, Inc. All rights reserved.</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "Realistic PayPal account limitation notice",
        "language": "EN",
        "is_builtin": True
    },
    # ============ AMAZON ============
    {
        "name": "Amazon - Order Confirmation Issue",
        "category": "E-commerce",
        "subject": "Problem with your Amazon order #112-4892756-3847261",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#eaeded;font-family:Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:0;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;">
<!-- Header -->
<tr><td style="background-color:#232f3e;padding:14px 20px;">
<img src="https://m.media-amazon.com/images/G/01/x-locale/cs/help/images/gateway/self-service/fshub/amazon-logo.png" alt="Amazon" style="height:28px;">
</td></tr>
<!-- Content -->
<tr><td style="background-color:#ffffff;padding:20px;">
<h1 style="margin:0 0 20px;font-size:18px;font-weight:400;color:#c45500;">There's a problem with your order</h1>
<p style="margin:0 0 16px;font-size:14px;color:#111111;line-height:20px;">Hello {{first_name}},</p>
<p style="margin:0 0 16px;font-size:14px;color:#111111;line-height:20px;">We're unable to process your recent order because we couldn't verify your payment information.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f3f3f3;border-radius:8px;margin-bottom:20px;">
<tr><td style="padding:16px;">
<p style="margin:0 0 12px;font-size:13px;color:#565959;">Order #112-4892756-3847261</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:80px;vertical-align:top;padding-right:12px;">
<div style="width:80px;height:80px;background-color:#ffffff;border:1px solid #ddd;border-radius:4px;"></div>
</td>
<td style="vertical-align:top;">
<p style="margin:0 0 4px;font-size:14px;color:#111111;font-weight:bold;">Apple AirPods Pro (2nd Generation)</p>
<p style="margin:0 0 4px;font-size:13px;color:#565959;">Qty: 1</p>
<p style="margin:0;font-size:14px;color:#111111;font-weight:bold;">$249.00</p>
</td>
</tr>
</table>
</td></tr>
</table>
<p style="margin:0 0 20px;font-size:14px;color:#111111;line-height:20px;">Please update your payment method within 24 hours to avoid order cancellation.</p>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#ffd814;color:#0f1111;font-size:14px;text-decoration:none;padding:10px 20px;border-radius:8px;border:1px solid #fcd200;">Update Payment Method</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#f3f3f3;padding:20px;">
<p style="margin:0 0 10px;font-size:12px;color:#565959;line-height:18px;">This email was sent from a notification-only address that cannot accept incoming email. Please do not reply to this message.</p>
<p style="margin:0;font-size:11px;color:#999999;">© 2024, Amazon.com, Inc. or its affiliates. All rights reserved. Amazon, Amazon.com and the Amazon logo are registered trademarks.</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "Amazon order payment issue notification",
        "language": "EN",
        "is_builtin": True
    },
    # ============ NETFLIX ============
    {
        "name": "Netflix - Payment Update Required",
        "category": "E-commerce",
        "subject": "Update your payment details to continue watching",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#000000;font-family:Netflix Sans,Helvetica Neue,Helvetica,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:0;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#000000;">
<!-- Header -->
<tr><td style="padding:24px 40px;">
<img src="https://assets.nflxext.com/ffe/siteui/email/20171127_Netflix_logo_SMALL.png" alt="NETFLIX" style="height:24px;">
</td></tr>
<!-- Content -->
<tr><td style="padding:0 40px 40px;">
<h1 style="margin:0 0 24px;font-size:32px;font-weight:500;color:#ffffff;line-height:40px;">Your membership is on hold</h1>
<p style="margin:0 0 24px;font-size:16px;color:#b3b3b3;line-height:26px;">Hi {{first_name}},</p>
<p style="margin:0 0 24px;font-size:16px;color:#b3b3b3;line-height:26px;">We were unable to process payment for your Netflix membership. To continue watching without interruption, please update your payment details.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#1a1a1a;border-radius:4px;margin-bottom:32px;">
<tr><td style="padding:24px;">
<p style="margin:0 0 8px;font-size:14px;color:#737373;">Account</p>
<p style="margin:0 0 16px;font-size:16px;color:#ffffff;">{{email}}</p>
<p style="margin:0 0 8px;font-size:14px;color:#737373;">Payment method</p>
<p style="margin:0;font-size:16px;color:#ffffff;">Visa ending in 4821 <span style="color:#e50914;">(declined)</span></p>
</td></tr>
</table>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#e50914;color:#ffffff;font-size:16px;font-weight:500;text-decoration:none;padding:16px 24px;border-radius:4px;">UPDATE PAYMENT</a>
</td></tr>
</table>
<p style="margin:32px 0 0;font-size:14px;color:#737373;line-height:22px;">If you need help, visit the <a href="#" style="color:#ffffff;text-decoration:none;">Help Center</a>.</p>
</td></tr>
<!-- Footer -->
<tr><td style="padding:24px 40px;border-top:1px solid #333333;">
<p style="margin:0;font-size:13px;color:#737373;line-height:20px;">This email was sent to {{email}} because it's associated with a Netflix account.<br><br>Netflix, Inc., 100 Winchester Circle, Los Gatos, CA 95032 USA</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "Netflix payment failure notification with dark theme",
        "language": "EN",
        "is_builtin": True
    },
    # ============ DOCUSIGN ============
    {
        "name": "DocuSign - Contract Signature",
        "category": "Business",
        "subject": "Please DocuSign: Employment Agreement - Confidential",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:30px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:4px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
<!-- Header -->
<tr><td style="background-color:#ffc829;padding:20px 30px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td><span style="font-size:24px;font-weight:700;color:#1a1a1a;">DocuSign</span></td>
<td style="text-align:right;"><span style="font-size:12px;color:#1a1a1a;">CONFIDENTIAL</span></td>
</tr>
</table>
</td></tr>
<!-- Content -->
<tr><td style="padding:40px 30px;">
<h1 style="margin:0 0 24px;font-size:22px;font-weight:400;color:#333333;">Please review and sign this document</h1>
<table role="presentation" style="width:100%;border:none;border-spacing:0;border-left:4px solid #ffc829;background-color:#fafafa;margin-bottom:24px;">
<tr><td style="padding:20px;">
<p style="margin:0 0 8px;font-size:16px;font-weight:600;color:#333333;">Employment Agreement - {{last_name}}</p>
<p style="margin:0 0 4px;font-size:14px;color:#666666;">From: Sarah Johnson, HR Director</p>
<p style="margin:0;font-size:14px;color:#666666;">Sent: {{date}}</p>
</td></tr>
</table>
<p style="margin:0 0 24px;font-size:15px;color:#333333;line-height:24px;">{{first_name}},</p>
<p style="margin:0 0 24px;font-size:15px;color:#333333;line-height:24px;">Sarah Johnson has requested your signature on the attached document. Please review the document and sign it at your earliest convenience.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#fff8e1;border-radius:4px;margin-bottom:24px;">
<tr><td style="padding:16px;">
<p style="margin:0;font-size:14px;color:#f57c00;"><strong>⏱ Expires:</strong> This document will expire in 3 days.</p>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#ffc829;color:#1a1a1a;font-size:16px;font-weight:700;text-decoration:none;padding:16px 40px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px;">Review Document</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#f8f8f8;padding:24px 30px;">
<p style="margin:0 0 16px;font-size:12px;color:#666666;line-height:18px;">Do not share this email. This email contains a secure link to DocuSign. Please do not share this email, link, or access code with others.</p>
<p style="margin:0;font-size:11px;color:#999999;">Powered by DocuSign, Inc. 221 Main Street, Suite 1550, San Francisco, CA 94105</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "Professional DocuSign signature request for employment documents",
        "language": "EN",
        "is_builtin": True
    },
    # ============ LINKEDIN ============
    {
        "name": "LinkedIn - Profile Views",
        "category": "Social Media",
        "subject": "{{first_name}}, you appeared in 89 searches this week",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f3f2ef;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 0 0 1px rgba(0,0,0,0.08);">
<!-- Header -->
<tr><td style="background-color:#0a66c2;padding:16px 24px;">
<span style="font-size:26px;font-weight:600;color:#ffffff;">in</span>
</td></tr>
<!-- Content -->
<tr><td style="padding:24px;">
<p style="margin:0 0 4px;font-size:14px;color:#00000099;">Your weekly search stats</p>
<h1 style="margin:0 0 24px;font-size:20px;font-weight:600;color:#000000e6;">You appeared in 89 searches this week</h1>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f3f2ef;border-radius:8px;margin-bottom:24px;">
<tr><td style="padding:24px;text-align:center;">
<p style="margin:0;font-size:48px;font-weight:700;color:#0a66c2;">89</p>
<p style="margin:8px 0 0;font-size:14px;color:#00000099;">search appearances</p>
</td></tr>
</table>
<p style="margin:0 0 24px;font-size:14px;color:#00000099;line-height:20px;">Your profile is showing up in searches by recruiters and hiring managers. See who's searching for professionals like you.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;border:1px solid #e0e0e0;border-radius:8px;margin-bottom:24px;">
<tr><td style="padding:16px;">
<p style="margin:0 0 4px;font-size:14px;font-weight:600;color:#000000e6;">Top searcher companies</p>
<p style="margin:0;font-size:13px;color:#00000099;">Google, Microsoft, Amazon, and 12 others</p>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0a66c2;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;padding:12px 24px;border-radius:24px;">See all search appearances</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="padding:24px;background-color:#f3f2ef;text-align:center;">
<p style="margin:0 0 8px;font-size:12px;color:#00000099;">This email was sent to {{email}}</p>
<p style="margin:0;font-size:11px;color:#00000099;">LinkedIn Corporation, 1000 W Maude Ave, Sunnyvale, CA 94085</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "easy",
        "description": "LinkedIn weekly profile search statistics",
        "language": "EN",
        "is_builtin": True
    },
    # ============ DROPBOX ============
    {
        "name": "Dropbox - Shared File",
        "category": "Business",
        "subject": "{{first_name}}, Michael Chen shared \"Q4 Financial Report.xlsx\" with you",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f7f7f7;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:520px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
<!-- Header -->
<tr><td style="padding:32px;text-align:center;border-bottom:1px solid #f0f0f0;">
<img src="https://cfl.dropboxstatic.com/static/images/logo_catalog/dropbox_logo_glyph_m1.svg" alt="Dropbox" style="height:40px;">
</td></tr>
<!-- Content -->
<tr><td style="padding:32px;">
<h1 style="margin:0 0 8px;font-size:24px;font-weight:600;color:#1e1919;text-align:center;">"Q4 Financial Report.xlsx"</h1>
<p style="margin:0 0 32px;font-size:14px;color:#637282;text-align:center;">shared with you</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f7f7f7;border-radius:8px;margin-bottom:24px;">
<tr><td style="padding:20px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:48px;vertical-align:top;">
<div style="width:48px;height:48px;background-color:#0061fe;border-radius:50%;display:inline-block;text-align:center;line-height:48px;color:#ffffff;font-weight:600;font-size:18px;">MC</div>
</td>
<td style="padding-left:16px;vertical-align:top;">
<p style="margin:0 0 4px;font-size:15px;font-weight:600;color:#1e1919;">Michael Chen</p>
<p style="margin:0;font-size:13px;color:#637282;">CFO • Acme Corporation</p>
</td>
</tr>
</table>
</td></tr>
</table>
<p style="margin:0 0 24px;font-size:14px;color:#637282;line-height:22px;text-align:center;">"Please review the Q4 numbers before our meeting tomorrow at 2 PM. Let me know if you have any questions."</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0061fe;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:8px;">Open file</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="padding:24px;background-color:#f7f7f7;text-align:center;">
<p style="margin:0;font-size:12px;color:#637282;">Dropbox • San Francisco, CA</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "Dropbox file sharing notification from CFO",
        "language": "EN",
        "is_builtin": True
    },
    # ============ DHL ============
    {
        "name": "DHL - Delivery On Hold",
        "category": "Delivery",
        "subject": "DHL: Your shipment is waiting - Action required",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Delivery,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:0;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;">
<!-- Header -->
<tr><td style="background-color:#ffcc00;padding:20px 30px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td><span style="font-size:32px;font-weight:800;color:#d40511;">DHL</span></td>
<td style="text-align:right;font-size:12px;color:#333333;">EXPRESS</td>
</tr>
</table>
</td></tr>
<!-- Alert -->
<tr><td style="background-color:#d40511;padding:12px 30px;">
<p style="margin:0;font-size:14px;font-weight:600;color:#ffffff;">⚠ Delivery Exception - Action Required</p>
</td></tr>
<!-- Content -->
<tr><td style="background-color:#ffffff;padding:30px;">
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">Dear Customer,</p>
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">We attempted to deliver your package but were unable to complete the delivery. Your shipment is currently being held at our local facility.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;border:1px solid #e5e5e5;margin-bottom:20px;">
<tr><td style="padding:20px;background-color:#fafafa;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:8px 0;color:#666666;width:40%;">Tracking Number</td><td style="padding:8px 0;color:#333333;font-weight:600;">1234567890</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Status</td><td style="padding:8px 0;color:#d40511;font-weight:600;">On Hold - Address Incomplete</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Shipment Date</td><td style="padding:8px 0;color:#333333;">{{date}}</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Service Fee</td><td style="padding:8px 0;color:#333333;">$3.99 (customs processing)</td></tr>
</table>
</td></tr>
</table>
<p style="margin:0 0 24px;font-size:15px;color:#333333;line-height:24px;">Please confirm your delivery address and pay the customs processing fee to release your package.</p>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#d40511;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:14px 28px;border-radius:4px;">Schedule Redelivery</a>
</td></tr>
</table>
<p style="margin:24px 0 0;font-size:13px;color:#666666;line-height:20px;">Your package will be returned to sender if not claimed within 5 business days.</p>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#333333;padding:20px 30px;">
<p style="margin:0;font-size:11px;color:#999999;line-height:18px;">© 2024 DHL International GmbH. All rights reserved.<br>DHL Express, Charles-de-Gaulle-Str. 20, 53113 Bonn, Germany</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "DHL delivery exception with customs fee",
        "language": "EN",
        "is_builtin": True
    },
    # ============ INSTAGRAM ============
    {
        "name": "Instagram - Suspicious Login",
        "category": "Social Media",
        "subject": "Unusual login attempt on your Instagram account",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#fafafa;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:450px;border:none;border-spacing:0;background-color:#ffffff;border:1px solid #dbdbdb;border-radius:4px;">
<!-- Content -->
<tr><td style="padding:40px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;margin-bottom:24px;">
<tr><td align="center">
<img src="https://static.cdninstagram.com/rsrc.php/v3/yS/r/ajlEU-wEDyo.png" alt="Instagram" style="height:52px;">
</td></tr>
</table>
<h1 style="margin:0 0 16px;font-size:16px;font-weight:600;color:#262626;text-align:center;">Suspicious login attempt</h1>
<p style="margin:0 0 24px;font-size:14px;color:#262626;line-height:20px;text-align:center;">Hi {{first_name}},</p>
<p style="margin:0 0 24px;font-size:14px;color:#262626;line-height:20px;text-align:center;">We detected an unusual login attempt on your Instagram account. If this was you, you can safely ignore this message.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#fafafa;border-radius:4px;margin-bottom:24px;">
<tr><td style="padding:16px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:6px 0;color:#8e8e8e;">When</td><td style="padding:6px 0;color:#262626;text-align:right;">{{date}}</td></tr>
<tr><td style="padding:6px 0;color:#8e8e8e;">Device</td><td style="padding:6px 0;color:#262626;text-align:right;">Android Device</td></tr>
<tr><td style="padding:6px 0;color:#8e8e8e;">Location</td><td style="padding:6px 0;color:#262626;text-align:right;">Unknown</td></tr>
</table>
</td></tr>
</table>
<p style="margin:0 0 24px;font-size:14px;color:#262626;line-height:20px;text-align:center;">If this wasn't you, secure your account now.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#0095f6;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 24px;border-radius:8px;">Secure Account</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="padding:16px;border-top:1px solid #dbdbdb;text-align:center;">
<p style="margin:0;font-size:12px;color:#8e8e8e;">from <strong style="color:#262626;">Instagram</strong></p>
</td></tr>
</table>
<p style="margin:24px 0 0;font-size:12px;color:#8e8e8e;text-align:center;">© Instagram. Meta Platforms, Inc., 1601 Willow Road, Menlo Park, CA 94025</p>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "Instagram suspicious login security alert",
        "language": "EN",
        "is_builtin": True
    },
    # ============ HR SALARY ============
    {
        "name": "HR Portal - Salary Review",
        "category": "HR",
        "subject": "Confidential: Your 2024 Compensation Review is Ready",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
<!-- Header -->
<tr><td style="background-color:#1a5f4a;padding:24px 40px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td><span style="font-size:20px;font-weight:600;color:#ffffff;">HR Portal</span></td>
<td style="text-align:right;"><span style="font-size:11px;color:#ffffff;background-color:rgba(255,255,255,0.2);padding:4px 8px;border-radius:4px;">CONFIDENTIAL</span></td>
</tr>
</table>
</td></tr>
<!-- Content -->
<tr><td style="padding:40px;">
<h1 style="margin:0 0 24px;font-size:24px;font-weight:600;color:#333333;">2024 Annual Compensation Review</h1>
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">Dear {{first_name}},</p>
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">Your annual performance and compensation review document is now available in the HR Portal. This document contains confidential information regarding:</p>
<ul style="margin:0 0 24px;padding-left:20px;color:#333333;font-size:15px;line-height:28px;">
<li>Your 2024 performance evaluation</li>
<li>Salary adjustment effective January 1, 2025</li>
<li>Bonus allocation</li>
<li>Stock option grants (if applicable)</li>
</ul>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#e8f5e9;border-left:4px solid #1a5f4a;margin-bottom:24px;">
<tr><td style="padding:16px;">
<p style="margin:0;font-size:14px;color:#1a5f4a;"><strong>Action Required:</strong> Please review and acknowledge receipt of this document by {{date}}.</p>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#fafafa;border-radius:4px;margin-bottom:24px;">
<tr><td style="padding:20px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:6px 0;color:#666666;">Document</td><td style="padding:6px 0;color:#333333;text-align:right;">2024_Compensation_Review_{{last_name}}.pdf</td></tr>
<tr><td style="padding:6px 0;color:#666666;">From</td><td style="padding:6px 0;color:#333333;text-align:right;">Human Resources Department</td></tr>
</table>
</td></tr>
</table>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#1a5f4a;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:14px 32px;border-radius:4px;">View Document</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#fafafa;padding:24px 40px;">
<p style="margin:0;font-size:12px;color:#666666;line-height:18px;">This is a confidential communication intended only for the named recipient. Please do not forward or share this email.</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "HR annual compensation review notification",
        "language": "EN",
        "is_builtin": True
    },
    # ============ COINBASE ============
    {
        "name": "Coinbase - Withdrawal Alert",
        "category": "Crypto",
        "subject": "Withdrawal request: 0.5 BTC ($21,450.00) pending",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f8f8f8;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:520px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
<!-- Header -->
<tr><td style="background-color:#0052ff;padding:24px;text-align:center;">
<span style="font-size:24px;font-weight:600;color:#ffffff;">coinbase</span>
</td></tr>
<!-- Alert -->
<tr><td style="background-color:#fef2f2;padding:16px 24px;border-bottom:1px solid #fecaca;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:24px;vertical-align:top;">
<span style="font-size:18px;">⚠️</span>
</td>
<td style="padding-left:12px;">
<p style="margin:0;font-size:14px;font-weight:600;color:#dc2626;">Withdrawal request detected</p>
</td>
</tr>
</table>
</td></tr>
<!-- Content -->
<tr><td style="padding:32px 24px;">
<p style="margin:0 0 20px;font-size:15px;color:#1e293b;line-height:24px;">Hi {{first_name}},</p>
<p style="margin:0 0 24px;font-size:15px;color:#1e293b;line-height:24px;">A withdrawal request was initiated from your Coinbase account. If you didn't make this request, please cancel it immediately.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f8fafc;border-radius:8px;margin-bottom:24px;">
<tr><td style="padding:20px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:8px 0;color:#64748b;">Amount</td><td style="padding:8px 0;color:#1e293b;font-weight:600;text-align:right;">0.5 BTC</td></tr>
<tr><td style="padding:8px 0;color:#64748b;">Value</td><td style="padding:8px 0;color:#dc2626;font-weight:600;text-align:right;">$21,450.00 USD</td></tr>
<tr><td style="padding:8px 0;color:#64748b;">To Address</td><td style="padding:8px 0;color:#1e293b;font-family:monospace;text-align:right;font-size:12px;">bc1qxy2kgdygjrs...qz7qgm4</td></tr>
<tr><td style="padding:8px 0;color:#64748b;">Time</td><td style="padding:8px 0;color:#1e293b;text-align:right;">{{date}}</td></tr>
<tr><td style="padding:8px 0;color:#64748b;">Status</td><td style="padding:8px 0;color:#f59e0b;font-weight:600;text-align:right;">Pending (24h hold)</td></tr>
</table>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#dc2626;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 32px;border-radius:8px;margin-right:12px;">Cancel Withdrawal</a>
</td></tr>
</table>
<p style="margin:24px 0 0;font-size:13px;color:#64748b;line-height:20px;text-align:center;">If you authorized this withdrawal, no action is needed. The transaction will process after the 24-hour security hold.</p>
</td></tr>
<!-- Footer -->
<tr><td style="padding:20px 24px;background-color:#f8fafc;text-align:center;">
<p style="margin:0;font-size:11px;color:#64748b;">Coinbase, Inc. 548 Market Street, San Francisco, CA 94104</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "hard",
        "description": "Coinbase cryptocurrency withdrawal security alert",
        "language": "EN",
        "is_builtin": True
    },
    # ============ ZOOM ============
    {
        "name": "Zoom - Meeting Recording",
        "category": "IT",
        "subject": "Cloud Recording: Your meeting recording is available",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f6f6f6;font-family:Lato,Helvetica Neue,Helvetica,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:540px;border:none;border-spacing:0;background-color:#ffffff;border-radius:12px;overflow:hidden;">
<!-- Header -->
<tr><td style="background-color:#2d8cff;padding:24px;text-align:center;">
<span style="font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-1px;">zoom</span>
</td></tr>
<!-- Content -->
<tr><td style="padding:40px;">
<h1 style="margin:0 0 8px;font-size:24px;font-weight:600;color:#232333;">Cloud Recording Available</h1>
<p style="margin:0 0 32px;font-size:14px;color:#747487;">Your meeting recording is ready to view</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#f8f8f8;border-radius:8px;margin-bottom:32px;">
<tr><td style="padding:24px;">
<p style="margin:0 0 16px;font-size:14px;color:#747487;">MEETING DETAILS</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:8px 0;color:#747487;">Topic</td><td style="padding:8px 0;color:#232333;font-weight:600;text-align:right;">Q4 Planning Session</td></tr>
<tr><td style="padding:8px 0;color:#747487;">Date</td><td style="padding:8px 0;color:#232333;text-align:right;">{{date}}</td></tr>
<tr><td style="padding:8px 0;color:#747487;">Duration</td><td style="padding:8px 0;color:#232333;text-align:right;">1 hour 23 minutes</td></tr>
<tr><td style="padding:8px 0;color:#747487;">Host</td><td style="padding:8px 0;color:#232333;text-align:right;">Sarah Johnson</td></tr>
</table>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#2d8cff;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;padding:14px 40px;border-radius:8px;">View Recording</a>
</td></tr>
</table>
<p style="margin:32px 0 0;font-size:13px;color:#747487;text-align:center;">This recording will be automatically deleted in 30 days.</p>
</td></tr>
<!-- Footer -->
<tr><td style="padding:24px;background-color:#f8f8f8;text-align:center;">
<p style="margin:0;font-size:12px;color:#747487;">Zoom Video Communications, Inc.<br>55 Almaden Blvd, San Jose, CA 95113</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "easy",
        "description": "Zoom cloud recording availability notification",
        "language": "EN",
        "is_builtin": True
    },
    # ============ QUICKBOOKS ============
    {
        "name": "QuickBooks - Invoice Payment",
        "category": "Finance",
        "subject": "Invoice #INV-2024-0847 from TechServices Inc - Due Tomorrow",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f4f5f7;font-family:AvenirNext,Avenir,Helvetica Neue,Helvetica,Arial,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
<!-- Header -->
<tr><td style="background-color:#2ca01c;padding:20px 32px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td><span style="font-size:24px;font-weight:700;color:#ffffff;">QuickBooks</span></td>
<td style="text-align:right;"><span style="font-size:12px;color:rgba(255,255,255,0.8);">INVOICE</span></td>
</tr>
</table>
</td></tr>
<!-- Alert -->
<tr><td style="background-color:#fef3cd;padding:12px 32px;border-bottom:1px solid #f5d78e;">
<p style="margin:0;font-size:14px;color:#856404;"><strong>⏰ Payment Reminder:</strong> This invoice is due tomorrow</p>
</td></tr>
<!-- Content -->
<tr><td style="padding:32px;">
<h1 style="margin:0 0 24px;font-size:22px;font-weight:600;color:#333333;">You have an invoice from TechServices Inc.</h1>
<table role="presentation" style="width:100%;border:none;border-spacing:0;border:1px solid #e4e4e4;border-radius:8px;margin-bottom:24px;">
<tr><td style="padding:24px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td style="padding-bottom:16px;border-bottom:1px solid #e4e4e4;">
<p style="margin:0 0 4px;font-size:14px;color:#666666;">Invoice number</p>
<p style="margin:0;font-size:16px;color:#333333;font-weight:600;">INV-2024-0847</p>
</td></tr>
<tr><td style="padding:16px 0;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:4px 0;color:#666666;">Due date</td><td style="padding:4px 0;color:#d63030;font-weight:600;text-align:right;">Tomorrow</td></tr>
<tr><td style="padding:4px 0;color:#666666;">Services</td><td style="padding:4px 0;color:#333333;text-align:right;">IT Consulting Services</td></tr>
</table>
</td></tr>
<tr><td style="padding-top:16px;border-top:1px solid #e4e4e4;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td style="font-size:14px;color:#666666;">Amount due</td><td style="font-size:28px;font-weight:700;color:#2ca01c;text-align:right;">$4,250.00</td></tr>
</table>
</td></tr>
</table>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#2ca01c;color:#ffffff;font-size:16px;font-weight:600;text-decoration:none;padding:14px 48px;border-radius:4px;">Review and Pay</a>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="padding:24px 32px;background-color:#f4f5f7;">
<p style="margin:0;font-size:12px;color:#666666;line-height:18px;">Intuit QuickBooks • 2700 Coast Ave, Mountain View, CA 94043<br>This invoice was sent via QuickBooks Online.</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "QuickBooks invoice payment reminder",
        "language": "EN",
        "is_builtin": True
    },
    # ============ FEDEX ============
    {
        "name": "FedEx - Delivery Exception",
        "category": "Delivery",
        "subject": "FedEx: Delivery Exception - Address Verification Required",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#ffffff;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:0;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;">
<!-- Header -->
<tr><td style="background-color:#4d148c;padding:16px 24px;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td><span style="font-size:28px;font-weight:700;color:#ff6600;">FedEx</span></td>
<td style="text-align:right;"><span style="font-size:11px;color:#ffffff;">Track | Ship | Manage</span></td>
</tr>
</table>
</td></tr>
<!-- Alert Bar -->
<tr><td style="background-color:#ffc107;padding:10px 24px;">
<p style="margin:0;font-size:14px;font-weight:600;color:#333333;">⚠ Delivery Exception</p>
</td></tr>
<!-- Content -->
<tr><td style="padding:32px 24px;">
<h1 style="margin:0 0 20px;font-size:20px;font-weight:600;color:#333333;">We need more information to deliver your package</h1>
<p style="margin:0 0 24px;font-size:15px;color:#333333;line-height:24px;">Your shipment has encountered a delivery exception. Please verify your delivery information to proceed.</p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;border:1px solid #e5e5e5;margin-bottom:24px;">
<tr><td style="padding:20px;background-color:#fafafa;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;font-size:14px;">
<tr><td style="padding:8px 0;color:#666666;width:40%;">Tracking Number</td><td style="padding:8px 0;color:#333333;font-weight:600;">794644790147</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Status</td><td style="padding:8px 0;color:#d63030;font-weight:600;">Exception - Address Verification Needed</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Ship Date</td><td style="padding:8px 0;color:#333333;">{{date}}</td></tr>
<tr><td style="padding:8px 0;color:#666666;">Current Location</td><td style="padding:8px 0;color:#333333;">Local FedEx Facility</td></tr>
</table>
</td></tr>
</table>
<table role="presentation" style="border:none;border-spacing:0;">
<tr><td>
<a href="{{tracking_link}}" style="display:inline-block;background-color:#ff6600;color:#ffffff;font-size:14px;font-weight:600;text-decoration:none;padding:12px 24px;border-radius:4px;">Verify Address</a>
</td></tr>
</table>
<p style="margin:24px 0 0;font-size:13px;color:#666666;">If not verified within 3 business days, the package will be returned to sender.</p>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#f5f5f5;padding:20px 24px;">
<p style="margin:0;font-size:11px;color:#666666;line-height:16px;">© FedEx 1995-2024 | FedEx Corporation, 942 South Shady Grove Road, Memphis, TN 38120</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "FedEx delivery exception requiring address verification",
        "language": "EN",
        "is_builtin": True
    },
    # ============ BENEFITS ENROLLMENT ============
    {
        "name": "HR Portal - Benefits Enrollment",
        "category": "HR",
        "subject": "Final Notice: Open Enrollment Closes Tomorrow",
        "html_content": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background-color:#f0f4f8;font-family:Arial,Helvetica,sans-serif;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center" style="padding:40px 20px;">
<table role="presentation" style="width:100%;max-width:600px;border:none;border-spacing:0;background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);">
<!-- Header -->
<tr><td style="background-color:#1565c0;padding:24px 40px;">
<span style="font-size:22px;font-weight:600;color:#ffffff;">Benefits Portal</span>
</td></tr>
<!-- Urgent Banner -->
<tr><td style="background-color:#fff3e0;padding:16px 40px;border-bottom:1px solid #ffe0b2;">
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr>
<td style="width:24px;vertical-align:top;">
<span style="font-size:20px;">⏰</span>
</td>
<td style="padding-left:12px;">
<p style="margin:0;font-size:15px;font-weight:600;color:#e65100;">Final Reminder: Open Enrollment ends tomorrow at 11:59 PM</p>
</td>
</tr>
</table>
</td></tr>
<!-- Content -->
<tr><td style="padding:40px;">
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">Dear {{first_name}},</p>
<p style="margin:0 0 20px;font-size:15px;color:#333333;line-height:24px;">This is your final reminder to complete your 2025 benefits enrollment. <strong>If you do not make your selections by tomorrow, you will be automatically enrolled in the default plan.</strong></p>
<table role="presentation" style="width:100%;border:none;border-spacing:0;background-color:#ffebee;border-radius:4px;margin-bottom:24px;">
<tr><td style="padding:20px;">
<p style="margin:0 0 12px;font-size:14px;font-weight:600;color:#c62828;">Your Current Status: INCOMPLETE</p>
<p style="margin:0;font-size:14px;color:#333333;">The following selections are still required:</p>
<ul style="margin:12px 0 0;padding-left:20px;color:#333333;font-size:14px;line-height:24px;">
<li>Medical Insurance</li>
<li>Dental Insurance</li>
<li>401(k) Contribution</li>
</ul>
</td></tr>
</table>
<table role="presentation" style="width:100%;border:none;border-spacing:0;">
<tr><td align="center">
<a href="{{tracking_link}}" style="display:inline-block;background-color:#1565c0;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:14px 40px;border-radius:4px;">Complete Enrollment Now</a>
</td></tr>
</table>
<p style="margin:32px 0 0;font-size:13px;color:#666666;line-height:20px;text-align:center;">If you have questions, please contact HR at benefits@company.com</p>
</td></tr>
<!-- Footer -->
<tr><td style="background-color:#f5f5f5;padding:24px 40px;">
<p style="margin:0;font-size:12px;color:#666666;line-height:18px;">This is an automated message from the Benefits Portal. Please do not reply to this email.</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>""",
        "difficulty": "medium",
        "description": "HR benefits open enrollment deadline reminder",
        "language": "EN",
        "is_builtin": True
    },
]
