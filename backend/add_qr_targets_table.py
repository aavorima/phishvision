"""
Add QR code targets table to track who was sent QR posters
This enables proper reporting just like Email and SMS campaigns
"""
from app import app
from database import db

# SQL to create the qr_targets table
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS qr_targets (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL,
    name TEXT,
    email TEXT NOT NULL,
    department TEXT,
    tracking_token TEXT UNIQUE NOT NULL,
    sent_at DATETIME,
    scanned_at DATETIME,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (campaign_id) REFERENCES qrcode_campaigns (id) ON DELETE CASCADE
);
"""

with app.app_context():
    print("Creating qr_targets table...")

    # Execute the SQL
    db.session.execute(db.text(CREATE_TABLE_SQL))
    db.session.commit()

    # Create indexes separately
    db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_qr_targets_campaign ON qr_targets(campaign_id)"))
    db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_qr_targets_email ON qr_targets(email)"))
    db.session.execute(db.text("CREATE INDEX IF NOT EXISTS idx_qr_targets_token ON qr_targets(tracking_token)"))
    db.session.commit()

    print("[OK] qr_targets table created successfully!")
    print("\nThis table will track:")
    print("  - Who was sent QR code posters")
    print("  - Whether they scanned the QR code")
    print("  - When they scanned it")
    print("\nNow QR campaigns will have proper target tracking like Email and SMS!")
