"""FastMCP integration for KeyCard OAuth client.

This module provides seamless integration between KeyCard's OAuth client
and FastMCP servers, following the sync/async API design standard.

Components:
- KeycardAuthProvider: FastMCP authentication provider using KeyCard zone tokens
- AccessMiddleware: Middleware that manages OAuth client lifecycle and provides grant decorator
- Access token management through grant decorators

Example Usage:

    # Basic FastMCP server setup with KeyCard authentication
    import fastmcp
    from keycardai.mcp.integrations.fastmcp import (
        KeycardAuthProvider,
        AccessMiddleware,
    )

    # Create MCP server with KeyCard authentication
    mcp = fastmcp.MCP("My KeyCard Server")

    # Add authentication provider
    auth_provider = KeycardAuthProvider(
        zone_url="https://my-keycard-zone.com",
        audience="my-mcp-server"
    )
    mcp.add_auth_provider(auth_provider)

    # Add access middleware for automatic token management
    access = AccessMiddleware(
        zone_url="https://my-keycard-zone.com"
    )
    mcp.add_middleware(access)

    # Use the grant decorator for automatic token exchange in tools
    @mcp.tool()
    @access.grant("https://api.example.com")
    async def call_external_api(ctx: Context, query: str) -> str:
        '''Call an external API on behalf of the authenticated user.

        The decorator automatically exchanges the user's token for one
        that can access the specified resource.
        '''
        # Use the token to call the external API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.example.com/search",
                params={"q": query},
                headers={"Authorization": create_auth_header(ctx.get_state("keycardai").access("https://api.example.com").access_token)}
            )
            return response.json()

    # Simplified setup for common scenarios
    @mcp.tool()
    @access.grant("https://www.googleapis.com/calendar/v3")
    async def get_calendar_events(ctx: Context) -> list:
        '''Get user's calendar events with automatic token delegation.'''
        # Calendar API call with delegated token
        from keycardai.oauth.utils.bearer import create_auth_header
        token = ctx.get_state("keycardai").access("https://www.googleapis.com/calendar/v3").access_token
        headers = {"Authorization": create_auth_header(token)}
        # ... implementation details ...
        return events

    # Run the server
    if __name__ == "__main__":
        mcp.run()

Advanced Configuration:

    # Custom access middleware configuration
    access = AccessMiddleware(
        zone_url="https://my-keycard-zone.com",
        client_name="My Custom Client"
    )

    # Custom authentication with specific requirements
    auth_provider = KeycardAuthProvider(
        zone_url="https://my-keycard-zone.com",
        audience="my-specific-audience",
        mcp_server_name="My Custom Server",
        resource_server_url="https://my-resource-server.com/"
    )

    # Multiple resource access with single decorator
    @mcp.tool()
    @access.grant(["https://www.googleapis.com/calendar/v3", "https://www.googleapis.com/drive/v3"])
    async def sync_calendar_to_drive(ctx: Context):
        '''Sync calendar events to Google Drive with multiple token exchanges.'''
        from keycardai.oauth.utils.bearer import create_auth_header
        calendar_token = ctx.get_state("keycardai").access("https://www.googleapis.com/calendar/v3").access_token
        drive_token = ctx.get_state("keycardai").access("https://www.googleapis.com/drive/v3").access_token
        calendar_headers = {"Authorization": create_auth_header(calendar_token)}
        drive_headers = {"Authorization": create_auth_header(drive_token)}

        # Use both tokens for cross-service operations
        # ... implementation ...
"""

from .middleware import AccessMiddleware
from .provider import KeycardAuthProvider

__all__ = [
    "KeycardAuthProvider",
    "AccessMiddleware",
]
