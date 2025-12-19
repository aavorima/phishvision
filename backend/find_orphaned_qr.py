"""
Find QR campaigns and check their program association
"""

from database import db
from models import QRCodeCampaign, QRCodeTarget
from app import app

def find_qr_campaigns():
    """Find all QR campaigns"""
    with app.app_context():
        qr_campaigns = QRCodeCampaign.query.all()

        print(f"Total QR Campaigns: {len(qr_campaigns)}\n")
        print("=" * 80)

        for camp in qr_campaigns:
            print(f"\nCampaign: {camp.name}")
            print(f"ID: {camp.id}")
            print(f"Status: {camp.status}")
            print(f"Program ID: {camp.program_id or 'NOT LINKED TO ANY PROGRAM'}")
            print(f"Total Scans: {camp.total_scans}")
            print(f"Unique Scans: {camp.unique_scans}")

            # Get targets
            targets = QRCodeTarget.query.filter_by(campaign_id=camp.id).all()
            print(f"Targets: {len(targets)}")

            if targets:
                for t in targets:
                    print(f"  * {t.name} ({t.email}) - Scanned: {'Yes' if t.scanned_at else 'No'}")

            print("-" * 80)

if __name__ == '__main__':
    find_qr_campaigns()
