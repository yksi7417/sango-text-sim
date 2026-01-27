"""
Display module for rendering game visuals.

This module contains various renderers for displaying game state:
- map_view: Strategic map renderer
- city_view: City detail view (future)
- officer_view: Officer profile view (future)
- components: Reusable UI components (future)
"""

from .map_view import render_strategic_map

__all__ = ['render_strategic_map']
