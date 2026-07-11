import os
import django

# Setup Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from mcp.server.fastmcp import FastMCP
from telemetry.models import User, CodeEvent, GitEvent, ErrorEvent
from asgiref.sync import sync_to_async

mcp = FastMCP("Developer DNA")

@mcp.tool()
async def get_activity_timeline(user_id: int, limit: int = 50) -> str:
    """Get the recent activity timeline for a user."""
    @sync_to_async
    def fetch_events():
        events = []
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return "User not found."
            
        code_events = CodeEvent.objects.filter(session__user=user).order_by("-timestamp")[:limit]
        git_events = GitEvent.objects.filter(session__user=user).order_by("-timestamp")[:limit]
        error_events = ErrorEvent.objects.filter(session__user=user).order_by("-timestamp")[:limit]
        
        for ce in code_events:
            events.append({"type": "code", "timestamp": ce.timestamp, "desc": f"{ce.event_type} on {ce.file_path}"})
        for ge in git_events:
            events.append({"type": "git", "timestamp": ge.timestamp, "desc": f"{ge.event_type} on {ge.branch}"})
        for ee in error_events:
            events.append({"type": "error", "timestamp": ee.timestamp, "desc": f"{ee.severity} - {ee.error_type}"})
            
        events.sort(key=lambda x: x["timestamp"], reverse=True)
        events = events[:limit]
        
        if not events:
            return "No activity found."
            
        return "\n".join([f"[{e['timestamp'].isoformat()}] {e['type'].upper()}: {e['desc']}" for e in events])
    
    return await fetch_events()

@mcp.resource("user://{user_id}/profile")
def get_user_profile(user_id: int) -> str:
    """Get a user's profile information."""
    try:
        user = User.objects.get(pk=user_id)
        return f"User: {user.username}\nEmail: {user.email}\nJoined: {user.created_at}"
    except User.DoesNotExist:
        return "User not found."
