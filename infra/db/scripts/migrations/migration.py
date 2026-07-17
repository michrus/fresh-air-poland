"""Module defining Migration class."""

import re


class Migration:
    """Migration descriptor."""

    MIGRATION_NAME_PATTERN = r'([0-9]+)_(\w+).sql'

    def __init__(self, full_name):
        self.full_name = full_name
        m = re.match(self.MIGRATION_NAME_PATTERN, self.full_name)
        if m:
            self.number = int(m.group(1))
            self.name = m.group(2)
        else:
            self.number = None
            self.name = None

    def __bool__(self):
        return bool(self.number and self.name)

    def __eq__(self, value):
        if isinstance(value, Migration):
            return self.full_name == value.full_name
        else:
            return False

    def __hash__(self):
        return hash(self.full_name)

    def __str__(self):
        return self.full_name
