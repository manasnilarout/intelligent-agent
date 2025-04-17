from .utils.action_analyzer import ActionAnalyzer
from .actions.sql_action import SQLDatabaseAction
import re
import os

def parse_sql_query(question):
    """Parse the question to extract SQL-related parameters"""
    
    # Check if the question is asking about PostgreSQL but should use agent mode
    if "postgresql" in question.lower() or "postgres" in question.lower():
        # Complex PostgreSQL questions should use agent mode
        if any(phrase in question.lower() for phrase in [
            "tell me about", "analyze", "what is", "how many", "show me", 
            "compare", "find", "calculate", "which", "where", "who", "when",
            "statistics", "summary", "report", "aggregate"
        ]):
            return {"query": question, "agent_mode": True}
    
    # Check for PostgreSQL info queries that should use direct mode
    postgres_info_patterns = {
        "tables": [r"list (all )?postgres(ql)? tables", r"show (all )?postgres(ql)? tables"],
        "schemas": [r"list (all )?postgres(ql)? schemas", r"show (all )?postgres(ql)? schemas"],
        "functions": [r"list (all )?postgres(ql)? functions", r"show (all )?postgres(ql)? functions"],
        "users": [r"list (all )?postgres(ql)? users", r"show (all )?postgres(ql)? users"],
        "size": [r"(show|list|get) (the )?size of postgres(ql)? tables", r"postgres(ql)? table sizes"]
    }
    
    for info_type, patterns in postgres_info_patterns.items():
        for pattern in patterns:
            if re.search(pattern, question.lower()):
                return {"postgres_info": info_type, "agent_mode": False}
    
    # Example patterns to look for in questions
    list_tables_patterns = [
        r"what tables (are available|do we have)",
        r"list (all )?tables",
        r"show (me )?(all )?tables"
    ]
    
    schema_patterns = [
        r"(what is|show) the schema (of|for) ([a-zA-Z_, ]+)",
        r"describe ([a-zA-Z_, ]+) table",
        r"describe table[s]? ([a-zA-Z_, ]+)"
    ]
    
    # Check if the question is asking to list tables
    for pattern in list_tables_patterns:
        if re.search(pattern, question.lower()):
            return {"list_tables": True, "agent_mode": False}
    
    # Check if the question is asking for a schema
    for pattern in schema_patterns:
        match = re.search(pattern, question.lower())
        if match:
            tables = match.group(3) if len(match.groups()) >= 3 else match.group(1)
            table_list = [t.strip() for t in tables.split(',')]
            return {"get_schema": True, "table_names": table_list, "agent_mode": False}
    
    # For everything else, use the agent mode
    return {"query": question, "agent_mode": True}

def main():
    # Initialize the action analyzer
    analyzer = ActionAnalyzer()
    
    # Get the question from the user
    question = input("Enter your question: ")
    
    # Get the required actions
    required_actions = analyzer.get_required_actions(question)
    
    # Print the required actions
    print("\nRequired actions:")
    for action_class in required_actions:
        print(f"- {action_class.get_description()}")
    
    # Execute each action
    for action_class in required_actions:
        action = action_class()
        action_name = action_class.get_description()
        print(f"\nExecuting: {action_name}")
        
        if action_name == "Execute SQL queries on a database":
            # Parse the question to get SQL parameters
            params = parse_sql_query(question)
            
            # Determine and show mode
            if "postgres_info" in params:
                print(f"Using PostgreSQL info mode: {params['postgres_info']}")
            else:
                print(f"Using SQL {'agent' if params.get('agent_mode', True) else 'direct'} mode")
                
            result = action.execute(**params)
            print(f"\nResult: {result}")
            
        elif action_name == "Read a CSV file and extract data":
            # Execute the CSV action with the query
            result = action.execute(query=question)
            print(f"\nResult: {result}")
            
        elif action_name == "Connect to internet and browse for data":
            # Execute the web action with a generated URL
            # This is a simplification - in a real app, you would generate an appropriate URL
            result = action.execute(url="https://example.com")
            print(f"\nResult: {result}")
            
        else:
            print(f"No implementation available for action: {action_name}")

if __name__ == "__main__":
    main()
