"""
Regenerate missing QR code for campaign
"""

import qrcode
import os
from app import app
from models import QRCodeCampaign

def regenerate_qr_code(campaign_id):
    """Regenerate QR code for a campaign"""
    with app.app_context():
        campaign = QRCodeCampaign.query.get(campaign_id)

        if not campaign:
            print(f"Campaign {campaign_id} not found")
            return

        print(f"Campaign: {campaign.name}")
        print(f"Target URL: {campaign.target_url}")
        print(f"Expected QR Image: {campaign.qr_image_path}")

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

        qr_path = os.path.join(qr_folder, campaign.qr_image_path)
        img.save(qr_path)

        print(f"[SUCCESS] QR code regenerated at: {qr_path}")

        # Verify file exists
        if os.path.exists(qr_path):
            file_size = os.path.getsize(qr_path)
            print(f"File exists: {qr_path} ({file_size} bytes)")
        else:
            print(f"[ERROR] File was not created!")

if __name__ == '__main__':
    # Regenerate for the missing campaign
    campaign_id = '6e49d971-bb4d-4f25-b7de-c5f3a9e14d50'
    regenerate_qr_code(campaign_id)
