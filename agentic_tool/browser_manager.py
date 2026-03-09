import logging
import os
import contextvars
from typing import Optional, Tuple
from agentic_tool.browser_use_agent.browser import start_local_browser, start_agentbay_browser, BrowserWrapper
from agentic_tool.browser_use_agent.context import current_uid_cv
from browser_use import BrowserProfile, BrowserSession
from config import config

logger = logging.getLogger(__name__)

class BrowserManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = BrowserManager()
        return cls._instance

    async def create_new_session(self, uid: str = None) -> Tuple[BrowserSession, BrowserWrapper]:
        """Create a new browser session and wrapper. Caller is responsible for closing."""
        target_uid = uid or current_uid_cv.get()
        logger.info(f"Creating new browser session for user: {target_uid}")
        
        cdp_url = None
        user_data_dir = None
        wrapper = None
        
        try:
            if config.browser_provider == "agent_bay":
                # Pass target_uid as user_id to enable persistent context
                wrapper = await start_agentbay_browser(user_id=target_uid)
                cdp_url = wrapper.endpoint
                # For AgentBay, user_data_dir is managed remotely
            else:
                # Determine user data directory for local browser
                if target_uid:
                    user_data_dir = os.path.join(config.user_data_dir, target_uid)
                else:
                    user_data_dir = config.user_data_dir

                wrapper = await start_local_browser(config.cdp_port, user_data_dir=user_data_dir)
                cdp_url = f"http://127.0.0.1:{config.cdp_port}"
            
            # Create Browser Profile
            browser_profile = BrowserProfile(
                headless=config.headless,
                disable_security=config.disable_security,
                highlight_elements=True,
                wait_between_actions=config.wait_between_actions,
                user_data_dir=user_data_dir,
            )
            
            session = BrowserSession(
                browser_profile=browser_profile,
                cdp_url=cdp_url,
            )
            
            return session, wrapper
            
        except Exception as e:
            logger.error(f"Failed to create new session: {e}")
            if wrapper:
                await wrapper.stop()
            raise

    async def close(self):
        """No-op for stateless manager, but kept for compatibility."""
        pass
