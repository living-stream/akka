import os
import logging
import re
from datetime import datetime
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.outputs import LLMResult

logger = logging.getLogger(__name__)

def enforce_log_format():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

class ModelLoggingCallback(BaseCallbackHandler):
    def on_chat_model_start(
        self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs
    ) -> None:
        logging.info(f"[Model] Chat model started\n")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        logging.info(f"[Model] Chat model ended, response: {response}")

    def on_llm_error(self, error: BaseException, **kwargs) -> Any:
        logging.info(f"[Model] Chat model error, response: {error}")

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        logging.info(f"[Model] Chain {serialized.get('name')} started")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        logging.info(f"[Model] Chain ended, outputs: {outputs}")

async def create_output_dir(task: str, llm=None) -> str:
    """
    Create an output directory based on current time and task description.
    Format: output/YYYY-MM-DD_HH-MM-SS_TaskSummary
    
    If llm is provided, use it to generate a better summary.
    """
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    summary = ""
    
    # Try to use LLM to generate a summary
    if llm:
        try:            
            msg = HumanMessage(content=f"Generate a very short (max 4-5 words), descriptive directory name for this task: '{task}'. Use underscores instead of spaces. Return ONLY the name, no other text.")
            response = await llm.ainvoke([msg])
            
            content = ""
            if hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'completion'):
                content = response.completion
            else:
                content = str(response)
                
            summary = re.sub(r'[^\w\s-]', '', content).strip().replace(' ', '_')
        except Exception as e:
            logging.warning(f"Failed to generate directory name with LLM: {e}")
    
    # Fallback if LLM failed or not provided
    if not summary:
        # Extract a short summary from the task (first 10-15 chars, safe filename)
        # Remove special chars and spaces
        summary = re.sub(r'[^\w\s-]', '', task)[:20].strip().replace(' ', '_')
    
    if not summary:
        summary = "task"
        
    # Ensure reasonable length
    summary = summary[:50]
        
    dir_name = f"{now}_{summary}"
    output_path = os.path.join(os.getcwd(), "output", dir_name)
    
    os.makedirs(output_path, exist_ok=True)
    return output_path

class Wrapper:
    def __init__(self, wrapped_class):
        self.wrapped_class = wrapped_class

    def __getattr__(self, attr):
        original_func = getattr(self.wrapped_class, attr)

        def wrapper(*args, **kwargs):
            print(f"Calling function: {attr}")
            print(f"Arguments: {args}, {kwargs}")
            result = original_func(*args, **kwargs)
            print(f"Response: {result}")
            return result

        return wrapper
