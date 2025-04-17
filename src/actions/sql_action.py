from .base_action import BaseAction
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.prompts import ChatPromptTemplate
from ..config.config import OPENAI_API_KEY, DB_CONNECTION_STRING

class SQLDatabaseAction(BaseAction):
    def __init__(self):
        try:
            # Initialize the SQL database utility
            self.db = SQLDatabase.from_uri(DB_CONNECTION_STRING)
            
            # Initialize the LLM
            self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
            
            # Create the SQL toolkit
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            
            # Create an agent executor with the SQL toolkit
            self.agent = create_sql_agent(
                llm=self.llm,
                toolkit=self.toolkit,
                verbose=True,
                handle_parsing_errors=True
            )
            
            # Also create a simpler query chain for direct SQL generation
            self.query_chain = create_sql_query_chain(self.llm, self.db)
            
            self.error = None
            
        except Exception as e:
            self.error = f"Error initializing SQL agent: {str(e)}"
            self.db = None
            self.agent = None
            self.query_chain = None

    def execute(self, query: str = None, list_tables: bool = False, get_schema: bool = False, 
                table_names: list = None, agent_mode: bool = True):
        """Execute SQL operations using LangChain's SQLDatabase toolkit
        
        Args:
            query: Natural language query or SQL query to execute
            list_tables: If True, list all tables in the database
            get_schema: If True, return the schema for specified tables
            table_names: List of table names to get schema for (when get_schema is True)
            agent_mode: If True, use the SQL agent, otherwise use direct operations
        """
        if self.error:
            return self.error
            
        try:
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