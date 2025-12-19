"""
Check the January program and its associated campaigns
"""

from database import db
from models import CampaignProgram, Campaign, QRCodeCampaign, SMSCampaign, QRCodeTarget
from app import app

def check_january_program():
    """Check January program campaigns"""
    with app.app_context():
        # Find the January program
        program = CampaignProgram.query.filter(
            CampaignProgram.name.like('%January%')
        ).first()

        if not program:
            print("January program not found")
            return

        print(f"Program: {program.name}")
        print(f"Program ID: {program.id}")
        print(f"Description: {program.description}")
        print(f"\n" + "="*80)

        # Check Email campaigns
        email_campaigns = Campaign.query.filter_by(program_id=program.id).all()
        print(f"\nEMAIL CAMPAIGNS: {len(email_campaigns)}")
        for camp in email_campaigns:
            print(f"  - {camp.name} (ID: {camp.id}, Status: {camp.status})")
            print(f"    Targets: {len(camp.targets)}")

        # Check QR campaigns
        qr_campaigns = QRCodeCampaign.query.filter_by(program_id=program.id).all()
        print(f"\nQR CODE CAMPAIGNS: {len(qr_campaigns)}")
        for camp in qr_campaigns:
            print(f"  - {camp.name} (ID: {camp.id}, Status: {camp.status})")
            targets = QRCodeTarget.query.filter_by(campaign_id=camp.id).all()
            print(f"    Targets: {len(targets)}")
            print(f"    Total Scans: {camp.total_scans}")
            print(f"    Unique Scans: {camp.unique_scans}")

            if targets:
                print(f"\n    Target Details:")
                for t in targets:
                    print(f"      * {t.name} ({t.email})")
                    print(f"        Scanned: {'Yes' if t.scanned_at else 'No'}")
                    if t.scanned_at:
                        print(f"        Scanned at: {t.scanned_at}")

        # Check SMS campaigns
        sms_campaigns = SMSCampaign.query.filter_by(program_id=program.id).all()
        print(f"\nSMS CAMPAIGNS: {len(sms_campaigns)}")
        for camp in sms_campaigns:
            print(f"  - {camp.name} (ID: {camp.id}, Status: {camp.status})")
            print(f"    Targets: {len(camp.targets)}")

if __name__ == '__main__':
    check_january_program()
