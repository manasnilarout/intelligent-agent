# Action Analyzer

This project uses LangChain and OpenAI to analyze questions and determine which actions should be taken from a predefined set of available actions.

## Available Actions

1. SQL Operations: Execute SQL queries and natural language queries on a database using LangChain's SQL agent
   - Supports both SQLite and PostgreSQL databases
   - Includes PostgreSQL-specific query features
   - Full agent mode support for complex database questions
2. CSV Operations: Analyze CSV data using LangChain's CSV agent
3. Web Operations: Connect to the internet and browse for data

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or regenerate the requirements file based on the actual imports used:
   ```bash
   ./generate_requirements.sh
   pip install -r requirements.txt
   ```

4. Download the sample database (optional - for SQLite testing):
   ```bash
   python scripts/download_sample_db.py
   ```
5. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   
   # Database connection settings (uncomment/modify as needed)
   # POSTGRES_CONNECTION=postgres://username:password@hostname:port/database
   # SQLITE_CONNECTION=sqlite:///path/to/local/database.db
   # DB_CONNECTION_STRING=postgres://username:password@hostname:port/database
   
   # Default CSV path
   # DEFAULT_CSV_PATH=data/sample.csv
   ```

## Usage

Run the main script:
```bash
python run.py
```

The script will prompt you to enter a question. Based on your question, it will analyze and determine which actions need to be taken from the available set of actions.

### SQL Agent Features

The SQL action uses LangChain's SQL agent, which can:
- Answer natural language questions about database contents
- Generate and execute SQL queries based on your questions
- List tables and describe schemas when requested
- Handle complex SQL operations through agent-based reasoning

#### PostgreSQL-Specific Features

For PostgreSQL databases, the following additional operations are available:

**Direct Mode Operations:**
- List all tables in the database: "List all PostgreSQL tables"
- Show all schemas: "Show all PostgreSQL schemas"
- List database functions: "List all PostgreSQL functions"
- Show database users: "List all PostgreSQL users"
- Get table sizes: "Show the size of PostgreSQL tables"

**Agent Mode Support:**
- Complex analytical queries about PostgreSQL database structure
- Natural language questions about database contents and relationships
- Multi-step reasoning to answer complex questions about database design
- Automatic translation of natural language to PostgreSQL-specific syntax
- Examples:
  - "What tables in PostgreSQL have foreign key relationships?"
  - "Tell me about the structure of the database"
  - "Analyze the schema of table X"
  - "What columns in table Y are indexed?"

### CSV Agent Features

The CSV action uses LangChain's CSV agent, which can:
- Answer questions about data in CSV files
- Perform data analysis, filtering, and calculations
- Generate insights and statistics from CSV data
- Work with any CSV file specified in the question

### Example Queries

SQL Database Examples:
- "What are the top 3 best-selling artists?" (SQLite - Chinook)
- "List all tables in the database" (works with both SQLite and PostgreSQL)
- "What tables are available in the PostgreSQL database?" (PostgreSQL)
- "Show all PostgreSQL tables" (PostgreSQL-specific)
- "List all PostgreSQL functions" (PostgreSQL-specific)

CSV Data Examples:
- "What is the average salary in the sample.csv file?"
- "Who has the highest salary in the data?"
- "Count how many people are in each occupation"

## Project Structure

```
.
├── src/
│   ├── actions/
│   │   ├── base_action.py
│   │   ├── csv_action.py
│   │   ├── web_action.py
│   │   └── sql_action.py
│   ├── config/
│   │   └── config.py
│   ├── utils/
│   │   └── action_analyzer.py
│   └── main.py
├── scripts/
│   ├── download_sample_db.py
│   └── generate_requirements.py
├── data/
│   ├── sample.csv
│   ├── sales.csv
│   └── customer_reviews.csv
├── tests/
├── requirements.txt
├── generate_requirements.sh
├── run.py
└── README.md
```

## Development

### Generating Requirements

The project includes a script to programmatically generate the requirements.txt file based on the actual imports used in the code:

```bash
./generate_requirements.sh
```

This will:
1. Scan all Python files in the project
2. Identify imported packages
3. Map import names to package names
4. Check installed versions
5. Generate a requirements.txt file with pinned versions

This ensures that the requirements file stays up-to-date with the actual code dependencies.

### Database Configuration

By default, the system is configured to use the provided PostgreSQL database. You can change this by setting the appropriate environment variables in your `.env` file:

```
# Use SQLite instead of PostgreSQL
DB_CONNECTION_STRING=sqlite:///chinook.db
```

## Examples

Input:
```
What is the average invoice total by country?
```

The system might determine that it needs to:
1. Execute SQL queries on the database (using agent mode)

Input:
```
Tell me about the tables in the PostgreSQL database
```

The system will use agent mode to analyze and describe the tables in detail.

Input:
```
Show all PostgreSQL tables
```

The system will use direct mode to list all tables in the PostgreSQL database.

Input:
```
What relationships exist between tables in the PostgreSQL database?
```

The system will use agent mode to analyze table relationships and provide detailed information.

Input:
```
What is the average salary in the sample.csv file?
```

The system might determine that it needs to:
1. Read a CSV file and extract data 