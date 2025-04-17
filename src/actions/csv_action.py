from .base_action import BaseAction
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
from langchain.prompts import ChatPromptTemplate
from ..config.config import OPENAI_API_KEY, DEFAULT_CSV_PATH
import os
import glob
import pandas as pd

class CSVAction(BaseAction):
    def __init__(self):
        try:
            # Initialize the LLM
            self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
            self.error = None
        except Exception as e:
            self.error = f"Error initializing CSV agent: {str(e)}"
            self.llm = None

    def _find_best_csv_file(self, question, data_dir="data"):
        """Use LLM to determine the most relevant CSV file based on the question
        
        Args:
            question (str): The user question
            data_dir (str): Directory containing CSV files
            
        Returns:
            str: Path to the most relevant CSV file
        """
        # Check if a specific file path is mentioned in the question
        direct_path_patterns = [
            r"in the (csv|file|data|dataset) (?:at |from |located at |in |called |named )?([\w\-\.\/]+\.csv)",
            r"([\w\-\.\/]+\.csv)",
            r"from ([\w\-\.\/]+\.csv)"
        ]
        
        for pattern in direct_path_patterns:
            import re
            match = re.search(pattern, question, re.IGNORECASE)
            if match:
                path = match.group(2) if len(match.groups()) > 1 else match.group(1)
                if os.path.exists(path):
                    return path, f"Using explicitly mentioned file: {path}"
        
        # Find all CSV files in the data directory
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        if not csv_files:
            return DEFAULT_CSV_PATH, f"No CSV files found in {data_dir}, using default"
            
        # If only one CSV file, use it
        if len(csv_files) == 1:
            return csv_files[0], f"Only one CSV file available: {csv_files[0]}"
            
        # Get CSV file metadata to help LLM decide
        csv_metadata = []
        for file_path in csv_files:
            try:
                # Read a small sample to get column info
                df = pd.read_csv(file_path, nrows=5)
                columns = ", ".join(df.columns)
                metadata = {
                    "file_path": file_path,
                    "columns": columns,
                    "sample_values": str(df.iloc[0].to_dict())
                }
                csv_metadata.append(metadata)
            except Exception as e:
                print(f"Error reading CSV file {file_path}: {str(e)}")
                
        # Create a prompt for the LLM
        template = """
        I need to determine which CSV file is most relevant to answer the following question:
        Question: {question}
        
        Available CSV files:
        {csv_files}
        
        Return only the file path of the most relevant CSV file. Do not include any explanation.
        If none of the files seem relevant, return the path to the first file.
        """
        
        # Format the CSV files information
        csv_files_info = "\n".join([
            f"File: {meta['file_path']}\nColumns: {meta['columns']}\nSample row: {meta['sample_values']}"
            for meta in csv_metadata
        ])
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(template)
        
        # Get response from LLM
        messages = prompt.format_messages(
            question=question,
            csv_files=csv_files_info
        )
        
        response = self.llm.invoke(messages)
        selected_file = response.content.strip()
        
        # Verify the selected file exists
        if os.path.exists(selected_file):
            return selected_file, f"LLM selected file: {selected_file}"
        else:
            # Fall back to first file if LLM returned an invalid path
            return csv_files[0], f"Invalid path from LLM, using first file: {csv_files[0]}"
    
    def execute(self, file_path=None, query=None, pandas_kwargs=None, *args, **kwargs):
        """Process CSV data using LangChain's CSV agent
        
        Args:
            file_path (str, optional): Path to the CSV file. Defaults to None.
            query (str): Natural language query about the CSV data
            pandas_kwargs (dict, optional): Additional arguments to pass to pandas.read_csv
        """
        if self.error:
            return self.error
            
        if not query:
            return "Please provide a query to analyze the CSV data"
            
        try:
            # Determine the file path
            selection_message = ""
            if not file_path:
                file_path, selection_message = self._find_best_csv_file(query)
                print(selection_message)
                
            # Check if file exists
            if not os.path.exists(file_path):
                return f"CSV file not found at {file_path}"
                
            # Create CSV agent
            agent = create_csv_agent(
                llm=self.llm,
                path=file_path,
                pandas_kwargs=pandas_kwargs or {},
                agent_type="openai-tools",
                verbose=True,
                allow_dangerous_code=True
            )
            
            # Execute the query
            result = agent.invoke({"input": query})
            
            return result.get("output", "No result found")
            
        except Exception as e:
            return f"Error analyzing CSV data: {str(e)}"

    @classmethod
    def get_description(cls) -> str:
        return "Read a CSV file and extract data" 