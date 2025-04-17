from .utils.action_analyzer import ActionAnalyzer
from .actions.sql_action import SQLDatabaseAction
import re
import os

def parse_sql_query(question):
    """Parse the question to extract SQL-related parameters"""
    
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
