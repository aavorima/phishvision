"""
Fix QR campaigns to link them to the correct profiling program
"""
from models import QRCodeCampaign, CampaignProgram
from database import db
from app import app

with app.app_context():
    # Get the "May program"
    may_program = CampaignProgram.query.filter_by(name='May program').first()

    if not may_program:
        print("May program not found!")
    else:
        print(f"Found May program: {may_program.name} (ID: {may_program.id})")

        # Get all QR campaigns without a program_id
        orphan_qr_campaigns = QRCodeCampaign.query.filter_by(program_id=None).all()

        print(f"\nFound {len(orphan_qr_campaigns)} QR campaigns without program_id:")
        for qr in orphan_qr_campaigns:
            print(f"  - {qr.name} (ID: {qr.id})")

        if orphan_qr_campaigns:
            print(f"\nLinking all QR campaigns to '{may_program.name}'...")
            for qr in orphan_qr_campaigns:
                qr.program_id = may_program.id
                print(f"  [OK] Linked '{qr.name}' to program")

            db.session.commit()
            print("\n[SUCCESS] All QR campaigns linked successfully!")
        else:
            print("\nNo orphan QR campaigns to fix.")
