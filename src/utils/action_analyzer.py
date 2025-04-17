from typing import List, Type
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from ..config.config import OPENAI_API_KEY
from ..actions.base_action import BaseAction
from ..actions.csv_action import CSVAction
from ..actions.web_action import WebAction
from ..actions.sql_action import SQLDatabaseAction
import re

class ActionAnalyzer:
    def __init__(self):
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        self.available_actions = [
            CSVAction,
            WebAction,
            SQLDatabaseAction
        ]
        self._create_prompt_template()

    def _create_prompt_template(self):
        template = """
        Given the following question: {question}
        
        And these available actions:
        {actions}
        
        Return a list of actions that should be taken to answer the question.
        Format your response as a valid Python list of strings containing the action names, exactly as they appear above.
        For example: ["Connect to DB and retrieve data", "Read a CSV file and extract data"]
        Only include actions that are directly relevant to answering the question.
        """
        
        self.prompt = ChatPromptTemplate.from_template(template)

    def _parse_response(self, response_content: str) -> List[str]:
        """Parse the response from OpenAI to extract action names"""
        # First, try to evaluate as a Python list
        try:
            return eval(response_content)
        except (SyntaxError, ValueError):
            # If eval fails, try to parse as bullet points
            action_names = []
            lines = response_content.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Check for bullet point format (- Action name)
                if line.startswith('- '):
                    action_names.append(line[2:].strip())
                # Check for numbered list format (1. Action name)
                elif re.match(r'^\d+\.\s+', line):
                    action_names.append(re.sub(r'^\d+\.\s+', '', line).strip())
            return action_names

    def get_required_actions(self, question: str) -> List[Type[BaseAction]]:
        """Analyze the question and return a list of required actions"""
        # Create the action descriptions string
        action_descriptions = "\n".join(
            f"- {action.get_description()}" 
            for action in self.available_actions
        )
        
        # Get the response from OpenAI
        messages = self.prompt.format_messages(
            question=question,
            actions=action_descriptions
        )
        response = self.llm.invoke(messages)
        
        # Parse the response to get action names
        action_names = self._parse_response(response.content)
        
        # Map the descriptions back to action classes
        selected_actions = []
        for name in action_names:
            for action in self.available_actions:
                if action.get_description() == name:
                    selected_actions.append(action)
                    
        return selected_actions
