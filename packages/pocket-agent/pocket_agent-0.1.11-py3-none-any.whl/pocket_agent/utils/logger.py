import logging
import os
import litellm


def configure_logger(log_level: str = "DEBUG"):
    # Configure root logger with file handler only
    # read log level from environment variable
    log_level = os.getenv("POCKET_AGENT_LOG_LEVEL", "DEBUG")
    log_level = log_level.upper()
    log_level = logging.getLevelNamesMapping().get(log_level, logging.INFO)
    # Add only file handler
    logging.basicConfig(  
        level=log_level,  
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  
        handlers=[  
            logging.FileHandler('pocket-agent.log')
        ]  
    ) 
    pocket_agent_logger = logging.getLogger("pocket_agent")
    pocket_agent_logger.handlers = logging.getLogger().handlers


    fastmcp_logger = logging.getLogger("FastMCP")  
    fastmcp_logger.handlers = logging.getLogger().handlers  

    mcp_logger = logging.getLogger("mcp")  
    mcp_logger.handlers = logging.getLogger().handlers

    if log_level == "DEBUG":
        litellm._turn_on_debug()
    litellm_logger = logging.getLogger("LiteLLM")  
    litellm_logger.handlers = logging.getLogger().handlers

    litellm_router_logger = logging.getLogger("LiteLLM Router")  
    litellm_router_logger.handlers = logging.getLogger().handlers
        
        
    return pocket_agent_logger