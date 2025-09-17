"""
Protocol middleware module.

This module provides middleware for validating protocol access based on configuration.
"""

from typing import Callable, Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.protocol_manager import get_protocol_manager
from mcp_proxy_adapter.core.logging import logger


class ProtocolMiddleware(BaseHTTPMiddleware):
    """
    Middleware for protocol validation.

    This middleware checks if the incoming request protocol is allowed
    based on the protocol configuration.
    """

    def __init__(self, app, app_config: Optional[Dict[str, Any]] = None):
        """
        Initialize protocol middleware.

        Args:
            app: FastAPI application
            app_config: Application configuration dictionary (optional)
        """
        super().__init__(app)
        # Normalize config to dictionary
        normalized_config: Optional[Dict[str, Any]]
        if app_config is None:
            normalized_config = None
        elif hasattr(app_config, "get_all"):
            try:
                normalized_config = app_config.get_all()
            except Exception as e:
                logger.debug(
                    f"ProtocolMiddleware - Error calling get_all(): {e}, type: {type(app_config)}"
                )
                normalized_config = None
        elif hasattr(app_config, "keys"):
            normalized_config = app_config  # Already dict-like
        else:
            logger.debug(
                f"ProtocolMiddleware - app_config is not dict-like, type: {type(app_config)}, value: {repr(app_config)}"
            )
            normalized_config = None

        logger.debug(
            f"ProtocolMiddleware - normalized_config type: {type(normalized_config)}"
        )
        if normalized_config:
            logger.debug(
                f"ProtocolMiddleware - protocols in config: {'protocols' in normalized_config}"
            )
            if "protocols" in normalized_config:
                logger.debug(
                    f"ProtocolMiddleware - protocols type: {type(normalized_config['protocols'])}"
                )

        self.app_config = normalized_config
        # Get protocol manager with current configuration
        self.protocol_manager = get_protocol_manager(normalized_config)

    def update_config(self, new_config: Dict[str, Any]):
        """
        Update configuration and reload protocol manager.

        Args:
            new_config: New configuration dictionary
        """
        # Normalize new config
        if hasattr(new_config, "get_all"):
            try:
                self.app_config = new_config.get_all()
            except Exception:
                self.app_config = None
        elif hasattr(new_config, "keys"):
            self.app_config = new_config
        else:
            self.app_config = None
        self.protocol_manager = get_protocol_manager(self.app_config)
        logger.info("Protocol middleware configuration updated")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through protocol middleware.

        Args:
            request: Incoming request
            call_next: Next middleware/endpoint function

        Returns:
            Response object
        """
        logger.debug(
            f"🔍 ProtocolMiddleware.dispatch START for {request.method} {request.url.path}"
        )
        logger.debug(f"🔍 ProtocolMiddleware - protocols.enabled: {self.protocol_manager.enabled}")
        logger.debug(f"🔍 ProtocolMiddleware - allowed_protocols: {self.protocol_manager.allowed_protocols}")
        
        try:
            # Get protocol from request
            protocol = self._get_request_protocol(request)
            logger.debug(f"🔍 ProtocolMiddleware - Detected protocol: {protocol} for {request.method} {request.url.path}")
            logger.debug(f"🔍 ProtocolMiddleware - Request scheme: {request.url.scheme}")
            logger.debug(f"🔍 ProtocolMiddleware - Request headers: {dict(request.headers)}")

            # Check if protocol is allowed
            is_allowed = self.protocol_manager.is_protocol_allowed(protocol)
            logger.debug(f"🔍 ProtocolMiddleware - Protocol '{protocol}' allowed: {is_allowed}")
            
            if not is_allowed:
                logger.warning(
                    f"❌ ProtocolMiddleware - Protocol '{protocol}' not allowed for request to {request.url.path}"
                )
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": "Protocol not allowed",
                        "message": f"Protocol '{protocol}' is not allowed. Allowed protocols: {self.protocol_manager.get_allowed_protocols()}",
                        "allowed_protocols": self.protocol_manager.get_allowed_protocols(),
                    },
                )

            # Continue processing
            logger.debug(f"✅ ProtocolMiddleware - Protocol '{protocol}' allowed, continuing to next middleware/handler")
            logger.debug(f"🔍 ProtocolMiddleware - About to call next handler")
            response = await call_next(request)
            logger.debug(f"✅ ProtocolMiddleware - Next handler completed with status: {response.status_code}")
            logger.debug(f"✅ ProtocolMiddleware - Protocol middleware completed successfully for {request.method} {request.url.path}")
            return response

        except Exception as e:
            logger.error(f"❌ ProtocolMiddleware - Protocol middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Protocol validation error", "message": str(e)},
            )

    def _get_request_protocol(self, request: Request) -> str:
        """
        Extract protocol from request.

        Args:
            request: FastAPI request object

        Returns:
            Protocol name (http, https, mtls)
        """
        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol START")
        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - request.url.scheme: {request.url.scheme}")
        
        try:
            # Check if request is secure (HTTPS)
            if request.url.scheme:
                scheme = request.url.scheme.lower()
                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - scheme: {scheme}")

                # If HTTPS, check if client certificate is provided (MTLS)
                if scheme == "https":
                    logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - HTTPS detected, checking for mTLS")
                    
                    # Check for client certificate in ASGI scope
                    try:
                        # Method 1: Check transport info in ASGI scope
                        if hasattr(request, "scope") and request.scope:
                            logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - ASGI scope available")
                            # Check for client certificate in transport layer
                            transport = request.scope.get("transport")
                            if transport and hasattr(transport, "get_extra_info"):
                                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - transport available, checking SSL object")
                                try:
                                    ssl_object = transport.get_extra_info("ssl_object")
                                    if ssl_object:
                                        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - SSL object available, checking peer cert")
                                        try:
                                            cert = ssl_object.getpeercert()
                                            if cert:
                                                logger.debug(f"✅ ProtocolMiddleware._get_request_protocol - mTLS client certificate detected: {cert.get('subject', 'unknown')}")
                                                return "mtls"
                                            else:
                                                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - No peer certificate found")
                                        except Exception as e:
                                            logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Error checking client certificate: {e}")
                                    else:
                                        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - No SSL object found")
                                except Exception as e:
                                    logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Error getting SSL object from transport: {e}")
                            else:
                                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - No transport or get_extra_info method")
                            
                            # Method 2: Check client info in ASGI scope
                            try:
                                client_info = request.scope.get("client")
                                if client_info and len(client_info) > 2:
                                    # client_info format: (host, port, additional_info...)
                                    # Additional info might contain certificate information
                                    logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Client info detected, might be mTLS: {client_info}")
                                else:
                                    logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Client info: {client_info}")
                            except Exception as e:
                                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Error checking client info: {e}")
                        else:
                            logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - No ASGI scope available")
                    except Exception as e:
                        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Error checking ASGI scope for mTLS: {e}")

                    # Check for client certificate in headers (proxy forwarded)
                    try:
                        mtls_headers = [
                            request.headers.get("ssl-client-cert"),
                            request.headers.get("x-client-cert"),
                            request.headers.get("x-ssl-cert"),
                            request.headers.get("x-forwarded-client-cert")
                        ]
                        if any(mtls_headers):
                            logger.debug(f"✅ ProtocolMiddleware._get_request_protocol - mTLS client certificate detected in headers")
                            return "mtls"
                        else:
                            logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - No mTLS headers found")
                    except Exception as e:
                        logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Error checking headers for mTLS: {e}")

                    logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Returning 'https' (no mTLS detected)")
                    return "https"

                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Returning scheme: {scheme}")
                return scheme

            # Fallback to checking headers
            x_forwarded_proto = request.headers.get("x-forwarded-proto")
            if x_forwarded_proto:
                logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Using x-forwarded-proto: {x_forwarded_proto}")
                return x_forwarded_proto.lower()

            # Default to HTTP
            logger.debug(f"🔍 ProtocolMiddleware._get_request_protocol - Defaulting to 'http'")
            return "http"
            
        except Exception as e:
            logger.error(f"❌ ProtocolMiddleware._get_request_protocol - Error: {e}", exc_info=True)
            # Fallback to HTTP if there's any error
            return "http"


def setup_protocol_middleware(app, app_config: Optional[Dict[str, Any]] = None):
    """
    Setup protocol middleware for FastAPI application.

    Args:
        app: FastAPI application
        app_config: Application configuration dictionary (optional)
    """
    logger.debug(f"setup_protocol_middleware - app_config type: {type(app_config)}")

    # Check if protocol management is enabled
    if app_config is None:
        from mcp_proxy_adapter.config import config

        app_config = config.get_all()
        logger.debug(
            f"setup_protocol_middleware - loaded from global config, type: {type(app_config)}"
        )

    logger.debug(
        f"setup_protocol_middleware - final app_config type: {type(app_config)}"
    )

    if hasattr(app_config, "get"):
        logger.debug(
            f"setup_protocol_middleware - app_config keys: {list(app_config.keys()) if hasattr(app_config, 'keys') else 'no keys'}"
        )
        protocols_config = app_config.get("protocols", {})
        logger.debug(
            f"setup_protocol_middleware - protocols_config: {protocols_config}"
        )
        logger.debug(
            f"setup_protocol_middleware - protocols_config type: {type(protocols_config)}"
        )
        enabled = (
            protocols_config.get("enabled", True)
            if hasattr(protocols_config, "get")
            else True
        )
        logger.debug(f"setup_protocol_middleware - protocols_config.get('enabled', True) = {enabled}")
    else:
        logger.debug(
            f"setup_protocol_middleware - app_config is not dict-like: {repr(app_config)}"
        )
        enabled = True

    logger.debug(f"setup_protocol_middleware - protocol management enabled: {enabled}")

    if enabled:
        # Create protocol middleware with current configuration
        logger.debug(
            f"setup_protocol_middleware - creating ProtocolMiddleware with config type: {type(app_config)}"
        )
        middleware = ProtocolMiddleware(app, app_config)
        logger.debug(f"setup_protocol_middleware - adding middleware to app")
        app.add_middleware(ProtocolMiddleware, app_config=app_config)
        logger.info("Protocol middleware added to application")
    else:
        logger.info("Protocol management is disabled, skipping protocol middleware")
