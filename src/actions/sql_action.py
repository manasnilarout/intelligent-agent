from .base_action import BaseAction
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.prompts import ChatPromptTemplate
from ..config.config import OPENAI_API_KEY, DB_CONNECTION_STRING
import os
import re
import sqlalchemy

class SQLDatabaseAction(BaseAction):
    def __init__(self):
        try:
            # Get the connection string from the environment
            connection_string = DB_CONNECTION_STRING
            
            # Detect if it's a PostgreSQL connection
            self.is_postgres = connection_string.startswith('postgres')
            
            # Initialize the SQL database utility with appropriate options for PostgreSQL
            if self.is_postgres:
                # Additional options for PostgreSQL
                self.db = SQLDatabase.from_uri(
                    connection_string,
                    sample_rows_in_table_info=3,
                    include_tables=None,  # Include all tables
                    indexes_in_table_info=True,  # Include index information
                    custom_table_info=None,
                    view_support=True  # Support views in PostgreSQL
                )
                print("Connected to PostgreSQL database")
            else:
                # Default options for SQLite or other databases
                self.db = SQLDatabase.from_uri(connection_string)
            
            # Initialize the LLM
            self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
            
            # Create custom system message for the agent that includes database type info
            system_message = """You are an expert SQL agent who helps users interact with databases.
            
            """
            if self.is_postgres:
                system_message += """
                You are currently connected to a PostgreSQL database. You can:
                1. Execute regular SQL queries
                2. Get information about tables, schemas, and functions
                3. Answer natural language questions about the database
                
                For PostgreSQL, use appropriate PostgreSQL syntax and capabilities.
                """
            else:
                system_message += """
                You are currently connected to a SQLite database. Use SQLite-compatible 
                SQL syntax in your queries.
                """
            
            # Create the SQL toolkit
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            # Create an agent executor with the SQL toolkit
            self.agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                handle_parsing_errors=True,
                extra_tools=[self._create_postgres_tools() if self.is_postgres else None]
            )
            
            # Also create a simpler query chain for direct SQL generation
            self.query_chain = create_sql_query_chain(self.llm, self.db)
            
            self.error = None
            
        except Exception as e:
            self.error = f"Error initializing SQL agent: {str(e)}"
            self.db = None
            self.agent = None
            self.query_chain = None
    
    def _create_postgres_tools(self):
        """Create PostgreSQL-specific tools for the agent"""
        class PostgreSQLInfoTool:
            def __init__(self, db):
                self.db = db
                
            def run(self, info_type: str) -> str:
                """Run a PostgreSQL-specific information query
                
                Args:
                    info_type: Type of information to retrieve (tables, schemas, functions, users, size)
                    
                Returns:
                    Query results as a string
                """
                # Various PostgreSQL information queries
                queries = {
                    "tables": """
                        SELECT table_name, table_type 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name;
                    """,
                    "schemas": """
                        SELECT schema_name 
                        FROM information_schema.schemata 
                        ORDER BY schema_name;
                    """,
                    "functions": """
                        SELECT routine_name, routine_type 
                        FROM information_schema.routines 
                        WHERE routine_schema = 'public'
                        ORDER BY routine_name;
                    """,
                    "users": """
                        SELECT usename AS username, usesuper AS is_superuser 
                        FROM pg_user
                        ORDER BY usename;
                    """,
                    "size": """
                        SELECT
                            table_name,
                            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
                    """
                }
                
                if info_type.lower() in queries:
                    result = self.db.run(queries[info_type.lower()])
                    return result
                else:
                    valid_types = ", ".join(queries.keys())
                    return f"Unknown PostgreSQL information type. Valid types are: {valid_types}"
        
        return PostgreSQLInfoTool(self.db)
            
    def execute_postgres_info_query(self, info_type):
        """Execute PostgreSQL-specific information queries"""
        try:
            if not self.is_postgres or not self.db:
                return "This operation is only available for PostgreSQL databases"
            
            # Various PostgreSQL information queries
            queries = {
                "tables": """
                    SELECT table_name, table_type 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """,
                "schemas": """
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    ORDER BY schema_name;
                """,
                "functions": """
                    SELECT routine_name, routine_type 
                    FROM information_schema.routines 
                    WHERE routine_schema = 'public'
                    ORDER BY routine_name;
                """,
                "users": """
                    SELECT usename AS username, usesuper AS is_superuser 
                    FROM pg_user
                    ORDER BY usename;
                """,
                "size": """
                    SELECT
                        table_name,
                        pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY pg_total_relation_size(quote_ident(table_name)) DESC;
                """
            }
            
            # Execute the appropriate query if it exists
            if info_type in queries:
                result = self.db.run(queries[info_type])
                return result
            else:
                return f"Unknown PostgreSQL information type: {info_type}"
            
        except Exception as e:
            return f"Error executing PostgreSQL info query: {str(e)}"

    def execute(self, query: str = None, list_tables: bool = False, get_schema: bool = False, 
                table_names: list = None, agent_mode: bool = True, postgres_info: str = None):
        """Execute SQL operations using LangChain's SQLDatabase toolkit
        
        Args:
            query: Natural language query or SQL query to execute
            list_tables: If True, list all tables in the database
            get_schema: If True, return the schema for specified tables
            table_names: List of table names to get schema for (when get_schema is True)
            agent_mode: If True, use the SQL agent, otherwise use direct operations
            postgres_info: Type of PostgreSQL information to query (tables, schemas, functions, users, size)
        """
        if self.error:
            return self.error
            
        try:
            # Agent mode with PostgreSQL information query
            if agent_mode and self.is_postgres and query and "postgresql" in query.lower():
                if any(keyword in query.lower() for keyword in ["list tables", "show tables"]):
                    # Modify query to be clearer that it's about PostgreSQL tables
                    modified_query = "List all tables in the PostgreSQL database and their types"
                    result = self.agent.invoke({"input": modified_query})
                    return result.get("output", "No result found")
                
                if any(keyword in query.lower() for keyword in ["list schemas", "show schemas"]):
                    modified_query = "List all schemas in the PostgreSQL database"
                    result = self.agent.invoke({"input": modified_query})
                    return result.get("output", "No result found")
                
                if any(keyword in query.lower() for keyword in ["list functions", "show functions"]):
                    modified_query = "List all functions in the PostgreSQL database"
                    result = self.agent.invoke({"input": modified_query})
                    return result.get("output", "No result found")
            
            # PostgreSQL-specific information operations (direct mode)
            if self.is_postgres and postgres_info:
                return self.execute_postgres_info_query(postgres_info)
                
            # Basic database operations (non-agent mode)
            if not agent_mode:
                if list_tables:
                    return self.db.get_table_names()
                elif get_schema:
                    if table_names:
                        return self.db.get_table_info(table_names=table_names)
                    else:
                        # Get schema for all tables if none specified
                        return self.db.get_table_info()
                elif query and query.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE')):
                    # Direct SQL execution
                    return self.db.run(query)
            
            # If we have a natural language query, or agent_mode is True
            if query:
                if agent_mode:
                    # Use the SQL agent to answer the query
                    result = self.agent.invoke({"input": query})
                    return result.get("output", "No result found")
                else:
                    # Generate SQL from natural language and execute it
                    sql_query = self.query_chain.invoke({"question": query})
                    print(f"Generated SQL: {sql_query}")
                    return self.db.run(sql_query)
                    
            return "Please provide a query or set list_tables/get_schema to True"
            
        except Exception as e:
            return f"Error executing SQL operation: {str(e)}"

    @classmethod
    def get_description(cls) -> str:
        return "Execute SQL queries on a database" 