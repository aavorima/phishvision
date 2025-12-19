"""
Delete specific SMS target by phone number from the profiling program campaign
"""

from database import db
from models import SMSTarget, SMSCampaign
from app import app

def delete_target():
    """Delete the unwanted target"""
    with app.app_context():
        # Find the campaign
        campaign = SMSCampaign.query.filter_by(
            id='c97c89c7-530d-4dc9-bb95-febc86d4b4a5'
        ).first()

        if not campaign:
            print("Campaign not found")
            return

        print(f"Campaign: {campaign.name}")
        print(f"Campaign ID: {campaign.id}\n")

        # Find the target with phone +994514843688
        target = SMSTarget.query.filter_by(
            campaign_id=campaign.id,
            phone_number='+994514843688'
        ).first()

        if not target:
            print("Target not found")
            return

        print(f"Found target to delete:")
        print(f"  ID: {target.id}")
        print(f"  Name: {target.name or 'Unknown'}")
        print(f"  Phone: {target.phone_number}")
        print(f"  Email: {target.email or 'N/A'}")
        print(f"  Department: {target.department or 'Unknown'}")

        # Delete the target
        db.session.delete(target)
        db.session.commit()

        print(f"\n[SUCCESS] Target deleted successfully!")

        # Verify remaining targets
        remaining = SMSTarget.query.filter_by(campaign_id=campaign.id).all()
        print(f"\nRemaining targets in campaign: {len(remaining)}")
        for i, t in enumerate(remaining, 1):
            print(f"  {i}. {t.name or 'Unknown'} - {t.phone_number}")

if __name__ == '__main__':
    delete_target()
