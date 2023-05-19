from time import time

from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsItem

from .player import AnimationPlayer, Animation, Item, Reanim

__all__ = (
    'AnimationPlayer',
    'Animation',
    'Item',
    'Reanim',
    'AnimatedItem',
)


class AnimatedItem(QGraphicsItem):
    def __init__(self, anim: Animation):
        try:
            super().__init__()
        except RuntimeError:
            pass
        self.anim = anim
        self._player = AnimationPlayer(self.anim)
        self._player.ground_moved = self.__move
        self.prepareGeometryChange()
        self.movable = True
        self.time = time()

    def set_anim(self, name: str):
        self._player.set_anim(name)

    def paint(self, painter: QPainter, _1, _2=None) -> None:
        self._player.paint(painter)

    def advance(self, phase: int) -> None:
        if not phase:
            return
        new_time = time()
        self._player.update(new_time - self.time)
        self.time = new_time

    def boundingRect(self) -> QRectF:
        return self._player.bounding_rect()

    def hide_item(self, name: str):
        self._player.hide_item(name)

    def show_item(self, name: str):
        self._player.show_item(name)

    def __move(self, ground_translate: QPointF):
        if self.movable:
            # 物体的移动和地面的移动相反
            self.setPos(self.pos() - ground_translate)

    def set_items_hidden(self, hidden: bool, *items: str):
        for item in items:
            if hidden:
                self.hide_item(item)
            else:
                self.show_item(item)

    def set_speed(self, speed: float):
        self._player.speed = speed
