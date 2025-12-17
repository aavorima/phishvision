"""
Migration script to add department column to campaign_targets and sms_targets tables
"""
from database import db
from sqlalchemy import text
from app import app

def add_department_columns():
    with app.app_context():
        try:
            # Add department column to campaign_targets
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE campaign_targets ADD COLUMN department VARCHAR(200)'))
                conn.commit()
            print('[OK] Added department column to campaign_targets')
        except Exception as e:
            if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                print('[OK] department column already exists in campaign_targets')
            else:
                print(f'Error adding department to campaign_targets: {e}')

        try:
            # Add department column to sms_targets
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE sms_targets ADD COLUMN department VARCHAR(200)'))
                conn.commit()
            print('[OK] Added department column to sms_targets')
        except Exception as e:
            if 'duplicate column name' in str(e).lower() or 'already exists' in str(e).lower():
                print('[OK] department column already exists in sms_targets')
            else:
                print(f'Error adding department to sms_targets: {e}')

        print('\n[OK] Migration completed successfully!')

if __name__ == '__main__':
    add_department_columns()
