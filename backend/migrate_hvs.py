"""
Database Migration Script for Human Vulnerability Score (HVS)
Adds HVS-related fields to existing Employee table and creates HVSEvent table
"""

from app import app
from database import db
from models import Employee, HVSEvent

def migrate_hvs():
    """Add HVS support to database"""
    with app.app_context():
        print("[MIGRATION] Starting HVS database migration...")

        # Create all tables (this will create HVSEvent table)
        print("[MIGRATION] Creating HVSEvent table...")
        db.create_all()

        # Check if employees table needs HVS columns
        print("[MIGRATION] Checking Employee table for HVS columns...")

        try:
            # Try to query an employee's HVS score
            test_employee = Employee.query.first()
            if test_employee:
                # Access hvs_score to check if column exists
                _ = test_employee.hvs_score
                print("[MIGRATION] OK Employee table already has HVS columns")
            else:
                print("[MIGRATION] OK No employees found, but table schema is correct")
        except Exception as e:
            print(f"[MIGRATION] WARN Employee table needs HVS columns: {e}")
            print("[MIGRATION] Adding HVS columns to employees table...")

            # Add columns using raw SQL
            try:
                with db.engine.connect() as conn:
                    # Add hvs_score column
                    conn.execute(db.text(
                        "ALTER TABLE employees ADD COLUMN hvs_score INTEGER DEFAULT 0"
                    ))
                    # Add hvs_last_updated column
                    conn.execute(db.text(
                        "ALTER TABLE employees ADD COLUMN hvs_last_updated DATETIME"
                    ))
                    conn.commit()
                print("[MIGRATION] OK Successfully added HVS columns to employees table")
            except Exception as alter_error:
                print(f"[MIGRATION] Note: {alter_error}")
                print("[MIGRATION] Columns may already exist or table needs recreation")

        # Initialize HVS scores for all employees (set to 0 if NULL)
        print("[MIGRATION] Initializing HVS scores for existing employees...")
        employees = Employee.query.all()
        updated_count = 0
        for emp in employees:
            if emp.hvs_score is None:
                emp.hvs_score = 0
                updated_count += 1

        if updated_count > 0:
            db.session.commit()
            print(f"[MIGRATION] OK Initialized HVS scores for {updated_count} employees")
        else:
            print("[MIGRATION] OK All employees already have HVS scores")

        print("[MIGRATION] Migration completed successfully!")
        print("")
        print("=" * 60)
        print("HVS System is now active!")
        print("=" * 60)
        print("")
        print("New API Endpoints:")
        print("  - GET  /api/hvs/employees              - List all employee HVS scores")
        print("  - GET  /api/hvs/employees/<id>         - Get employee HVS detail")
        print("  - GET  /api/hvs/employees/<id>/events  - Get HVS event history")
        print("  - POST /api/hvs/employees/<id>/manual-update - Manually update HVS")
        print("  - GET  /api/hvs/departments            - Department HVS averages")
        print("  - GET  /api/hvs/departments/<name>     - Department HVS detail")
        print("  - GET  /api/hvs/stats                  - Overall HVS statistics")
        print("  - GET  /api/hvs/events/recent          - Recent HVS events")
        print("")
        print("HVS Score Changes:")
        print("  - Clicked phishing link:      +25 points")
        print("  - Submitted credentials:      +40 points")
        print("  - Clicked SMS link:           +20 points")
        print("  - Opened email only:          +5 points")
        print("  - Watched training video:     -15 points")
        print("  - Reported phishing correctly:-25 points")
        print("")
        print("HVS Levels:")
        print("  - Low:      0-24  (Green)")
        print("  - Medium:   25-49 (Yellow)")
        print("  - High:     50-74 (Orange)")
        print("  - Critical: 75-100 (Red)")
        print("=" * 60)

if __name__ == '__main__':
    migrate_hvs()
