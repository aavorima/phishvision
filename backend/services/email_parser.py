import re
from datetime import datetime

def parse_email_to_name(email):
    """
    Parse an email address to extract first name, last name, and full name.

    Examples:
    - john.doe@example.com -> John Doe
    - jane_smith@company.com -> Jane Smith
    - bob-johnson123@test.com -> Bob Johnson
    - alice.williams.phd@university.edu -> Alice Williams
    """
    try:
        # Extract local part (before @)
        local_part = email.split('@')[0].lower()

        # Remove common numbers and special chars
        local_part = re.sub(r'\d+', '', local_part)  # Remove numbers

        # Split by common separators (., _, -, etc.)
        parts = re.split(r'[._\-]+', local_part)

        # Filter out common prefixes/suffixes and short parts
        unwanted = ['mr', 'ms', 'mrs', 'dr', 'prof', 'jr', 'sr', 'phd', 'md', 'esq', 'admin', 'info', 'contact']
        parts = [p for p in parts if p and len(p) > 1 and p not in unwanted]

        # Capitalize each part
        capitalized_parts = [p.capitalize() for p in parts]

        # Determine first name, last name, full name
        if len(capitalized_parts) == 0:
            # Fallback to generic
            first_name = "User"
            last_name = ""
            full_name = "User"
        elif len(capitalized_parts) == 1:
            first_name = capitalized_parts[0]
            last_name = ""
            full_name = first_name
        else:
            first_name = capitalized_parts[0]
            last_name = capitalized_parts[-1]  # Last part as surname
            full_name = ' '.join(capitalized_parts)

        return {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': full_name,
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'current_time': datetime.now().strftime('%I:%M %p'),
            'current_year': datetime.now().year
        }
    except Exception as e:
        # Fallback on error
        return {
            'email': email,
            'first_name': 'User',
            'last_name': '',
            'full_name': 'User',
            'current_date': datetime.now().strftime('%B %d, %Y'),
            'current_time': datetime.now().strftime('%I:%M %p'),
            'current_year': datetime.now().year
        }

def substitute_template_variables(template_text, variables):
    """
    Substitute template variables with actual values.

    Supported variables:
    - {{first_name}} -> John
    - {{last_name}} -> Doe
    - {{full_name}} -> John Doe
    - {{email}} -> john.doe@example.com
    - {{current_date}} -> November 28, 2025
    - {{current_time}} -> 03:45 PM
    - {{current_year}} -> 2025
    - {{tracking_link}} -> (preserved for later substitution)
    """
    result = template_text

    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    return result

def get_available_variables():
    """Return list of available template variables"""
    return [
        {
            'name': '{{first_name}}',
            'description': 'Recipient\'s first name (parsed from email)',
            'example': 'John'
        },
        {
            'name': '{{last_name}}',
            'description': 'Recipient\'s last name (parsed from email)',
            'example': 'Doe'
        },
        {
            'name': '{{full_name}}',
            'description': 'Recipient\'s full name',
            'example': 'John Doe'
        },
        {
            'name': '{{email}}',
            'description': 'Recipient\'s email address',
            'example': 'john.doe@example.com'
        },
        {
            'name': '{{current_date}}',
            'description': 'Current date',
            'example': 'November 28, 2025'
        },
        {
            'name': '{{current_time}}',
            'description': 'Current time',
            'example': '03:45 PM'
        },
        {
            'name': '{{current_year}}',
            'description': 'Current year',
            'example': '2025'
        },
        {
            'name': '{{tracking_link}}',
            'description': 'Tracking link (automatically added by system)',
            'example': 'https://example.com/track/abc123'
        }
    ]
