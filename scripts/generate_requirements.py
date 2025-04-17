#!/usr/bin/env python3
"""
Script to programmatically generate requirements.txt by scanning
the project for imports and mapping them to their package names.
"""

import os
import re
import sys
import subprocess
from collections import defaultdict

# Mapping of import names to package names (when they differ)
IMPORT_TO_PACKAGE = {
    'dotenv': 'python-dotenv',
    'decouple': 'python-decouple',
    'openai': 'openai',
    'pandas': 'pandas',
    'sqlalchemy': 'sqlalchemy',
    're': None,  # Standard library
    'os': None,  # Standard library
    'sys': None,  # Standard library
    'json': None,  # Standard library
    'typing': None,  # Standard library
    'collections': None,  # Standard library
    'abc': None,  # Standard library
    'glob': None,  # Standard library
    'datetime': None,  # Standard library
    'requests': 'requests',
    'langchain': 'langchain',
    'langchain_openai': 'langchain-openai',
    'langchain_community': 'langchain-community',
    'langchain_experimental': 'langchain-experimental',
}

# Search directories
SEARCH_DIRS = ['src', 'scripts']

def find_python_files(directory):
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def extract_imports(file_path):
    """Extract imports from a Python file."""
    imports = set()
    with open(file_path, 'r') as file:
        content = file.read()
        
        # Match import statements
        import_patterns = [
            r'^\s*import\s+(\w+)',  # import package
            r'^\s*from\s+(\w+)\s+import',  # from package import ...
            r'^\s*from\s+(\w+)\.[\w\.]+\s+import',  # from package.module import ...
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                imports.add(match.group(1))
                
    return imports

def get_package_version(package_name):
    """Get the installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
        return None
    except Exception as e:
        print(f"Error getting version for {package_name}: {e}")
        return None

def generate_requirements():
    """Generate requirements.txt by scanning for imports."""
    all_imports = set()
    
    # Find all Python files in the search directories
    for directory in SEARCH_DIRS:
        if os.path.exists(directory):
            for file_path in find_python_files(directory):
                imports = extract_imports(file_path)
                all_imports.update(imports)
    
    # Map imports to package names and get versions
    packages = {}
    for import_name in all_imports:
        if import_name in IMPORT_TO_PACKAGE:
            package_name = IMPORT_TO_PACKAGE[import_name]
            if package_name:  # Only process non-None packages (not stdlib)
                version = get_package_version(package_name)
                if version:
                    packages[package_name] = version
    
    # Sort packages by name
    sorted_packages = sorted(packages.items())
    
    # Create or update requirements.txt
    with open('requirements.txt', 'w') as req_file:
        for package, version in sorted_packages:
            req_file.write(f"{package}=={version}\n")
        
    print(f"Generated requirements.txt with {len(sorted_packages)} packages")
    return sorted_packages

if __name__ == "__main__":
    generate_requirements() 