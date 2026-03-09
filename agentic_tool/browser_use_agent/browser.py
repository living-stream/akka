import asyncio
import logging
import os
import aiohttp
from typing import Union, Optional, Any
from playwright.async_api import async_playwright, Browser, BrowserContext
from playwright.async_api._generated import Playwright as AsyncPlaywright
from config import config

try:
    from agentbay import AgentBay, CreateSessionParams, BrowserOption, BrowserViewport, BrowserContext as AgentBayBrowserContext
    AGENTBAY_AVAILABLE = True
except ImportError:
    AGENTBAY_AVAILABLE = False
    logging.warning("AgentBay SDK not found. AgentBay integration will be disabled.")

logger = logging.getLogger(__name__)

# Use ContextVar from context.py
from agentic_tool.browser_use_agent.context import agentbay_session_cv

class BrowserWrapper:
    def __init__(self, port, browser: Union[Browser, BrowserContext], playwright: AsyncPlaywright, remote_browser_id: str = None, endpoint: str = None, agent_bay_session: Any = None, preview_url: str = None):
        self.port = port
        self.browser = browser
        self.playwright = playwright
        self.remote_browser_id = remote_browser_id
        self.endpoint = endpoint
        self.agent_bay_session = agent_bay_session
        self.preview_url = preview_url

    async def stop(self):
        if self.browser:
            logger.info(f"Closing browser on port {self.port}...")
            try:
                await self.browser.close()
                logger.info(f"Browser on port {self.port} closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser on port {self.port}: {e}")
                
        if self.playwright:
            logger.info(f"Closing playwright session {self.port}...")
            try:
                await self.playwright.stop()
                logger.info(f"Playwright session on port {self.port} closed successfully")
            except Exception as e:
                logger.warning(f"Error closing playwright session on port {self.port}: {e}")
        
        if self.agent_bay_session:
            logger.info("Closing AgentBay session...")
            try:
                self.agent_bay_session.delete()
                logger.info("AgentBay session closed successfully")
            except Exception as e:
                # Check if it's a "no alive session" error (session already dead)
                error_str = str(e)
                if "no alive session found" in error_str or "SessionHandleError" in error_str:
                    logger.warning(f"AgentBay session already terminated: {e}")
                else:
                    logger.error(f"Error closing AgentBay session: {e}")
                
        if self.remote_browser_id and self.endpoint:
            logger.info(f"Closing remote browser {self.remote_browser_id}...")
            try:
                async with aiohttp.ClientSession() as session:
                    delete_url = f"{self.endpoint}/{self.remote_browser_id}"
                    async with session.delete(delete_url, timeout=30) as response:
                        if response.status == 200:
                            logger.info(f"Remote browser {self.remote_browser_id} closed successfully")
                        else:
                            error_text = await response.text()
                            logger.error(f"Failed to close remote browser. Status: {response.status}, Error: {error_text}")
            except Exception as e:
                logger.error(f"Error closing remote browser {self.remote_browser_id}: {e}")

async def start_agentbay_browser(user_id: str = None) -> BrowserWrapper:
    if not AGENTBAY_AVAILABLE:
        raise ImportError("AgentBay SDK is not available. Please install it to use AgentBay browser.")
        
    if not config.agent_bay_config or not config.agent_bay_config.api_key:
        raise ValueError("AgentBay API Key not found in config.yaml under agent_bay.api_key")

    logger.info("Starting AgentBay browser session...")
    
    agent_bay = AgentBay(api_key=config.agent_bay_config.api_key)
    params = CreateSessionParams(image_id="browser_latest")
    
    # Configure persistence if user_id is provided
    if user_id:
        logger.info(f"Using persistent context for user: {user_id}")
        context_result = agent_bay.context.get(user_id, create=True)
        context = context_result.context
        
        browser_context = AgentBayBrowserContext(
            context_id=context.id,
            auto_upload=True
        )
        params.browser_context = browser_context
    
    # Create session
    result = agent_bay.create(params)
    if not result.success:
        raise RuntimeError(f"Failed to create AgentBay session: {result.error_message}")

    session = result.session
    logger.info(f"AgentBay session created: {session.session_id}")

    # Set ContextVar
    agentbay_session_cv.set(session)
    
    # Extract interactive preview URL
    preview_url = getattr(session, "resource_url", None)
    if preview_url:
        logger.info(f"Interactive Remote Browser URL: {preview_url}")
        print("\n" + "="*50)
        print("🔴 INTERACTIVE REMOTE BROWSER")
        print(f"URL: {preview_url}")
        print("Use this link to view and control the browser manually.")
        print("="*50 + "\n")
    
    # Initialize browser options
    CUSTOM_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    option = BrowserOption(
        user_agent=CUSTOM_UA,
        viewport=BrowserViewport(width=1920, height=1080),
    )

    # Initialize browser in session
    ok = session.browser.initialize(option)
    if not ok:
        session.delete()
        raise RuntimeError("AgentBay Browser initialization failed")

    endpoint_url = session.browser.get_endpoint_url()
    logger.info(f"AgentBay CDP Endpoint: {endpoint_url}")
    
    # Connect with Playwright
    p = await async_playwright().start()
    browser = None
    
    # Retry mechanism for CDP connection
    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to AgentBay CDP (Attempt {attempt+1}/{max_retries})...")
            # Increase timeout to 60s for remote connections
            browser = await p.chromium.connect_over_cdp(endpoint_url, timeout=60000)
            break
        except Exception as e:
            logger.warning(f"CDP connection attempt {attempt+1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to AgentBay CDP after {max_retries} attempts: {e}")
                await p.stop()
                session.delete()
                raise
            await asyncio.sleep(2) # Wait before retry

    # Use a dummy port for AgentBay since it's remote
    return BrowserWrapper(port=0, browser=browser, playwright=p, endpoint=endpoint_url, agent_bay_session=session, preview_url=preview_url)

async def start_local_browser(port: int = config.cdp_port, user_data_dir: str = None) -> BrowserWrapper:
    logger.info(f"Attempting to start browser on port {port}")
    p = None
    browser = None
    w = None

    try:
        p = await async_playwright().start()
        w = BrowserWrapper(port, None, p)

        # Configure proxy if environment variables are set
        proxy_config = None
        proxy_server = os.getenv('PROXY_SERVER')
        if proxy_server:
            proxy_config = {
                'server': proxy_server,
                'bypass': '127.0.0.1,localhost'
            }

        if user_data_dir is None:
            user_data_dir = config.user_data_dir
            
        os.makedirs(user_data_dir, exist_ok=True)
        logger.info(f"Using browser user data directory: {user_data_dir}")

        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=config.headless,
            args=[
                f'--remote-debugging-port={port}',
                '--remote-allow-origins=*',
                '--remote-debugging-address=0.0.0.0',
                '--no-sandbox'
            ],
            proxy=proxy_config
        )

        w.browser = browser
        logger.info(f"Browser launched successfully on port {port}")

        # Verify CDP is actually running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:{port}/json/version", timeout=5) as response:
                    if response.status == 200:
                        version_info = await response.json()
                        logger.info(f"successfully connected to cdp: {version_info}")
                    else:
                        logger.error(f"Failed to get CDP version. Status: {response.status}")
        except Exception as cdp_e:
            logger.error(f"Error checking CDP availability: {cdp_e}")
            await w.stop()
            raise

        return w

    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        if w:
            await w.stop()
        raise
