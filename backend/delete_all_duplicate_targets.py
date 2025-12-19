"""
Delete all SMS targets with phone number +994514843688
"""

from database import db
from models import SMSTarget
from app import app

def delete_all_duplicates():
    """Delete all targets with the unwanted phone number"""
    with app.app_context():
        # Find all targets with this phone number
        targets = SMSTarget.query.filter_by(phone_number='+994514843688').all()

        print(f"Found {len(targets)} target(s) with phone +994514843688\n")

        if not targets:
            print("No targets to delete")
            return

        for i, target in enumerate(targets, 1):
            print(f"Target {i}:")
            print(f"  ID: {target.id}")
            print(f"  Name: {target.name or 'Unknown'}")
            print(f"  Campaign ID: {target.campaign_id}")
            print(f"  Department: {target.department or 'Unknown'}")

            # Delete the target
            db.session.delete(target)
            print(f"  [DELETED]\n")

        db.session.commit()

        print(f"[SUCCESS] Deleted {len(targets)} target(s)")

if __name__ == '__main__':
    delete_all_duplicates()
