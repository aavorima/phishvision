"""
Seed Employee Demo Data
Creates sample employees across different departments with varied HVS scores
"""

from app import app
from database import db
from models import Employee
from datetime import datetime, timedelta
import random

def seed_employees():
    """Create demo employee data"""
    with app.app_context():
        print("[SEED] Starting employee data seeding...")

        # Check if employees already exist
        existing_count = Employee.query.count()
        if existing_count > 0:
            print(f"[SEED] Found {existing_count} existing employees")
            response = input("Do you want to add more demo employees? (y/n): ")
            if response.lower() != 'y':
                print("[SEED] Cancelled")
                return

        # Demo employee data
        departments = {
            'IT': [
                {'first': 'John', 'last': 'Smith', 'title': 'Software Engineer', 'hvs': 15},
                {'first': 'Sarah', 'last': 'Johnson', 'title': 'DevOps Engineer', 'hvs': 8},
                {'first': 'Michael', 'last': 'Chen', 'title': 'System Administrator', 'hvs': 22},
                {'first': 'Emily', 'last': 'Davis', 'title': 'Frontend Developer', 'hvs': 35},
                {'first': 'David', 'last': 'Wilson', 'title': 'Security Analyst', 'hvs': 5},
            ],
            'HR': [
                {'first': 'Lisa', 'last': 'Anderson', 'title': 'HR Manager', 'hvs': 42},
                {'first': 'Robert', 'last': 'Taylor', 'title': 'Recruiter', 'hvs': 55},
                {'first': 'Jennifer', 'last': 'Brown', 'title': 'HR Specialist', 'hvs': 38},
                {'first': 'James', 'last': 'Miller', 'title': 'Training Coordinator', 'hvs': 28},
            ],
            'Finance': [
                {'first': 'William', 'last': 'Garcia', 'title': 'Financial Analyst', 'hvs': 65},
                {'first': 'Maria', 'last': 'Martinez', 'title': 'Accountant', 'hvs': 72},
                {'first': 'Thomas', 'last': 'Rodriguez', 'title': 'CFO', 'hvs': 18},
                {'first': 'Patricia', 'last': 'Lopez', 'title': 'Budget Manager', 'hvs': 48},
            ],
            'Sales': [
                {'first': 'Christopher', 'last': 'Lee', 'title': 'Sales Manager', 'hvs': 58},
                {'first': 'Nancy', 'last': 'Walker', 'title': 'Account Executive', 'hvs': 82},
                {'first': 'Daniel', 'last': 'Hall', 'title': 'Sales Representative', 'hvs': 75},
                {'first': 'Karen', 'last': 'Allen', 'title': 'Business Development', 'hvs': 68},
                {'first': 'Matthew', 'last': 'Young', 'title': 'Sales Associate', 'hvs': 88},
            ],
            'Marketing': [
                {'first': 'Jessica', 'last': 'King', 'title': 'Marketing Director', 'hvs': 32},
                {'first': 'Ryan', 'last': 'Wright', 'title': 'Content Manager', 'hvs': 45},
                {'first': 'Michelle', 'last': 'Scott', 'title': 'Social Media Manager', 'hvs': 52},
                {'first': 'Kevin', 'last': 'Green', 'title': 'SEO Specialist', 'hvs': 28},
            ],
            'Operations': [
                {'first': 'Brian', 'last': 'Adams', 'title': 'Operations Manager', 'hvs': 38},
                {'first': 'Amanda', 'last': 'Baker', 'title': 'Project Manager', 'hvs': 42},
                {'first': 'Steven', 'last': 'Nelson', 'title': 'Operations Analyst', 'hvs': 35},
            ],
            'Customer Support': [
                {'first': 'Laura', 'last': 'Carter', 'title': 'Support Manager', 'hvs': 48},
                {'first': 'Jason', 'last': 'Mitchell', 'title': 'Support Specialist', 'hvs': 62},
                {'first': 'Ashley', 'last': 'Perez', 'title': 'Customer Success', 'hvs': 55},
                {'first': 'Joshua', 'last': 'Roberts', 'title': 'Technical Support', 'hvs': 38},
            ],
            'Executive': [
                {'first': 'Richard', 'last': 'Turner', 'title': 'CEO', 'hvs': 12},
                {'first': 'Elizabeth', 'last': 'Phillips', 'title': 'COO', 'hvs': 20},
                {'first': 'Charles', 'last': 'Campbell', 'title': 'CTO', 'hvs': 8},
            ]
        }

        # Age groups and job levels
        age_groups = ['18-25', '26-35', '36-45', '46-55', '56+']
        job_levels = ['entry', 'mid', 'senior', 'manager', 'executive']

        created_count = 0
        for department, employees in departments.items():
            for emp_data in employees:
                # Create email
                email = f"{emp_data['first'].lower()}.{emp_data['last'].lower()}@company.com"

                # Check if employee already exists
                existing = Employee.query.filter_by(email=email).first()
                if existing:
                    print(f"[SEED] WARN Employee {email} already exists, skipping...")
                    continue

                # Random hire date (1-5 years ago)
                days_ago = random.randint(365, 1825)
                hire_date = datetime.utcnow() - timedelta(days=days_ago)

                # Determine job level based on title
                title = emp_data['title'].lower()
                if 'ceo' in title or 'cto' in title or 'cfo' in title or 'coo' in title:
                    level = 'executive'
                elif 'manager' in title or 'director' in title:
                    level = 'manager'
                elif 'senior' in title or 'lead' in title:
                    level = 'senior'
                elif 'specialist' in title or 'analyst' in title or 'engineer' in title:
                    level = 'mid'
                else:
                    level = 'entry'

                # Create employee
                employee = Employee(
                    email=email,
                    first_name=emp_data['first'],
                    last_name=emp_data['last'],
                    department=department,
                    job_title=emp_data['title'],
                    phone=f"+1{random.randint(2000000000, 9999999999)}",
                    employee_id=f"EMP{1000 + created_count}",
                    is_active=True,
                    age_group=random.choice(age_groups),
                    hire_date=hire_date,
                    job_level=level,
                    previous_training=random.choice([True, False]),
                    hvs_score=emp_data['hvs'],
                    hvs_last_updated=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )

                # Calculate tenure
                employee.calculate_tenure()

                db.session.add(employee)
                created_count += 1
                print(f"[SEED] OK Created: {employee.first_name} {employee.last_name} ({department}) - HVS: {employee.hvs_score}")

        db.session.commit()

        print("")
        print("=" * 60)
        print(f"[SEED] Successfully created {created_count} employees!")
        print("=" * 60)
        print("")

        # Show summary statistics
        print("Department Summary:")
        print("-" * 60)
        for dept in sorted(departments.keys()):
            dept_employees = Employee.query.filter_by(department=dept, is_active=True).all()
            if dept_employees:
                avg_hvs = sum(e.hvs_score for e in dept_employees) / len(dept_employees)
                print(f"  {dept:20s} {len(dept_employees):2d} employees  Avg HVS: {avg_hvs:5.1f}")

        print("")
        print("HVS Level Distribution:")
        print("-" * 60)
        all_employees = Employee.query.filter_by(is_active=True).all()
        levels = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        for emp in all_employees:
            levels[emp.get_hvs_level()] += 1

        print(f"  Low (0-24):      {levels['low']:3d} employees")
        print(f"  Medium (25-49):  {levels['medium']:3d} employees")
        print(f"  High (50-74):    {levels['high']:3d} employees")
        print(f"  Critical (75+):  {levels['critical']:3d} employees")

        print("")
        print("Top 5 Highest Risk Employees:")
        print("-" * 60)
        high_risk = sorted(all_employees, key=lambda e: e.hvs_score, reverse=True)[:5]
        for i, emp in enumerate(high_risk, 1):
            print(f"  {i}. {emp.first_name} {emp.last_name:15s} {emp.department:15s} HVS: {emp.hvs_score:3d}")

        print("")
        print("=" * 60)
        print("Demo data ready! Test the HVS API:")
        print("  curl http://localhost:5000/api/hvs/stats")
        print("  curl http://localhost:5000/api/hvs/departments")
        print("  curl http://localhost:5000/api/hvs/employees")
        print("=" * 60)


if __name__ == '__main__':
    seed_employees()
