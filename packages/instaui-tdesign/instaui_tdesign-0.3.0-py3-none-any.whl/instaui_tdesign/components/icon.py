from __future__ import annotations
from typing import List, Optional
from instaui.components.icon import Icon as IconComponent
from instaui.event.event_mixin import EventMixin


class Icon(IconComponent):
    def __init__(
        self,
        name: str,
        *,
        size: Optional[str] = None,
        color: Optional[str] = None,
    ):
        super().__init__(name, size=size, color=color)
        self.classes("t-icon")

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: Optional[List] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self
