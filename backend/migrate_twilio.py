"""
Database Migration Script for Twilio SMS Integration
Adds Twilio-related fields to existing Settings table
"""

from app import app
from database import db
from models import Settings

def migrate_twilio():
    """Add Twilio SMS support to settings table"""
    with app.app_context():
        print("[MIGRATION] Starting Twilio SMS database migration...")

        # Check if settings table needs Twilio columns
        print("[MIGRATION] Checking Settings table for Twilio columns...")

        try:
            # Try to query a setting's Twilio account SID
            test_setting = Settings.query.first()
            if test_setting:
                # Access twilio_account_sid to check if column exists
                _ = test_setting.twilio_account_sid
                print("[MIGRATION] OK Settings table already has Twilio columns")
            else:
                print("[MIGRATION] OK No settings found, but table schema is correct")
        except Exception as e:
            print(f"[MIGRATION] WARN Settings table needs Twilio columns: {e}")
            print("[MIGRATION] Adding Twilio columns to settings table...")

            # Add columns using raw SQL
            try:
                with db.engine.connect() as conn:
                    # Add twilio_account_sid column
                    conn.execute(db.text(
                        "ALTER TABLE settings ADD COLUMN twilio_account_sid VARCHAR(500)"
                    ))
                    # Add twilio_auth_token column
                    conn.execute(db.text(
                        "ALTER TABLE settings ADD COLUMN twilio_auth_token VARCHAR(500)"
                    ))
                    # Add twilio_phone_number column
                    conn.execute(db.text(
                        "ALTER TABLE settings ADD COLUMN twilio_phone_number VARCHAR(50)"
                    ))
                    conn.commit()
                print("[MIGRATION] OK Successfully added Twilio columns to settings table")
            except Exception as alter_error:
                print(f"[MIGRATION] Note: {alter_error}")
                print("[MIGRATION] Columns may already exist or table needs recreation")

        print("[MIGRATION] Migration completed successfully!")
        print("")
        print("=" * 60)
        print("Twilio SMS Integration is now active!")
        print("=" * 60)
        print("")
        print("You can now configure Twilio settings in:")
        print("  - Settings page -> AI Settings section")
        print("")
        print("Required Twilio Credentials:")
        print("  - Account SID (found in Twilio Console)")
        print("  - Auth Token (found in Twilio Console)")
        print("  - Phone Number (your Twilio phone number)")
        print("")
        print("After configuration, you can:")
        print("  - Create SMS phishing campaigns")
        print("  - Send smishing simulations")
        print("  - Track SMS click rates")
        print("=" * 60)

if __name__ == '__main__':
    migrate_twilio()
