import asyncio
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class HumanAssistRequest:
    request_id: str
    question: str
    preview_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    user_response: Optional[str] = None
    is_resolved: bool = False

class HumanAssistManager:
    _instance: Optional['HumanAssistManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._requests: Dict[str, HumanAssistRequest] = {}
        self._lock = asyncio.Lock()
        self._events: Dict[str, asyncio.Event] = {}
    
    async def create_request(self, question: str, preview_url: str = None) -> HumanAssistRequest:
        request_id = f"assist_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        request = HumanAssistRequest(
            request_id=request_id,
            question=question,
            preview_url=preview_url,
        )
        event = asyncio.Event()
        
        async with self._lock:
            self._requests[request_id] = request
            self._events[request_id] = event
        
        logger.info(f"Created human assist request: {request_id}")
        return request
    
    async def wait_for_response(self, request_id: str, timeout: float = 300.0) -> Optional[str]:
        request = self._requests.get(request_id)
        event = self._events.get(request_id)
        
        if not request or not event:
            logger.warning(f"Request {request_id} not found")
            return None
        
        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
            
            async with self._lock:
                request = self._requests.get(request_id)
                if request and request.is_resolved:
                    return request.user_response
            return None
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for response to {request_id}")
            return None
    
    async def resolve_request(self, request_id: str, user_response: str) -> bool:
        request = self._requests.get(request_id)
        event = self._events.get(request_id)
        
        if not request or not event:
            logger.warning(f"Request {request_id} not found")
            return False
        
        async with self._lock:
            request.is_resolved = True
            request.user_response = user_response
            request.resolved_at = datetime.now()
        
        event.set()
        logger.info(f"Resolved human assist request: {request_id}")
        return True
    
    def get_pending_requests(self) -> list:
        return [
            {
                "request_id": r.request_id,
                "question": r.question,
                "preview_url": r.preview_url,
                "created_at": r.created_at.isoformat()
            }
            for r in self._requests.values() if not r.is_resolved
        ]
    
    def get_request(self, request_id: str) -> Optional[Dict]:
        request = self._requests.get(request_id)
        if request:
            return {
                "request_id": request.request_id,
                "question": request.question,
                "preview_url": request.preview_url,
                "created_at": request.created_at.isoformat(),
                "is_resolved": request.is_resolved,
                "user_response": request.user_response
            }
        return None

human_assist_manager = HumanAssistManager()
