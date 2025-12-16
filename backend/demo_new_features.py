#!/usr/bin/env python3
"""
PhishVision - New Features Demo Script
Tests: Landing Pages, QR Code Phishing, SMS Phishing, Repeat Clicker Tracking
"""

import requests
import json
import time
import os

BASE_URL = "http://localhost:5000"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_json(data):
    print(f"{Colors.BLUE}{json.dumps(data, indent=2)}{Colors.END}")


def check_server():
    """Check if server is running"""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        return r.status_code == 200
    except:
        return False


def demo_landing_pages():
    """Demo: Credential Harvesting Landing Pages"""
    print_header("DEMO 1: Credential Harvesting Landing Pages")

    # 1. Create a landing page
    print_info("Creating a custom landing page...")

    landing_page_data = {
        "name": "Demo Corporate Login",
        "category": "corporate",
        "description": "Demo corporate SSO login page for testing",
        "difficulty": "medium",
        "html_content": """
<!DOCTYPE html>
<html>
<head>
    <title>Corporate Login</title>
    <style>
        body { font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f2f5; }
        .login-box { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 350px; }
        h2 { text-align: center; color: #333; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0052a3; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Corporate SSO Login</h2>
        <form action="/api/landing/capture/{{tracking_token}}" method="POST">
            <input type="hidden" name="tracking_token" value="{{tracking_token}}">
            <input type="email" name="email" placeholder="Email" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Sign In</button>
        </form>
    </div>
</body>
</html>
        """,
        "redirect_url": "/api/landing/training"
    }

    r = requests.post(f"{BASE_URL}/api/landing/pages", json=landing_page_data)
    if r.status_code == 201:
        page = r.json()
        print_success(f"Landing page created! ID: {page['id']}")
        print_info(f"View it at: {BASE_URL}/api/landing/serve/demo-token-123")
    else:
        print_error(f"Failed to create landing page: {r.text}")
        return None

    # 2. List all landing pages
    print_info("\nListing all landing pages...")
    r = requests.get(f"{BASE_URL}/api/landing/pages")
    pages = r.json()
    print_success(f"Found {len(pages)} landing pages:")
    for p in pages[:3]:
        print(f"   - {p['name']} ({p['category']}) - {p['difficulty']}")

    # 3. Get repeat offenders
    print_info("\nChecking for repeat offenders...")
    r = requests.get(f"{BASE_URL}/api/landing/repeat-offenders")
    data = r.json()
    print_success(f"Repeat offenders: {data['total']}")

    # 4. Get users requiring training
    print_info("\nChecking users requiring training...")
    r = requests.get(f"{BASE_URL}/api/landing/requires-training")
    data = r.json()
    print_success(f"Users requiring training: {data['total']}")

    return page['id'] if r.status_code == 200 else None


def demo_qr_phishing():
    """Demo: QR Code Phishing (Quishing)"""
    print_header("DEMO 2: QR Code Phishing (Quishing)")

    # 1. Create QR campaign
    print_info("Creating a QR code phishing campaign...")

    qr_campaign_data = {
        "name": "Office WiFi QR Test",
        "description": "Fake WiFi setup QR code for security awareness",
        "placement_location": "Break room poster",
        "color": "#1a73e8"
    }

    r = requests.post(f"{BASE_URL}/api/qr/campaigns", json=qr_campaign_data)
    if r.status_code == 201:
        campaign = r.json()
        print_success(f"QR Campaign created! ID: {campaign['id']}")
        print_info(f"Target URL: {campaign['target_url']}")
        print_info(f"QR Image: {BASE_URL}/api/qr/campaigns/{campaign['id']}/image")
        print_info(f"Printable Poster: {BASE_URL}/api/qr/campaigns/{campaign['id']}/poster")
        campaign_id = campaign['id']
    else:
        print_error(f"Failed to create QR campaign: {r.text}")
        return None

    # 2. List all QR campaigns
    print_info("\nListing all QR campaigns...")
    r = requests.get(f"{BASE_URL}/api/qr/campaigns")
    campaigns = r.json()
    print_success(f"Found {len(campaigns)} QR campaigns")

    # 3. Get QR stats
    print_info("\nGetting QR phishing statistics...")
    r = requests.get(f"{BASE_URL}/api/qr/stats")
    stats = r.json()
    print_success("QR Statistics:")
    print(f"   - Total campaigns: {stats['total_campaigns']}")
    print(f"   - Active campaigns: {stats['active_campaigns']}")
    print(f"   - Total scans: {stats['total_scans']}")

    # 4. Generate a quick QR code
    print_info("\nGenerating a quick test QR code...")
    r = requests.post(f"{BASE_URL}/api/qr/generate", json={"url": "https://example.com/test"})
    if r.status_code == 200:
        print_success("QR code generated successfully (PNG image)")

    return campaign_id


