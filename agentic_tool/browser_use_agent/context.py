from contextvars import ContextVar

agentbay_session_cv = ContextVar("agentbay_session", default=None)
current_uid_cv = ContextVar("current_uid", default=None)
browser_steps_cv = ContextVar("browser_steps", default=None)
output_stream_cv = ContextVar("output_stream", default=None)
preview_url_cv = ContextVar("preview_url", default=None)
