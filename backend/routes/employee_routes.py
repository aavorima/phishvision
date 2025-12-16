from flask import Blueprint, request, jsonify
from models import Employee
from database import db
import json

bp = Blueprint('employees', __name__, url_prefix='/api/employees')


@bp.route('/', methods=['GET'])
def get_employees():
    """Get all employees with optional filtering"""
    department = request.args.get('department')
    is_active = request.args.get('is_active')
    search = request.args.get('search')

    query = Employee.query

    if department:
        query = query.filter(Employee.department == department)

    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        query = query.filter(Employee.is_active == is_active_bool)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Employee.email.ilike(search_term),
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.job_title.ilike(search_term)
            )
        )

    employees = query.order_by(Employee.last_name, Employee.first_name).all()
    return jsonify([e.to_dict() for e in employees])


@bp.route('/<employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Get a single employee by ID"""
    employee = Employee.query.get_or_404(employee_id)
    return jsonify(employee.to_dict())


@bp.route('/', methods=['POST'])
def create_employee():
    """Create a new employee"""
    data = request.json

    # Check required fields
    if not data.get('email') or not data.get('first_name') or not data.get('last_name'):
        return jsonify({'error': 'Email, first name, and last name are required'}), 400

    # Check if email already exists
    existing = Employee.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({'error': 'An employee with this email already exists'}), 409

    employee = Employee(
        email=data['email'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        department=data.get('department'),
        job_title=data.get('job_title'),
        phone=data.get('phone'),
        manager_email=data.get('manager_email'),
        employee_id=data.get('employee_id'),
        is_active=data.get('is_active', True),
        tags=json.dumps(data.get('tags', [])) if data.get('tags') else None,
        notes=data.get('notes')
    )

    db.session.add(employee)
    db.session.commit()

    return jsonify(employee.to_dict()), 201


@bp.route('/bulk', methods=['POST'])
def create_employees_bulk():
    """Create multiple employees at once (from CSV import)"""
    data = request.json
    employees_data = data.get('employees', [])

    if not employees_data:
        return jsonify({'error': 'No employees data provided'}), 400

    created = []
    errors = []
    skipped = []

    for emp_data in employees_data:
        # Validate required fields
        if not emp_data.get('email') or not emp_data.get('first_name') or not emp_data.get('last_name'):
            errors.append({'data': emp_data, 'error': 'Missing required fields'})
            continue

        # Check if email already exists
        existing = Employee.query.filter_by(email=emp_data['email']).first()
        if existing:
            skipped.append({'email': emp_data['email'], 'reason': 'Already exists'})
            continue

        try:
            employee = Employee(
                email=emp_data['email'],
                first_name=emp_data['first_name'],
                last_name=emp_data['last_name'],
                department=emp_data.get('department'),
                job_title=emp_data.get('job_title'),
                phone=emp_data.get('phone'),
                manager_email=emp_data.get('manager_email'),
                employee_id=emp_data.get('employee_id'),
                is_active=emp_data.get('is_active', True),
                tags=json.dumps(emp_data.get('tags', [])) if emp_data.get('tags') else None,
                notes=emp_data.get('notes')
            )
            db.session.add(employee)
            created.append(emp_data['email'])
        except Exception as e:
            errors.append({'data': emp_data, 'error': str(e)})

    db.session.commit()

    return jsonify({
        'created': len(created),
        'skipped': len(skipped),
        'errors': len(errors),
        'details': {
            'created_emails': created,
            'skipped': skipped,
            'errors': errors
        }
    })


@bp.route('/<employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Update an existing employee"""
    employee = Employee.query.get_or_404(employee_id)
    data = request.json

    # Update fields if provided
    if 'email' in data:
        # Check if new email already exists
        if data['email'] != employee.email:
            existing = Employee.query.filter_by(email=data['email']).first()
            if existing:
                return jsonify({'error': 'An employee with this email already exists'}), 409
        employee.email = data['email']

    if 'first_name' in data:
        employee.first_name = data['first_name']
    if 'last_name' in data:
        employee.last_name = data['last_name']
    if 'department' in data:
        employee.department = data['department']
    if 'job_title' in data:
        employee.job_title = data['job_title']
    if 'phone' in data:
        employee.phone = data['phone']
    if 'manager_email' in data:
        employee.manager_email = data['manager_email']
    if 'employee_id' in data:
        employee.employee_id = data['employee_id']
    if 'is_active' in data:
        employee.is_active = data['is_active']
    if 'tags' in data:
        employee.tags = json.dumps(data['tags']) if data['tags'] else None
    if 'notes' in data:
        employee.notes = data['notes']

    db.session.commit()
    return jsonify(employee.to_dict())


@bp.route('/<employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Delete an employee"""
    employee = Employee.query.get_or_404(employee_id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employee deleted successfully'})


@bp.route('/departments', methods=['GET'])
def get_departments():
    """Get list of unique departments"""
    departments = db.session.query(Employee.department).filter(
        Employee.department.isnot(None),
        Employee.department != ''
    ).distinct().all()

    return jsonify([d[0] for d in departments if d[0]])


@bp.route('/stats', methods=['GET'])
def get_employee_stats():
    """Get employee statistics"""
    total = Employee.query.count()
    active = Employee.query.filter_by(is_active=True).count()
    inactive = Employee.query.filter_by(is_active=False).count()

    # Department breakdown
    dept_stats = db.session.query(
        Employee.department,
        db.func.count(Employee.id)
    ).filter(
        Employee.department.isnot(None)
    ).group_by(Employee.department).all()

    return jsonify({
        'total': total,
        'active': active,
        'inactive': inactive,
        'by_department': {d[0]: d[1] for d in dept_stats if d[0]}
    })
