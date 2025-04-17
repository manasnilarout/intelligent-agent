from decouple import config

OPENAI_API_KEY = config('OPENAI_API_KEY')

# Database connection settings
# Default to PostgreSQL connection if available, otherwise use SQLite
POSTGRES_CONNECTION = config('POSTGRES_CONNECTION', default='postgresql://reader:NWDMCE5xdipIjRrp@hh-pgsql-public.ebi.ac.uk:5432/pfmegrnargs')
SQLITE_CONNECTION = config('SQLITE_CONNECTION', default='sqlite:///chinook.db')

# Use PostgreSQL by default, but allow fallback to SQLite
DB_CONNECTION_STRING = config('DB_CONNECTION_STRING', default=SQLITE_CONNECTION)

DEFAULT_CSV_PATH = config('DEFAULT_CSV_PATH', default='data/sample.csv') 