"""KMAM — security middleware for access control of IoT devices in LLM Agent systems.

The package mirrors the architecture in the report (Figure 3.1): each subpackage
implements one component of the middleware pipeline orchestrated by
:class:`kmam.middleware.SecurityMiddleware`.
"""

from kmam.context import Decision, RequestContext, Verdict
from kmam.middleware import MiddlewareResult, SecurityMiddleware

__version__ = "0.1.0"

__all__ = [
    "Decision",
    "MiddlewareResult",
    "RequestContext",
    "SecurityMiddleware",
    "Verdict",
]
