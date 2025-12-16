from flask import Blueprint, request, jsonify, session
from database import db
from models import CustomTemplate, Settings, User
from datetime import datetime
from services.ai_template_generator import AITemplateGenerator
import os

bp = Blueprint('templates', __name__, url_prefix='/api/templates')

def get_ai_generator():
    """Get AI generator with user's API key from settings, or fall back to .env"""
    user_id = session.get('user_id')
    api_key = None

    print(f"[DEBUG] get_ai_generator - user_id from session: {user_id}")

    if user_id:
        settings = Settings.query.filter_by(user_id=user_id).first()
        if settings and settings.gemini_api_key:
            api_key = settings.gemini_api_key
            print(f"[DEBUG] Found API key from user settings (length: {len(api_key)})")
        else:
            print(f"[DEBUG] No API key in user settings")
    else:
        # Fallback: try to get any configured API key from settings table
        settings = Settings.query.filter(Settings.gemini_api_key.isnot(None)).first()
        if settings and settings.gemini_api_key:
            api_key = settings.gemini_api_key
            print(f"[DEBUG] Using API key from first available settings (length: {len(api_key)})")

    if not api_key:
        print(f"[DEBUG] No API key found, will use .env or fallback")

    return AITemplateGenerator(api_key=api_key)

@bp.route('', methods=['GET'])
def get_templates():
    """Get all templates"""
    try:
        category = request.args.get('category')

        if category:
            templates = CustomTemplate.query.filter_by(category=category, is_active=True).all()
        else:
            templates = CustomTemplate.query.filter_by(is_active=True).all()

        return jsonify([t.to_dict() for t in templates]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>', methods=['GET'])
def get_template(template_id):
    """Get a specific template"""
    try:
        template = CustomTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        return jsonify(template.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('', methods=['POST'])
def create_template():
    """Create a new template"""
    try:
        data = request.json

        # Validate required fields
        if not data.get('name') or not data.get('subject') or not data.get('html_content'):
            return jsonify({'error': 'Name, subject, and html_content are required'}), 400

        template = CustomTemplate(
            name=data['name'],
            category=data.get('category', 'general'),
            subject=data['subject'],
            html_content=data['html_content'],
            from_name=data.get('from_name', ''),
            difficulty=data.get('difficulty', 'medium'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

        db.session.add(template)
        db.session.commit()

        return jsonify(template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>', methods=['PUT'])
def update_template(template_id):
    """Update a template"""
    try:
        template = CustomTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        data = request.json

        # Update fields
        if 'name' in data:
            template.name = data['name']
        if 'category' in data:
            template.category = data['category']
        if 'subject' in data:
            template.subject = data['subject']
        if 'html_content' in data:
            template.html_content = data['html_content']
        if 'from_name' in data:
            template.from_name = data['from_name']
        if 'difficulty' in data:
            template.difficulty = data['difficulty']
        if 'description' in data:
            template.description = data['description']
        if 'is_active' in data:
            template.is_active = data['is_active']

        template.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify(template.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>', methods=['DELETE'])
def delete_template(template_id):
    """Delete a template (soft delete)"""
    try:
        template = CustomTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        # Prevent deletion of built-in templates
        if template.is_builtin:
            return jsonify({'error': 'Cannot delete built-in templates. You can duplicate and modify them instead.'}), 403

        # Soft delete by setting is_active to False
        template.is_active = False
        db.session.commit()

        return jsonify({'message': 'Template deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>/preview', methods=['POST'])
def preview_template(template_id):
    """Preview a template with sample data"""
    try:
        template = CustomTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        data = request.json
        sample_email = data.get('email', 'john.doe@example.com')

        # Import the parser
        from services.email_parser import parse_email_to_name, substitute_template_variables

        # Parse name from email
        parsed_data = parse_email_to_name(sample_email)

        # Substitute variables
        preview_subject = substitute_template_variables(template.subject, parsed_data)
        preview_content = substitute_template_variables(template.html_content, parsed_data)

        return jsonify({
            'subject': preview_subject,
            'html_content': preview_content,
            'parsed_data': parsed_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>/duplicate', methods=['POST'])
def duplicate_template(template_id):
    """Duplicate a template (useful for creating variations of built-in templates)"""
    try:
        original = CustomTemplate.query.get(template_id)
        if not original:
            return jsonify({'error': 'Template not found'}), 404

        data = request.json or {}

        # Create a copy with a new name
        new_template = CustomTemplate(
            name=data.get('name', f"{original.name} (Copy)"),
            category=original.category,
            subject=original.subject,
            html_content=original.html_content,
            from_name=original.from_name,
            difficulty=original.difficulty,
            description=original.description,
            language=original.language,
            is_builtin=False,  # Duplicated templates are not built-in
            is_active=True
        )

        db.session.add(new_template)
        db.session.commit()

        return jsonify(new_template.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/generate-ai', methods=['POST'])
def generate_ai_template():
    """Generate a template using AI (Gemini)"""
    try:
        data = request.json

        # Required field
        if not data.get('description'):
            return jsonify({'error': 'Description is required'}), 400

        # Optional fields
        category = data.get('category', 'IT')
        difficulty = data.get('difficulty', 'medium')
        company_name = data.get('company_name', '')

        # Generate template using AI (get fresh generator with user's API key)
        ai_generator = get_ai_generator()
        template_data = ai_generator.generate_template(
            description=data['description'],
            category=category,
            difficulty=difficulty,
            company_name=company_name
        )

        return jsonify(template_data), 200
    except Exception as e:
        print(f"Error in AI generation: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<template_id>/improve-ai', methods=['POST'])
def improve_template_ai(template_id):
    """Improve an existing template using AI"""
    try:
        template = CustomTemplate.query.get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        data = request.json
        improvement_notes = data.get('notes', 'Make it more professional and convincing')

        ai_generator = get_ai_generator()
        improved = ai_generator.improve_template(
            current_subject=template.subject,
            current_html=template.html_content,
            improvement_notes=improvement_notes
        )

        return jsonify(improved), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
