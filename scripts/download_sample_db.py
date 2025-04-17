import os
import urllib.request
import sys

def download_chinook_db():
    """Download the Chinook sample database for testing SQL functionality"""
    db_url = "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip"
    zip_path = "chinook.zip"
    db_path = "chinook.db"
    
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"Database already exists at {db_path}")
        return
    
    try:
        print(f"Downloading sample database from {db_url}...")
        urllib.request.urlretrieve(db_url, zip_path)
        
        print("Extracting database...")
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        print(f"Cleaning up...")
        os.remove(zip_path)
        
        print(f"Sample database downloaded and extracted to {db_path}")
        print("You can now use this database with the SQL action")
    except Exception as e:
        print(f"Error downloading database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    download_chinook_db() 