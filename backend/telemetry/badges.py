import pygal
from pygal.style import DarkStyle
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from telemetry.models import User, CodeEvent

def activity_badge(request, username: str):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)

    # Calculate recent activity over last 7 days
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    events = CodeEvent.objects.filter(session__user=user, timestamp__gte=seven_days_ago)

    # Simple aggregation by day
    activity_by_day = {}
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).date()
        activity_by_day[day] = 0

    for event in events:
        day = event.timestamp.date()
        if day in activity_by_day:
            activity_by_day[day] += 1

    chart = pygal.Bar(style=DarkStyle, width=400, height=200, show_legend=False)
    chart.title = f"{username}'s Last 7 Days Code Activity"
    chart.x_labels = [day.strftime("%a") for day in activity_by_day.keys()]
    chart.add('Events', list(activity_by_day.values()))

    svg = chart.render()

    response = HttpResponse(svg, content_type="image/svg+xml")
    # Cache for 1 hour to prevent abuse while keeping data relatively fresh
    response['Cache-Control'] = 'public, max-age=3600'
    return response
