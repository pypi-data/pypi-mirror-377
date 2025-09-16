"""
Resource subscription support for MCP
"""

from typing import Dict, Set

from mcp.server.fastmcp import Context, FastMCP


class SubscriptionManager:
    """Manages resource subscriptions for the MCP server"""

    def __init__(self, mcp_server: FastMCP):
        self.mcp_server = mcp_server
        self.subscriptions: Dict[str, Set[str]] = {}  # uri -> set of request_ids

    def subscribe(self, uri: str, request_id: str) -> bool:
        """
        Subscribe to changes in a resource
        
        Args:
            uri: The resource URI to subscribe to
            request_id: The request ID of the subscriber
            
        Returns:
            True if subscription was successful
        """
        if uri not in self.subscriptions:
            self.subscriptions[uri] = set()
        
        self.subscriptions[uri].add(request_id)
        return True
    
    def unsubscribe(self, uri: str, request_id: str) -> bool:
        """
        Unsubscribe from changes in a resource
        
        Args:
            uri: The resource URI to unsubscribe from
            request_id: The request ID of the subscriber
            
        Returns:
            True if unsubscription was successful
        """
        if uri in self.subscriptions and request_id in self.subscriptions[uri]:
            self.subscriptions[uri].remove(request_id)
            return True
        return False
    
    def notify_resource_changed(self, uri: str) -> None:
        """
        Notify subscribers that a resource has changed
        
        Args:
            uri: The URI of the changed resource
        """
        if uri not in self.subscriptions:
            return
        
        # Send notifications to all subscribers
        for request_id in self.subscriptions[uri]:
            self.mcp_server.notify(
                "notifications/resources/updated",
                {"uri": uri},
                request_id=request_id,
            )

    def notify_list_changed(self) -> None:
        """Notify that the list of available resources has changed"""
        self.mcp_server.notify("notifications/resources/list_changed")


# Handlers for subscription operations

def subscribe_resource(ctx: Context, uri: str):
    """
    Subscribe to changes in a specific resource
    
    Parameters:
        uri: The URI of the resource to subscribe to
    """
    subscription_manager = ctx.request_context.lifespan_context.subscription_manager
    request_id = ctx.request_context.request.id
    
    success = subscription_manager.subscribe(uri, request_id)
    
    if success:
        return {"result": {"subscribed": True}}
    else:
        return {
            "error": {
                "code": "subscription_failed",
                "message": f"Failed to subscribe to resource: {uri}"
            }
        }


def unsubscribe_resource(ctx: Context, uri: str):
    """
    Unsubscribe from changes in a specific resource
    
    Parameters:
        uri: The URI of the resource to unsubscribe from
    """
    subscription_manager = ctx.request_context.lifespan_context.subscription_manager
    request_id = ctx.request_context.request.id
    
    success = subscription_manager.unsubscribe(uri, request_id)
    
    if success:
        return {"result": {"unsubscribed": True}}
    else:
        return {
            "error": {
                "code": "unsubscription_failed",
                "message": f"Failed to unsubscribe from resource: {uri}"
            }
        }
