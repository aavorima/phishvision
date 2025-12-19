"""
Check all SMS targets in the campaign
"""

from database import db
from models import SMSTarget, SMSCampaign
from app import app

def check_sms_targets():
    """Check all SMS targets"""
    with app.app_context():
        # Find the campaign
        campaign = SMSCampaign.query.filter(
            SMSCampaign.name.like('%December Cybersecurity%SMS%')
        ).first()

        if not campaign:
            print("Campaign not found")
            return

        print(f"Campaign: {campaign.name}")
        print(f"Campaign ID: {campaign.id}")
        print(f"Total Sent (from campaign): {campaign.total_sent}")
        print(f"\nTargets in database:")
        print("-" * 60)

        targets = SMSTarget.query.filter_by(campaign_id=campaign.id).all()

        if not targets:
            print("No targets found in this campaign")
        else:
            for i, target in enumerate(targets, 1):
                print(f"\nTarget {i}:")
                print(f"  ID: {target.id}")
                print(f"  Name: {target.name or 'Unknown'}")
                print(f"  Phone: {target.phone_number}")
                print(f"  Email: {target.email or 'N/A'}")
                print(f"  Department: {target.department or 'Unknown'}")
                print(f"  Clicked: {'Yes' if target.clicked_at else 'No'}")

        print(f"\n\nTotal targets in database: {len(targets)}")

if __name__ == '__main__':
    check_sms_targets()
