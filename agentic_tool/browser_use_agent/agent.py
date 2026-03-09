import os
import logging
import socket
from browser_use import BrowserProfile, BrowserSession
from browser_use.llm.messages import UserMessage
from config import config
from agentic_tool.browser_use_agent.browser import start_local_browser, start_agentbay_browser
from llm import get_llm
from agentic_tool.browser_use_agent.controller import MyController
from agentic_tool.browser_use_agent.prompts.system import load_system_prompt
from browser_use.llm import ChatOpenAI as BrowserUseChatOpenAI

from browser_use.agent.service import Agent

logger = logging.getLogger(__name__)

def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])

from agentic_tool.browser_use_agent.context import current_uid_cv

class BrowserAgent:
    def __init__(self, context=None, step_callback=None):
        self.browser_wrapper = None
        self.browser_session = None
        self.agent = None
        self.llm = get_llm()
        self.context = context
        self.external_step_callback = step_callback

    async def _setup_browser(self, output_dir: str | None = None, cdp_port: int | None = None, session: BrowserSession | None = None):
        """Initialize the local or remote browser and session."""
        try:
            if session:
                self.browser_session = session
                logger.info("Using provided browser session")
                if getattr(self.browser_session, "cdp_url", None):
                    await self.browser_session.connect()
                return

            cdp_url = None
            
            if config.browser_provider == "agent_bay":
                logger.info("Using AgentBay browser provider")
                # Try to get user_id from context var
                user_id = current_uid_cv.get()
                self.browser_wrapper = await start_agentbay_browser(user_id=user_id)
                cdp_url = self.browser_wrapper.endpoint
            else:
                logger.info("Using Local browser provider")
                attempts = 3
                last_error: Exception | None = None
                for _ in range(attempts):
                    port = int(cdp_port or _get_free_port())
                    try:
                        self.browser_wrapper = await start_local_browser(port)
                        cdp_url = f"http://127.0.0.1:{port}"
                        break
                    except Exception as e:
                        last_error = e
                        cdp_port = None
                else:
                    raise last_error or RuntimeError("Failed to launch local browser")
            
            # Create Browser Profile
            browser_profile = BrowserProfile(
                headless=config.headless,
                disable_security=config.disable_security,
                highlight_elements=True,
                wait_between_actions=config.wait_between_actions,
                downloads_path=output_dir,
                user_data_dir=config.user_data_dir,
            )
            
            self.browser_session = BrowserSession(
                browser_profile=browser_profile,
                cdp_url=cdp_url,
            )
            await self.browser_session.connect()
            logger.info(f"Browser initialized with CDP URL: {cdp_url}")
            logger.info(f"Downloads path set to: {output_dir}")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            raise

    async def _create_agent(self, task: str):
        """Create the Browser Use Agent instance."""
        controller = MyController()
        system_prompt = load_system_prompt(task)
        ctx = {"mode": "cli"}
        
        extract_llm = get_llm()
        
        # Convert LangChain LLM to BrowserUse LLM to avoid "ainvoke" method mismatch
        # The browser-use library expects its own BaseChatModel implementation, not LangChain's
        bu_llm = BrowserUseChatOpenAI(
            model=self.llm.model_name,
            api_key=self.llm.openai_api_key.get_secret_value() if hasattr(self.llm.openai_api_key, 'get_secret_value') else self.llm.openai_api_key,
            base_url=self.llm.openai_api_base,
        )
        
        bu_extract_llm = BrowserUseChatOpenAI(
            model=extract_llm.model_name,
            api_key=extract_llm.openai_api_key.get_secret_value() if hasattr(extract_llm.openai_api_key, 'get_secret_value') else extract_llm.openai_api_key,
            base_url=extract_llm.openai_api_base,
        )

        result = await bu_llm.ainvoke([UserMessage(content="你好")])
        print(result)

        self.agent = Agent(
            task=task,
            llm=bu_llm,
            browser_session=self.browser_session,
            register_new_step_callback=self._step_callback,
            use_vision=True,
            page_extraction_llm=bu_extract_llm,
            controller=controller,
            override_system_message=system_prompt,
            context=ctx,
        )

        ctx["agent"] = self.agent

    async def _step_callback(self, browser_state, model_output, step_number):
        """Callback to log agent's thought process and actions."""
        try:
            step_info = {
                "step": step_number,
                "goal": "N/A",
                "memory": "N/A",
                "actions": [],
                "preview_url": None
            }
            
            if hasattr(model_output, "current_state"):
                state = model_output.current_state
                step_info["goal"] = getattr(state, 'next_goal', 'N/A')
                step_info["memory"] = getattr(state, 'memory', 'N/A')
                logger.info(f"\n--- Step {step_number} ---")
                logger.info(f"Goal: {step_info['goal']}")
                logger.info(f"Memory: {step_info['memory']}")
            
            if hasattr(model_output, "action"):
                for i, action in enumerate(model_output.action):
                    action_dict = action.model_dump(exclude_none=True)
                    step_info["actions"].append(action_dict)
                    logger.info(f"Action {i+1}: {action_dict}")
                    
                    if "ask_human" in action_dict and self.browser_wrapper and getattr(self.browser_wrapper, "preview_url", None):
                        preview_url = self.browser_wrapper.preview_url
                        step_info["preview_url"] = preview_url
                        from .context import preview_url_cv
                        preview_url_cv.set(preview_url)
                        print("\n" + "="*50)
                        print("🔴 INTERACTION REQUIRED")
                        print("Please open the link below to manually control the remote browser:")
                        print(f"\n[Interactive Remote Browser]\n{preview_url}\n")
                        print("(You can click, type, and navigate in this window)")
                        print("="*50 + "\n")
            
            from agentic_tool.browser_use_agent.context import browser_steps_cv
            
            def update_steps():
                steps = browser_steps_cv.get()
                logger.info(f"[DEBUG] _step_callback: browser_steps_cv id={id(browser_steps_cv)}, current steps={steps}")
                if steps is None:
                    steps = []
                steps.append(step_info)
                browser_steps_cv.set(steps)
                logger.info(f"[DEBUG] _step_callback: added step {step_number}, total steps={len(steps)}")
                logger.info(f"[DEBUG] Step info: goal={step_info['goal']}, actions={len(step_info['actions'])}")
            
            if self.context:
                logger.info(f"[DEBUG] Using context to update steps")
                self.context.run(update_steps)
            else:
                logger.info(f"[DEBUG] No context, updating steps directly")
                update_steps()
            
            # Call external callback if provided
            if self.external_step_callback:
                try:
                    await self.external_step_callback(step_info)
                except Exception as e:
                    logger.warning(f"Error in external step callback: {e}")
            
        except Exception as e:
            logger.warning(f"Error in step callback: {e}")

    async def invoke(self, task: str, cdp_port: int | None = None, folder_path: str | None = None, session: BrowserSession | None = None):
        """
        Main entry point to execute a task.
        """
        try:
            # Inject folder path into task if provided
            logger.info(f"[DEBUG] ainvoke received folder_path: '{folder_path}'")
            if folder_path:
                task = f"【重要资源路径】请使用位于以下目录的资源：{folder_path}\n\n任务：{task}"
                logger.info(f"[DEBUG] Task updated with folder_path")

            logger.info(f"Starting task: {task}")
            
            # 1. Setup Browser
            # Pass None for output_dir to avoid creating specific download folders or enforcing paths
            await self._setup_browser(None, cdp_port=cdp_port, session=session)
            
            # 2. Create Agent
            await self._create_agent(task)
            
            # 3. Run Agent
            history = await self.agent.run(max_steps=config.max_steps)
            
            # 4. Extract Final Result
            final_result = history.final_result()
            
            logger.info("\n" + "="*50)
            logger.info("TASK COMPLETED")
            logger.info("="*50)
            logger.info(f"Final Result: {final_result}")
            
            return final_result

        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            raise
        finally:
            await self._cleanup()

    async def _cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        # Only cleanup if we own the browser wrapper (meaning we created it)
        if self.browser_wrapper:
            # If we have a session but it was NOT passed in externally (implied by existence of wrapper created here)
            # Actually, _setup_browser logic: if session passed, wrapper is NOT created.
            # So if wrapper exists, we created it and should clean it up.
            
            # BUT, we should also close the browser_session's page/context if we created it.
            if self.browser_session:
                try:
                    await self.browser_session.close_page()
                except Exception:
                    pass
            
            await self.browser_wrapper.stop()
        else:
            logger.info("Skipping cleanup: Browser session was provided externally")

async def ainvoke(task: str, cdp_port: int | None = None, folder_path: str | None = None, session: BrowserSession | None = None, context=None, step_callback=None):
    agent = BrowserAgent(context=context, step_callback=step_callback)
    return await agent.invoke(task, cdp_port=cdp_port, folder_path=folder_path, session=session)