def demo_sms_phishing():
    """Demo: SMS Phishing (Smishing)"""
    print_header("DEMO 3: SMS Phishing (Smishing)")

    # 1. Get SMS templates
    print_info("Getting pre-built SMS templates...")
    r = requests.get(f"{BASE_URL}/api/sms/templates")
    templates = r.json()
    print_success(f"Found {len(templates)} SMS templates:")
    for t in templates:
        print(f"   - {t['name']} ({t['category']}) - {t['difficulty']}")

    # 2. Create SMS campaign
    print_info("\nCreating an SMS phishing campaign...")

    sms_campaign_data = {
        "name": "IT Password Reset Test",
        "description": "Test campaign for IT department awareness",
        "message_template": "IT Alert: Your corporate password expires today. Reset now: {{link}}",
        "sender_id": "IT-Dept"
    }

    r = requests.post(f"{BASE_URL}/api/sms/campaigns", json=sms_campaign_data)
    if r.status_code == 201:
        campaign = r.json()
        print_success(f"SMS Campaign created! ID: {campaign['id']}")
        campaign_id = campaign['id']
    else:
        print_error(f"Failed to create SMS campaign: {r.text}")
        return None

    # 3. Add targets
    print_info("\nAdding test targets...")
    targets_data = {
        "targets": [
            {"phone_number": "+1234567890", "email": "test1@company.com"},
            {"phone_number": "+1234567891", "email": "test2@company.com"},
            {"phone_number": "+1234567892", "email": "test3@company.com"}
        ]
    }

    r = requests.post(f"{BASE_URL}/api/sms/campaigns/{campaign_id}/targets", json=targets_data)
    if r.status_code == 200:
        data = r.json()
        print_success(f"Added {data['total_targets']} targets")

    # 4. Send campaign (mock mode)
    print_info("\nSending SMS campaign (MOCK MODE - no real SMS sent)...")
    r = requests.post(f"{BASE_URL}/api/sms/campaigns/{campaign_id}/send")
    if r.status_code == 200:
        data = r.json()
        print_success(f"Campaign sent!")
        print(f"   - Mock mode: {data['mock_mode']}")
        print(f"   - Sent: {data['results']['sent']}")
        print(f"   - Delivered: {data['results']['delivered']}")

    # 5. Get stats
    print_info("\nGetting SMS campaign statistics...")
    r = requests.get(f"{BASE_URL}/api/sms/stats")
    stats = r.json()
    print_success("SMS Statistics:")
    print(f"   - Total campaigns: {stats['total_campaigns']}")
    print(f"   - Total sent: {stats['total_sent']}")
    print(f"   - Total clicked: {stats['total_clicked']}")

    return campaign_id


def demo_repeat_clicker():
    """Demo: Repeat Clicker Tracking"""
    print_header("DEMO 4: Repeat Clicker Tracking")

    # 1. Create/update a user risk profile
    print_info("Creating a test user risk profile...")

    user_data = {
        "email": "repeat.clicker@company.com",
        "department": "Sales",
        "campaigns_received": 10,
        "campaigns_opened": 8,
        "campaigns_clicked": 5  # This should flag them as repeat offender
    }

    r = requests.post(f"{BASE_URL}/api/risk/users", json=user_data)
    if r.status_code in [200, 201]:
        user = r.json()
        print_success(f"User profile created/updated!")
        print(f"   - Email: {user['email']}")
        print(f"   - Risk Score: {user['risk_score']}")
        print(f"   - Risk Level: {user['risk_level']}")
        print(f"   - Repeat Offender: {user.get('is_repeat_offender', False)}")
        print(f"   - Requires Training: {user.get('requires_training', False)}")

    # 2. Get all high-risk users
    print_info("\nGetting high-risk users...")
    r = requests.get(f"{BASE_URL}/api/risk/users?risk_level=high")
    users = r.json()
    print_success(f"Found {len(users)} high-risk users")

    # 3. Get risk statistics
    print_info("\nGetting overall risk statistics...")
    r = requests.get(f"{BASE_URL}/api/risk/stats")
    if r.status_code == 200:
        stats = r.json()
        print_success("Risk Statistics:")
        print(f"   - Average risk score: {stats.get('average_risk_score', 'N/A')}")
        print(f"   - Risk distribution: {stats.get('risk_level_distribution', {})}")

    # 4. Get department heatmap
    print_info("\nGetting department risk heatmap...")
    r = requests.get(f"{BASE_URL}/api/risk/heatmap")
    if r.status_code == 200:
        heatmap = r.json()
        print_success(f"Heatmap data: {len(heatmap)} departments")


