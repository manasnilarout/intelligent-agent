from decouple import config

OPENAI_API_KEY = config('OPENAI_API_KEY')
DB_CONNECTION_STRING = config('DB_CONNECTION_STRING', default='sqlite:///chinook.db')
DEFAULT_CSV_PATH = config('DEFAULT_CSV_PATH', default='data/data.csv') 