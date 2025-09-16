"""
Base middleware module.
"""

from typing import Callable, Awaitable
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

from mcp_proxy_adapter.core.logging import logger


class BaseMiddleware(BaseHTTPMiddleware):
    """
    Base class for all middleware.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Method that will be overridden in child classes.

        Args:
            request: Request.
            call_next: Next handler.

        Returns:
            Response.
        """
        middleware_name = self.__class__.__name__
        logger.debug(f"🔍 {middleware_name}.dispatch START - {request.method} {request.url.path}")
        
        try:
            # Process request before calling the main handler
            logger.debug(f"🔍 {middleware_name}.before_request START")
            await self.before_request(request)
            logger.debug(f"🔍 {middleware_name}.before_request COMPLETED")

            # Call the next middleware or main handler
            logger.debug(f"🔍 {middleware_name}.call_next START")
            response = await call_next(request)
            logger.debug(f"🔍 {middleware_name}.call_next COMPLETED - Status: {response.status_code}")

            # Process response after calling the main handler
            logger.debug(f"🔍 {middleware_name}.after_response START")
            response = await self.after_response(request, response)
            logger.debug(f"🔍 {middleware_name}.after_response COMPLETED")

            logger.debug(f"🔍 {middleware_name}.dispatch COMPLETED SUCCESSFULLY")
            return response
        except Exception as e:
            logger.error(f"❌ {middleware_name}.dispatch ERROR: {str(e)}", exc_info=True)
            # If an error occurred, call the error handler
            return await self.handle_error(request, e)

    async def before_request(self, request: Request) -> None:
        """
        Method for processing request before calling the main handler.

        Args:
            request: Request.
        """
        pass

    async def after_response(self, request: Request, response: Response) -> Response:
        """
        Method for processing response after calling the main handler.

        Args:
            request: Request.
            response: Response.

        Returns:
            Processed response.
        """
        return response

    async def handle_error(self, request: Request, exception: Exception) -> Response:
        """
        Method for handling errors that occurred in middleware.

        Args:
            request: Request.
            exception: Exception.

        Returns:
            Error response.
        """
        # By default, just pass the error further
        raise exception
