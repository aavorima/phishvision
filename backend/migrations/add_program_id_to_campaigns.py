"""
Migration: Add program_id to campaigns, sms_campaigns, and qrcode_campaigns tables

This migration adds foreign key columns to link campaigns to their originating profiling programs.
"""
import sqlite3
import os

def migrate():
    """Add program_id columns to campaign tables"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'phishvision.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(campaigns)")
        campaigns_columns = [col[1] for col in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(sms_campaigns)")
        sms_columns = [col[1] for col in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(qrcode_campaigns)")
        qr_columns = [col[1] for col in cursor.fetchall()]

        # Add program_id to campaigns table if not exists
        if 'program_id' not in campaigns_columns:
            print("Adding program_id to campaigns table...")
            cursor.execute("""
                ALTER TABLE campaigns
                ADD COLUMN program_id VARCHAR(36)
                REFERENCES campaign_programs(id)
            """)
            print("[OK] Added program_id to campaigns")
        else:
            print("[OK] program_id already exists in campaigns")

        # Add program_id to sms_campaigns table if not exists
        if 'program_id' not in sms_columns:
            print("Adding program_id to sms_campaigns table...")
            cursor.execute("""
                ALTER TABLE sms_campaigns
                ADD COLUMN program_id VARCHAR(36)
                REFERENCES campaign_programs(id)
            """)
            print("[OK] Added program_id to sms_campaigns")
        else:
            print("[OK] program_id already exists in sms_campaigns")

        # Add program_id to qrcode_campaigns table if not exists
        if 'program_id' not in qr_columns:
            print("Adding program_id to qrcode_campaigns table...")
            cursor.execute("""
                ALTER TABLE qrcode_campaigns
                ADD COLUMN program_id VARCHAR(36)
                REFERENCES campaign_programs(id)
            """)
            print("[OK] Added program_id to qrcode_campaigns")
        else:
            print("[OK] program_id already exists in qrcode_campaigns")

        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
