import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if not username:
        raise ValidationError('Username must be provided.')
    if len(username) < 4:
        raise ValidationError('Username must be at least 4 characters long.')
    if len(username) > 20:
        raise ValidationError('Username cannot exceed 20 characters in length.')
    if username != username.lower():
        raise ValidationError('Username must be in lowercase.')
    if not username[0].isalpha():
        raise ValidationError('Username must start with a letter.')
    if not (username[-1].isalpha() or username[-1].isdigit()):
        raise ValidationError('Username must end with a letter or a digit.')
    if '--' in username:
        raise ValidationError('Username cannot contain consecutive underscores.')
    if not re.match(r'^[a-zA-Z]+[a-zA-Z0-9\-]+[a-zA-Z0-9]+$', username):
        raise ValidationError('Username can only contain letters, hyphens, and digits.')
