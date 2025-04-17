import os
import sys

# Check if the chinook.db exists
if not os.path.exists('chinook.db'):
    print("Sample database not found. Would you like to download it? (y/n)")
    response = input().strip().lower()
    if response == 'y':
        # Import and run the download script
        sys.path.append('scripts')
        from scripts.download_sample_db import download_chinook_db
        download_chinook_db()
    else:
        print("Note: SQL operations will fail without a database.")

# Run the main application
from src.main import main

if __name__ == "__main__":
    main()
