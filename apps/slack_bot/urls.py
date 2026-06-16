from django.urls import path
from .views import slack_commands

urlpatterns = [
    path("commands/", slack_commands, name="slack_commands"),
]