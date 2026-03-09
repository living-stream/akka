import asyncio
import os
import sys
import logging
import json
import base64
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

from agentic_tool.browser_use_agent.agent import BrowserAgent

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecordSkillAgent(BrowserAgent):
    def __init__(self, record_dir: str):
        super().__init__()
        self.record_dir = Path(record_dir)
        self.record_dir.mkdir(parents=True, exist_ok=True)
        self.step_log_file = self.record_dir / "execution_log.txt"
        # Clear log file if exists
        if self.step_log_file.exists():
            self.step_log_file.unlink()

    async def _step_callback(self, browser_state, model_output, step_number):
        """Override callback to record execution details."""
        try:
            # Call the original callback to keep existing logging behavior
            await super()._step_callback(browser_state, model_output, step_number)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"step_{step_number}_{timestamp}.png"
            image_path = self.record_dir / "images" / image_filename
            image_path.parent.mkdir(parents=True, exist_ok=True)

            # 1. Save Screenshot
            screenshot_saved = False
            try:
                # Use browser session to take a fresh, full-page screenshot
                if self.browser_session:
                    page = await self.browser_session.get_current_page()
                    if page:
                        logger.info(f"Attempting full-page screenshot for step {step_number}...")
                        logger.info(f"Page object type: {type(page)}")
                        
                        # Inspect wrapper attributes to find underlying Playwright page
                        logger.info(f"Page attributes: {dir(page)}")
                        
                        # Handle potential wrapper or direct Playwright page
                        target_page = None
                        
                        # Try 0: Check self.browser_wrapper from BrowserAgent
                        if not target_page and self.browser_wrapper and self.browser_wrapper.browser:
                            logger.info("Using browser_wrapper.browser to find page...")
                            try:
                                # Handle both Browser (has contexts) and BrowserContext (has pages)
                                 browser_obj = self.browser_wrapper.browser
                                 all_pages = []
                                 
                                 if hasattr(browser_obj, 'contexts'):
                                     for ctx in browser_obj.contexts:
                                         all_pages.extend(ctx.pages)
                                 elif hasattr(browser_obj, 'pages'):
                                     all_pages.extend(browser_obj.pages)
                                     
                                 if all_pages:
                                     # Try to find a page that matches the wrapper page URL if possible
                                     wrapper_url = None
                                     try:
                                         if hasattr(page, 'url'):
                                             wrapper_url = page.url
                                         elif hasattr(page, 'get_url'):
                                             wrapper_url = await page.get_url() if asyncio.iscoroutinefunction(page.get_url) else page.get_url()
                                     except Exception as e:
                                         logger.warning(f"Failed to get URL from wrapper: {e}")
                                     
                                     if wrapper_url:
                                         for p in all_pages:
                                             # Simple normalization (strip trailing slash)
                                             p_url = p.url.rstrip('/')
                                             w_url = wrapper_url.rstrip('/')
                                             if p_url == w_url:
                                                 target_page = p
                                                 logger.info(f"Found page matching URL via browser_wrapper: {p.url}")
                                                 break
                                    
                                     # Fallback: last page found
                                     if not target_page:
                                         target_page = all_pages[-1]
                                         logger.info("Found page via browser_wrapper (last available page)")
                            except Exception as e:
                                logger.warning(f"Failed to extract page from browser_wrapper: {e}")

                        # Logic adapted from skills/controller.py _get_playwright_page
                        # Try 1: Check if page itself is the handle (has locator)
                        if hasattr(page, 'locator'):
                            target_page = page
                        
                        # Try 2: Check for .page attribute
                        elif hasattr(page, 'page'):
                            target_page = page.page
                            logger.info("Found underlying 'page' attribute, using it.")
                        elif hasattr(page, '_page'):
                            target_page = page._page
                            logger.info("Found underlying '_page' attribute, using it.")
                        elif hasattr(page, 'playwright_page'):
                            target_page = page.playwright_page
                            logger.info("Found underlying 'playwright_page' attribute, using it.")
                        
                        # Try 3: Check browser_session context
                        if not target_page:
                            if hasattr(self.browser_session, 'context') and hasattr(self.browser_session.context, 'pages') and self.browser_session.context.pages:
                                target_page = self.browser_session.context.pages[-1]
                                logger.info("Found page via browser_session.context.pages[-1]")
                            elif hasattr(self.browser_session, 'browser_context') and hasattr(self.browser_session.browser_context, 'pages') and self.browser_session.browser_context.pages:
                                target_page = self.browser_session.browser_context.pages[-1]
                                logger.info("Found page via browser_session.browser_context.pages[-1]")

                        if target_page:
                            try:
                                # Try standard Playwright signature on target_page
                                if asyncio.iscoroutinefunction(target_page.screenshot):
                                    await target_page.screenshot(path=str(image_path), full_page=True)
                                else:
                                    # In case it's sync (unlikely for async playwright but possible for wrappers)
                                    target_page.screenshot(path=str(image_path), full_page=True)
                            except TypeError as e:
                                if "unexpected keyword argument 'path'" in str(e) or "unexpected keyword argument 'full_page'" in str(e):
                                    # Might be a wrapper or API mismatch, try getting bytes directly
                                    logger.info("Target page object does not accept 'path' or 'full_page', trying to get bytes...")
                                    screenshot_bytes = await target_page.screenshot()
                                    with open(image_path, "wb") as f:
                                        f.write(screenshot_bytes)
                                else:
                                    raise e
                                    
                            screenshot_saved = True
                            logger.info(f"Full-page screenshot saved to {image_path}")
                        else:
                            logger.warning("Could not find underlying Playwright page object.")
                    else:
                        logger.warning("No current page found in browser_session.")
                else:
                    logger.warning("browser_session is None.")
            except Exception as e:
                logger.warning(f"Failed to take full page screenshot: {e}")

            # Fallback to browser_state screenshot if direct capture failed
            if not screenshot_saved:
                logger.info("Falling back to browser_state screenshot...")
                screenshot_data = None
                # Handle different potential structures of browser_state
                if isinstance(browser_state, list) and len(browser_state) > 0:
                    # If it's a list, usually the last one is current
                    last_state = browser_state[-1]
                    if hasattr(last_state, 'screenshot'):
                        screenshot_data = last_state.screenshot
                elif hasattr(browser_state, 'screenshot'):
                     screenshot_data = browser_state.screenshot
                
                if screenshot_data:
                    try:
                        # Remove header if present (e.g. "data:image/png;base64,")
                        if "," in screenshot_data:
                            screenshot_data = screenshot_data.split(",")[1]
                        
                        with open(image_path, "wb") as f:
                            f.write(base64.b64decode(screenshot_data))
                        screenshot_saved = True
                    except Exception as e:
                        logger.error(f"Failed to save fallback screenshot: {e}")

            # 2. Extract State Info
            goal = "N/A"
            memory = "N/A"
            if hasattr(model_output, "current_state"):
                state = model_output.current_state
                goal = getattr(state, 'next_goal', 'N/A')
                memory = getattr(state, 'memory', 'N/A')

            # 3. Extract Actions
            actions = []
            if hasattr(model_output, "action"):
                for i, action in enumerate(model_output.action):
                    actions.append(f"Action {i+1}: {action.model_dump(exclude_none=True)}")

            # 4. Write to Log File
            log_entry = f"\n--- Step {step_number} ---\n"
            if screenshot_saved:
                log_entry += f"Picture: {image_path.absolute()}\n"
            else:
                log_entry += "Picture: N/A (Screenshot not found)\n"
            
            log_entry += f"Goal: {goal}\n"
            log_entry += f"Memory: {memory}\n"
            for action_str in actions:
                log_entry += f"{action_str}\n"
            
            with open(self.step_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            logger.error(f"Error in record callback: {e}")

async def main():
    print("\n" + "="*50)
    print("🎬 Skill Recording Tool")
    print("="*50)

    # 1. Get User Input
    skill_name = input("Enter the skill name to record (e.g., 'sohu-posting'): ").strip()
    if not skill_name:
        print("Skill name is required.")
        return

    task_description = input("Enter the task description to trigger this skill: ").strip()
    if not task_description:
        print("Task description is required.")
        return
    
    # 2. Setup Recording Directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    record_path = os.path.join("opti", f"record_{skill_name}_{timestamp}")
    print(f"\n📂 Recording to: {os.path.abspath(record_path)}")

    # 3. Initialize Agent
    agent = RecordSkillAgent(record_dir=record_path)

    # 4. Run Task
    # We construct the task prompt similar to how main execution might do it, 
    # but specifically mentioning the skill might help if the system prompt relies on it.
    # However, Agent logic uses LLM to select skill. 
    # To force a specific skill, we might need to bypass selection or ensure the task triggers it.
    # For now, we rely on the task description being clear enough.
    
    # If the user wants to *force* a skill, we might need to modify how `_select_skill` works or pass it explicitly.
    # But `BrowserAgent.invoke` calls `_select_skill` internally.
    # Let's trust the task description for now, or we can prepend "Use skill {skill_name}:" to the task.
    
    full_task = f"Using the skill '{skill_name}', {task_description}"
    
    try:
        await agent.invoke(task=full_task)
        print("\n✅ Recording completed successfully.")
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
