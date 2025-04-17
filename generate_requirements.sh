#!/bin/bash
# Script to generate requirements.txt programmatically

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Create a backup of the existing requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    echo "Backing up existing requirements.txt to requirements.txt.bak"
    cp requirements.txt requirements.txt.bak
fi

# Run the generator script
echo "Running requirements generator..."
python3 scripts/generate_requirements.py

# Check if requirements.txt was created successfully
if [ $? -eq 0 ] && [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt was generated successfully!"
    echo "You can install the requirements with: pip install -r requirements.txt"
else
    echo "❌ Failed to generate requirements.txt"
    
    # Restore backup if available
    if [ -f "requirements.txt.bak" ]; then
        echo "Restoring requirements.txt from backup"
        cp requirements.txt.bak requirements.txt
    fi
    
    exit 1
fi 