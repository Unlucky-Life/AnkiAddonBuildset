"""
Core business logic for the Music Player addon.
"""

from .config import config
from .player_controller import PlayerController

__all__ = ['config', 'PlayerController']
