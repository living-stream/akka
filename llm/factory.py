import os
from langchain_openai import ChatOpenAI
from config import config
from openai import AsyncOpenAI


def get_llm(model_name: str = None, need_reason_content: bool = False, enable_thinking: bool = True):
    """
    Get LLM instance by configuration.
    
    Args:
        model_name: Optional model name (for compatibility, but uses config.llm.model by default)
        need_reason_content: Whether to return reasoning content (for DeepSeek models)
        enable_thinking: Whether to enable thinking/reasoning feature (default: True)
    """
    if not config.llm:
        raise ValueError("LLM configuration not found. Please set OPENAI_API_KEY or configure config.yaml")
    
    if not config.llm.api_key:
        raise ValueError("LLM API key not found. Please set OPENAI_API_KEY or configure config.yaml")
    
    os.environ["OPENAI_API_KEY"] = "sk-dummy"
    
    extra_body = {}
    if not enable_thinking:
        extra_body["enable_thinking"] = False
    
    model = model_name or config.llm.model
    
    return ChatOpenAI(
        base_url=config.llm.base_url,
        model=model,
        api_key=config.llm.api_key,
        model_kwargs={"extra_body": extra_body} if extra_body else {}
    )


async def gen_picture(prompt: str) -> str:
    """Generate image from prompt."""
    if not config.llm or not config.llm.api_key:
        raise ValueError("LLM configuration not found. Please configure config.yaml")
    
    client = AsyncOpenAI( 
        base_url=config.llm.base_url,
        api_key=config.llm.api_key,
    ) 
 
    imagesResponse = await client.images.generate( 
        model=config.llm.model, 
        prompt=prompt,
        size="2K",
        response_format="url",
        extra_body={
            "watermark": False,
        },
    ) 
    
    return imagesResponse.data[0].url
