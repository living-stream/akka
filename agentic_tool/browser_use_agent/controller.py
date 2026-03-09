import logging
import asyncio
import sys
import os
import mimetypes
from pathlib import Path
from typing import List, Optional

from playwright.async_api import FilePayload, Page as PlaywrightPage, async_playwright
from browser_use.agent.views import ActionResult
from browser_use.browser import BrowserSession
from browser_use.controller import Controller
from pydantic import BaseModel
from agentic_tool.browser_use_agent.context import current_uid_cv

logger = logging.getLogger(__name__)


class SearchGoogleAction(BaseModel):
    query: str


class AskHumanAction(BaseModel):
    question: str


class ReadNoteResourcesAction(BaseModel):
    folder_path: str


class UploadImagesAction(BaseModel):
    image_paths: List[str]


class MyController(Controller):
    """Custom controller extending base Controller with additional actions."""

    # Constants for selectors
    UPLOAD_TRIGGER_SELECTORS = [
        '.upload-input',
        '.upload-wrapper',
        'div:contains("上传图片")',  # standard css :contains is not valid, but we use js below
        'button:contains("上传图片")',
        'div:contains("上传")',
        'div:contains("上传封面")',
        'div:contains("添加封面")',
        'div:contains("更换封面")',
        'div:contains("点击上传")',
        'div:contains("选择文件")',
        'div:contains("选择图片")',
    ]

    CONFIRM_SELECTORS = [
        'button:has-text("确定")',
        'button:has-text("确认")',
        'div:has-text("确定")',
        'div:has-text("确认")'
    ]

    def __init__(
        self,
        exclude_actions: list[str] = [],
        output_model: type[BaseModel] | None = None,
    ):
        super().__init__(exclude_actions, output_model)

        # Basic Navigation Actions
        @self.registry.action(
            'Search the query in Baidu in the current tab...',
            param_model=SearchGoogleAction,
        )
        async def search_google(params: SearchGoogleAction, browser_session: BrowserSession):
            search_url = f'https://www.baidu.com/s?wd={params.query}'
            
            page = await browser_session.get_current_page()
            if not page:
                page = await browser_session.new_page()
            await page.goto(search_url)
            await page.wait_for_load_state()
            msg = f'🔍 Searched for "{params.query}" in Baidu'
            logger.info(msg)
            return ActionResult(extracted_content=msg, include_in_memory=True)

        @self.registry.action(
            'Ask the human user to help with a task and allow user to input information or response...',
            param_model=AskHumanAction,
        )
        async def ask_human(params: AskHumanAction):
            from .human_assist import human_assist_manager
            from .context import preview_url_cv
            
            logger.info(f"Agent requesting human assistance: {params.question}")
            
            preview_url = preview_url_cv.get()
            request = await human_assist_manager.create_request(params.question, preview_url=preview_url)
            
            print("\n" + "=" * 50, flush=True)
            print(f"🤖 Agent 请求人工协助: {params.question}", flush=True)
            print(f"📋 请求ID: {request.request_id}", flush=True)
            print("👉 请在前端弹窗中完成操作并提交响应...", flush=True)
            print("=" * 50 + "\n", flush=True)
            
            try:
                response = await human_assist_manager.wait_for_response(request.request_id, timeout=300.0)
                
                if response:
                    logger.info(f"User response received for {request.request_id}: {response}")
                    print(f"\n✅ 用户响应: {response}\n", flush=True)
                    return ActionResult(extracted_content=f"User response: {response}", include_in_memory=True)
                else:
                    logger.warning(f"No response received for {request.request_id}")
                    return ActionResult(error="User did not respond within timeout")
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for user response: {request.request_id}")
                return ActionResult(error="Timeout waiting for user response")
            except Exception as e:
                logger.error(f"Error in ask_human: {e}")
                return ActionResult(error=f"Error getting user response: {str(e)}")

        @self.registry.action(
            'Read Little Red Book (XHS) note resources from a directory...',
            param_model=ReadNoteResourcesAction,
        )
        async def read_note_resources(params: ReadNoteResourcesAction):
            folder = Path(params.folder_path)
            
            # Robustness: if path ends with "images", use parent directory
            if folder.name == "images":
                folder = folder.parent
                logger.info(f"Detected 'images' in path, using parent directory: {folder}")
            
            if not folder.exists() or not folder.is_dir():
                return ActionResult(error=f"Directory not found: {params.folder_path}")

            outline_path = folder / "outline.md"
            copywriting_path = folder / "copywriting.md"
            images_dir = folder / "images"

            resources = {}

            if outline_path.exists():
                with open(outline_path, 'r', encoding='utf-8') as f:
                    resources['outline'] = f.read()
            else:
                resources['outline'] = "outline.md not found"

            if copywriting_path.exists():
                with open(copywriting_path, 'r', encoding='utf-8') as f:
                    resources['copywriting'] = f.read()
            else:
                resources['copywriting'] = "copywriting.md not found"

            image_paths = []
            if images_dir.exists() and images_dir.is_dir():
                for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
                    image_paths.extend([str(p.absolute()) for p in images_dir.glob(ext)])
            
            resources['image_paths'] = sorted(image_paths)

            msg = f"Successfully read resources from {folder}. Found {len(image_paths)} images."
            logger.info(msg)
            return ActionResult(extracted_content=str(resources), include_in_memory=True)

        @self.registry.action(
            'Upload multiple images to social media platforms (XHS, Toutiao, etc.) using file chooser... 请使用绝对路径',
            param_model=UploadImagesAction,
        )
        async def upload_images(params: UploadImagesAction, browser_session: BrowserSession):
            return await self._handle_upload_images(params, browser_session)

        @self.registry.action(
            'Get user persona from soul.md for generating personalized responses...',
        )
        async def get_user_persona():
            uid = current_uid_cv.get()
            if not uid:
                return ActionResult(error="No user context available")
            
            project_root = Path(__file__).parent.parent.parent
            soul_file = project_root / "users" / uid / "soul.md"
            
            if not soul_file.exists():
                return ActionResult(error=f"Persona file not found for user {uid}")
            
            with open(soul_file, 'r', encoding='utf-8') as f:
                persona_content = f.read()
            
            msg = f"Successfully loaded user persona ({len(persona_content)} chars)"
            logger.info(msg)
            return ActionResult(extracted_content=persona_content, include_in_memory=True)

    # --- Helper Methods for upload_images ---

    def _get_valid_image_paths(self, paths: List[str]) -> List[str]:
        valid_paths = []
        for p in paths:
            if os.path.exists(p):
                valid_paths.append(os.path.abspath(p))
            else:
                logger.warning(f"File not found: {p}")
        return valid_paths

    def _create_file_payloads(self, paths: List[str]) -> List[dict]:
        payloads = []
        for p in paths:
            mime_type, _ = mimetypes.guess_type(p)
            ext = os.path.splitext(p)[1].lower()
            
            # Strict MIME type enforcement for common image formats
            if ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif ext == '.png':
                mime_type = 'image/png'
            elif ext == '.webp':
                mime_type = 'image/webp'
            elif ext == '.gif':
                mime_type = 'image/gif'
            
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            with open(p, 'rb') as f:
                content = f.read()
            
            payloads.append({
                "name": os.path.basename(p),
                "mimeType": mime_type,
                "buffer": content
            })
        return payloads

    async def _get_playwright_page(self, page, browser_session: BrowserSession) -> Optional[PlaywrightPage]:
        # Try 1: Check if page itself is the handle
        if hasattr(page, 'locator'):
            return page
        
        # Try 2: Check for .page attribute
        if hasattr(page, 'page'):
            return page.page
        
        # Try 3: Check for .get_page() method
        if hasattr(page, 'get_page'):
            p = page.get_page()
            if asyncio.iscoroutine(p):
                return await p
            return p

        # Try 4: Check browser_session context
        if hasattr(browser_session, 'context') and hasattr(browser_session.context, 'pages') and browser_session.context.pages:
            return browser_session.context.pages[-1]
        elif hasattr(browser_session, 'browser_context') and hasattr(browser_session.browser_context, 'pages') and browser_session.browser_context.pages:
            return browser_session.browser_context.pages[-1]
            
        return None

    async def _find_or_trigger_file_input(self, page: PlaywrightPage) -> bool:
        # 1. Try to find existing file input
        file_input_elements = await page.locator('input[type="file"]').count()
        if file_input_elements > 0:
            return True
            
        # 2. If not found, try to trigger it by clicking upload buttons
        logger.info("No file input found, attempting to click upload triggers...")
        
        for selector in self.UPLOAD_TRIGGER_SELECTORS:
            try:
                # Use JS to click because we want to be robust
                if 'contains' in selector:
                    text = selector.split('"')[1]
                    js_code = f"""
                    () => {{
                        const xpath = "//*[contains(text(), '{text}')]";
                        const result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                        const el = result.singleNodeValue;
                        if (el) {{ el.click(); return true; }}
                        return false;
                    }}
                    """
                    res = await page.evaluate(js_code)
                else:
                    js_code = f"""
                    () => {{
                        const el = document.querySelector('{selector}');
                        if (el) {{ el.click(); return true; }}
                        return false;
                    }}
                    """
                    res = await page.evaluate(js_code)
                    
                if res == True: # JS returns boolean true
                    logger.info(f"Clicked trigger: {selector}")
                    await asyncio.sleep(1) # Wait for input creation
                    
                    # Check if input appeared
                    if await page.locator('input[type="file"]').count() > 0:
                        return True
            except Exception as e:
                logger.debug(f"Click failed for {selector}: {e}")
                continue
                
        return False

    async def _upload_to_best_input(self, page: PlaywrightPage, payloads: List[dict]) -> bool:
        try:
            upload_locators = page.locator('input[type="file"]')
            count = await upload_locators.count()
            logger.info(f"Found {count} file input elements")
            
            if count == 0:
                return False
            
            target_input = None
            
            # Priority 1: Visible input
            for i in range(count):
                loc = upload_locators.nth(i)
                if await loc.is_visible():
                    target_input = loc
                    logger.info(f"Found visible file input at index {i}")
                    break
            
            # Priority 2: Input with 'image' in accept attribute
            if not target_input:
                for i in range(count):
                    loc = upload_locators.nth(i)
                    accept = await loc.get_attribute("accept")
                    if accept and ("image" in accept or ".png" in accept or ".jpg" in accept):
                        target_input = loc
                        logger.info(f"Found image-accepting file input at index {i}: {accept}")
                        break
            
            # Priority 3: Default to first input
            if not target_input:
                logger.info("No specific target input found, defaulting to index 0")
                target_input = upload_locators.nth(0)

            await target_input.set_input_files(files=payloads)
            
            # Force dispatch events
            # Wrap in try-except because if the upload causes a navigation/refresh, this might fail
            try:
                await target_input.evaluate("e => { e.dispatchEvent(new Event('change', {bubbles: true})); e.dispatchEvent(new Event('input', {bubbles: true})); e.dispatchEvent(new Event('blur', {bubbles: true})); }")
            except Exception as e:
                logger.warning(f"Failed to dispatch events (might be normal if page navigated): {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error in _upload_to_best_input: {e}")
            return False

    async def _handle_post_upload_actions(self, page: PlaywrightPage):
        await asyncio.sleep(2) # Wait for UI reaction
        
        try:
            for selector in self.CONFIRM_SELECTORS:
                buttons = await page.locator(selector).all()
                for btn in buttons:
                    if await btn.is_visible():
                        await btn.click()
                        logger.info(f"Clicked confirmation button: {selector}")
                        await asyncio.sleep(1)
        except Exception as e:
            logger.debug(f"Auto-confirm failed (might not be needed): {e}")

    async def _upload_via_cdp_fallback(self, browser_session: BrowserSession, page, payloads: List[dict]) -> ActionResult:
        # logger.info("Direct Playwright Page extraction failed. Attempting sidecar connection via CDP...")
        logger.info("Initiating upload via CDP Sidecar Connection...")
        
        cdp_url = getattr(browser_session, 'cdp_url', None)
        if not cdp_url:
            return ActionResult(error="Failed to extract Playwright Page and no CDP URL found.")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(cdp_url)
                try:
                    # Find the target page
                    target_page = None
                    
                    # Try to match by URL if possible
                    current_url = None
                    if hasattr(page, 'get_url'):
                        try:
                            current_url = await page.get_url() if asyncio.iscoroutinefunction(page.get_url) else page.get_url()
                        except:
                            pass
                    
                    if browser.contexts:
                        for context in browser.contexts:
                            for pg in context.pages:
                                if current_url and pg.url == current_url:
                                    target_page = pg
                                    break
                            if target_page: break
                        
                        if not target_page and browser.contexts[0].pages:
                            target_page = browser.contexts[0].pages[-1]

                    if not target_page:
                        return ActionResult(error="Could not find matching Playwright page via CDP sidecar connection.")

                    # Reuse upload logic
                    success = await self._upload_to_best_input(target_page, payloads)
                    
                    if success:
                        # Also handle post-upload actions in CDP mode
                        await self._handle_post_upload_actions(target_page)
                        
                        msg = f"Successfully uploaded {len(payloads)} files via Playwright Sidecar Connection."
                        logger.info(msg)
                        await asyncio.sleep(3)
                        return ActionResult(extracted_content=msg, include_in_memory=True)
                    else:
                        return ActionResult(error="No file input elements found via sidecar connection.")
                finally:
                    if browser:
                        try:
                            await browser.close()
                        except Exception as e:
                            logger.warning(f"Error closing CDP browser connection: {e}")

        except Exception as e:
            logger.error(f"Sidecar connection failed: {e}")
            return ActionResult(error=f"Failed to upload images via sidecar connection: {str(e)}")

    async def _handle_upload_images(self, params: UploadImagesAction, browser_session: BrowserSession) -> ActionResult:
        try:
            # 1. Validate paths and create payloads
            valid_paths = self._get_valid_image_paths(params.image_paths)
            if not valid_paths:
                return ActionResult(error="No valid image paths provided")
            
            logger.info(f"Attempting to upload {len(valid_paths)} images...")
            payloads = self._create_file_payloads(valid_paths)

            # 2. Get Playwright Page
            # Note: browser_use often wraps the page, so we need to get the current one first
            current_bs_page = await browser_session.get_current_page()
            if not current_bs_page:
                return ActionResult(error="No active page found to upload images.")
                
            pw_page = await self._get_playwright_page(current_bs_page, browser_session)

            # 3. Try Standard Upload (SKIPPED by user request to force CDP)
            # if pw_page:
            #     try:
            #         if await self._find_or_trigger_file_input(pw_page):
            #             if await self._upload_to_best_input(pw_page, payloads):
            #                 await self._handle_post_upload_actions(pw_page)
            #                 msg = f"Successfully uploaded {len(valid_paths)} files via Playwright FilePayload."
            #                 logger.info(msg)
            #                 return ActionResult(extracted_content=msg, include_in_memory=True)
            #     except Exception as e:
            #         logger.warning(f"Standard upload failed, falling back to CDP: {e}")

            # 4. Fallback to CDP Sidecar
            logger.info("Directly attempting sidecar connection via CDP as requested...")
            return await self._upload_via_cdp_fallback(browser_session, current_bs_page, payloads)

        except Exception as e:
            error_msg = f"Failed to upload images: {str(e)}"
            logger.error(error_msg)
            return ActionResult(error=error_msg)
