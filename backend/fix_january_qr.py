"""
Fix January QR campaigns by regenerating their QR codes
"""

import qrcode
import os
from app import app
from models import QRCodeCampaign
from database import db

def fix_january_qr_campaigns():
    """Fix January QR campaigns"""
    with app.app_context():
        campaigns = QRCodeCampaign.query.filter(
            QRCodeCampaign.name.like('%January%')
        ).all()

        print(f'Found {len(campaigns)} January QR campaigns\n')

        for campaign in campaigns:
            print(f'Fixing: {campaign.name}')
            print(f'  ID: {campaign.id}')
            print(f'  Old QR Image: {campaign.qr_image_path}')

            # Generate new QR code filename based on campaign ID
            new_qr_filename = f'qr_{campaign.id}.png'
            campaign.qr_image_path = new_qr_filename

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(campaign.target_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Save to static folder
            qr_folder = os.path.join('static', 'qrcodes')
            os.makedirs(qr_folder, exist_ok=True)

            qr_path = os.path.join(qr_folder, new_qr_filename)
            img.save(qr_path)

            print(f'  New QR Image: {new_qr_filename}')
            print(f'  Saved to: {qr_path}')

            # Verify file exists
            if os.path.exists(qr_path):
                file_size = os.path.getsize(qr_path)
                print(f'  [SUCCESS] File created ({file_size} bytes)\n')
            else:
                print(f'  [ERROR] File was not created!\n')

        # Save changes to database
        db.session.commit()
        print('Database updated!')

if __name__ == '__main__':
    fix_january_qr_campaigns()
