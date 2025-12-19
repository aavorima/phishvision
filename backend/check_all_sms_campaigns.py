"""
Check all SMS campaigns and their targets
"""

from database import db
from models import SMSTarget, SMSCampaign
from app import app

def check_all_sms_campaigns():
    """Check all SMS campaigns and targets"""
    with app.app_context():
        campaigns = SMSCampaign.query.all()

        print(f"Total SMS Campaigns: {len(campaigns)}\n")
        print("=" * 80)

        for campaign in campaigns:
            print(f"\nCampaign: {campaign.name}")
            print(f"ID: {campaign.id}")
            print(f"Status: {campaign.status}")
            print(f"Total Sent: {campaign.total_sent}")

            targets = SMSTarget.query.filter_by(campaign_id=campaign.id).all()
            print(f"Targets Count: {len(targets)}")

            if targets:
                print("\nTargets:")
                for i, target in enumerate(targets, 1):
                    print(f"  {i}. Name: {target.name or 'Unknown':<20} Phone: {target.phone_number:<20} Email: {target.email or 'N/A':<30} Dept: {target.department or 'Unknown'}")

            print("-" * 80)

if __name__ == '__main__':
    check_all_sms_campaigns()
