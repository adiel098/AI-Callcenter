"""
Script to fix all backend. imports to relative imports
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace backend.X imports with X imports
    patterns = [
        (r'from backend\.config import', 'from config import'),
        (r'from backend\.database import', 'from database import'),
        (r'from backend\.models import', 'from models import'),
        (r'from backend\.services import', 'from services import'),
        (r'from backend\.services\.', 'from services.'),
        (r'from backend\.workers import', 'from workers import'),
        (r'from backend\.workers\.', 'from workers.'),
        (r'from backend\.utils import', 'from utils import'),
        (r'from backend\.utils\.', 'from utils.'),
        (r'from backend\.api\.routes import', 'from api.routes import'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """Fix all Python files in backend directory"""
    backend_dir = Path(__file__).parent / 'backend'

    count = 0
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                if fix_imports_in_file(file_path):
                    print(f"Fixed: {file_path}")
                    count += 1

    print(f"\nTotal files fixed: {count}")

if __name__ == '__main__':
    main()
