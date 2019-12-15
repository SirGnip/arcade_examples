# App-specific types for type hinting

from typing import Generator

# A generator function used for async "scripting" of game events.
Script = Generator[None, None, None]
