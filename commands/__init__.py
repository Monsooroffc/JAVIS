"""Command handlers that answer directly, without using a tool."""

from commands.computer import execute_command
from commands.system import date_answer, day_answer, system_command, time_answer

__all__ = [
    "date_answer",
    "day_answer",
    "execute_command",
    "system_command",
    "time_answer",
]