def show_api_endpoints():
    """Show all new API endpoints"""
    print_header("NEW API ENDPOINTS REFERENCE")

    endpoints = {
        "Landing Pages (Credential Harvesting)": [
            ("GET", "/api/landing/pages", "List all landing pages"),
            ("POST", "/api/landing/pages", "Create landing page"),
            ("POST", "/api/landing/clone", "Clone a website"),
            ("GET", "/api/landing/serve/<token>", "Serve fake login page"),
            ("POST", "/api/landing/capture/<token>", "Capture credential event"),
            ("GET", "/api/landing/repeat-offenders", "List repeat offenders"),
            ("GET", "/api/landing/requires-training", "Users needing training"),
        ],
        "QR Code Phishing (Quishing)": [
            ("GET", "/api/qr/campaigns", "List QR campaigns"),
            ("POST", "/api/qr/campaigns", "Create QR campaign"),
            ("GET", "/api/qr/campaigns/<id>/image", "Get QR code image"),
            ("GET", "/api/qr/campaigns/<id>/poster", "Printable poster"),
            ("GET", "/api/qr/scan/<tracking_id>", "Track QR scan"),
            ("GET", "/api/qr/stats", "QR statistics"),
            ("POST", "/api/qr/generate", "Quick QR generation"),
        ],
        "SMS Phishing (Smishing)": [
            ("GET", "/api/sms/campaigns", "List SMS campaigns"),
            ("POST", "/api/sms/campaigns", "Create SMS campaign"),
            ("POST", "/api/sms/campaigns/<id>/targets", "Add targets"),
            ("POST", "/api/sms/campaigns/<id>/send", "Send campaign"),
            ("GET", "/api/sms/click/<token>", "Track link click"),
            ("GET", "/api/sms/templates", "Pre-built templates"),
            ("GET", "/api/sms/stats", "SMS statistics"),
        ],
    }

    for category, eps in endpoints.items():
        print(f"\n{Colors.BOLD}{category}:{Colors.END}")
        for method, path, desc in eps:
            color = Colors.GREEN if method == "GET" else Colors.YELLOW
            print(f"  {color}{method:6}{Colors.END} {path:40} - {desc}")


def main():
    print(f"""
{Colors.BOLD}{Colors.CYAN}
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗ ██╗  ██╗██╗███████╗██╗  ██╗██╗   ██╗██╗███████╗    ║
║   ██╔══██╗██║  ██║██║██╔════╝██║  ██║██║   ██║██║██╔════╝    ║
║   ██████╔╝███████║██║███████╗███████║██║   ██║██║███████╗    ║
║   ██╔═══╝ ██╔══██║██║╚════██║██╔══██║╚██╗ ██╔╝██║╚════██║    ║
║   ██║     ██║  ██║██║███████║██║  ██║ ╚████╔╝ ██║███████║    ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ║
║                                                               ║
║            NEW FEATURES DEMO - December 2024                  ║
╚═══════════════════════════════════════════════════════════════╝
{Colors.END}
    """)

    # Check if server is running
    print_info("Checking if server is running...")
    if not check_server():
        print_error("Server is not running!")
        print_warning("Start the server first with: python app.py")
        print_warning("Then run this demo again.")
        return

    print_success("Server is running!")

    # Run demos
    try:
        demo_landing_pages()
        time.sleep(0.5)

        demo_qr_phishing()
        time.sleep(0.5)

        demo_sms_phishing()
        time.sleep(0.5)

        demo_repeat_clicker()

        # Show API reference
        show_api_endpoints()

        # Final summary
        print_header("DEMO COMPLETE!")
        print(f"""
{Colors.GREEN}All new features are working!{Colors.END}

{Colors.BOLD}To test manually:{Colors.END}

1. {Colors.CYAN}Landing Pages:{Colors.END}
   Open: {BASE_URL}/api/landing/pages

2. {Colors.CYAN}QR Code Image:{Colors.END}
   Check the QR campaigns and view their images

3. {Colors.CYAN}SMS Templates:{Colors.END}
   Open: {BASE_URL}/api/sms/templates

4. {Colors.CYAN}Training Pages:{Colors.END}
   - Landing: {BASE_URL}/api/landing/training
   - QR: {BASE_URL}/api/qr/training
   - SMS: {BASE_URL}/api/sms/training

{Colors.BOLD}Frontend URLs to test:{Colors.END}
   - Dashboard: http://localhost:3000
   - All new features are API-ready for frontend integration!
        """)

    except requests.exceptions.ConnectionError:
        print_error("Connection failed! Make sure the server is running.")
    except Exception as e:
        print_error(f"Error: {e}")


if __name__ == "__main__":
    main()
