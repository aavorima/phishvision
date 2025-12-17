"""
Fix scheduled_campaigns table - add missing scenario_id column
"""
from database import db
from app import app
import sqlite3

with app.app_context():
    # Get database path
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

    print(f"Fixing scheduled_campaigns table in: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(scheduled_campaigns)")
    columns = [row[1] for row in cursor.fetchall()]

    if 'scenario_id' not in columns:
        print("Adding scenario_id column...")
        cursor.execute("""
            ALTER TABLE scheduled_campaigns
            ADD COLUMN scenario_id VARCHAR(36)
        """)
        print("✓ scenario_id column added")
    else:
        print("✓ scenario_id column already exists")

    conn.commit()
    conn.close()

    print("\n✓ Database schema fixed successfully!")
