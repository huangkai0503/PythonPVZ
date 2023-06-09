from abc import abstractmethod, ABCMeta
from dataclasses import dataclass
from math import cos, sin, radians
from pathlib import Path
from typing import Callable, TypeVar, cast, Any, TYPE_CHECKING, Final, overload
from xml.etree.ElementTree import Element, tostring

import mypy_extensions
from PySide6.QtCore import QPointF, QPoint, QRect, QRectF
from PySide6.QtGui import QPixmap, QPainter, QTransform, Qt

from Resources import Resources, parse_xml

if TYPE_CHECKING:
    from typing_extensions import Self

real = TypeVar('real', int, float)
ATTACH: Final = 'attacher__'


class Animation:
    fps: float

    def __init__(self, fps: float = 12., items: list['Item'] | None = None):
        if items is None:
            items = []
        self.fps = fps
        self._items: list[Item] = items

    def paint(self, frame: float, painter: QPainter, hide_items: list[str]):
        for item in self._items:
            if item.name in hide_items:
                continue
            painter.save()
            item.paint(frame, painter)
            painter.restore()

    def bounding_rect_at(self, frame: float, hide_items: list[str]) -> QRectF:
        points = []
        for item in self._items:
            if item.name in hide_items:
                continue
            bounding = item.bounding_rect_at(frame)
            if bounding is None or bounding.isNull():
                continue
            points.append(bounding.topLeft())
            points.append(bounding.topRight())
            points.append(bounding.bottomRight())
            points.append(bounding.bottomLeft())
        return bounding_rect(points)

    def max_frame(self):
        if not self._items:
            return 0
        return max(item.max_frame() for item in self._items)

    def find_item_by_name(self, name: str) -> 'Item | None':
        for item in self._items:
            if item.name == name:
                return item
        return None

    @overload
    def internal_to(self, frame: float, guide_name: str, /) -> 'Animation': ...
    @overload
    def internal_to(self, start: float, end: float, /) -> 'Animation': ...

    def internal_to(self, frame: float, guide_name: str | float, /) -> 'Animation':
        if isinstance(guide_name, str):
            end, _ = self.sub_anim_frame(guide_name)
        else:
            end = guide_name
        res = Animation()
        res.fps = self.fps
        items = []
        for item in self._items:
            new_item = item.internal_to(frame, end)
            items.append(new_item)
        res._items = items
        return res

    def sub_anim_frame(self, name: str):  # 切片表示法
        guide_item: NormalItem = cast(NormalItem, self.find_item_by_name(name))
        if guide_item is None:
            return 0, 0
        max_frame = self.max_frame() + 1
        if guide_item.hidden_at(0):
            start = 1
            for start in range(1, max_frame):
                if not guide_item.hidden_at(start):
                    break
        else:
            start = 0
        for frame in range(start, max_frame):
            if guide_item.hidden_at(frame):
                return start, frame
        return start, max_frame

    def load_img0(self, guide_name: str = '', hide_items: list[str] | None = None) -> QPixmap:
        if hide_items is None:
            hide_items = []
        if guide_name:
            frame, _ = self.sub_anim_frame(guide_name)
        else:
            frame = 0
        max_frame = self.max_frame()
        if not max_frame:
            return QPixmap()
        bounding = self.bounding_rect_at(frame, hide_items)
        res = QPixmap(bounding.size().toSize())
        res.fill(Qt.transparent)
        painter = QPainter(res)
        painter.translate(-bounding.topLeft())
        self.paint(frame, painter, hide_items)
        del painter
        return res

    # abstract
    def save(self, path: Path | str): pass


class Reanim(Animation):
    @staticmethod
    def load(path: Path | str):
        if not isinstance(path, Path):
            path = Path(path)
        root = parse_xml(path)
        calc = _ReanimCalculator(root, path.parent)
        return calc.start()

    def save(self, path: Path | str):
        if not isinstance(path, Path):
            path = Path(path)
        dummy_top = 'dummy-top'
        root = Element(dummy_top)
        fps = Element('fps')
        if int(self.fps) == self.fps:
            fps.text = str(int(self.fps))
        else:
            fps.text = str(self.fps)
        root.append(fps)
        for item in self._items:
            assert isinstance(item, ReanimItem)
            root.append(item.to_xml())
        res = tostring(root, method='html')[len(dummy_top) + 2: -(len(dummy_top) + 2 + 1)]
        with path.open('wb') as f:
            f.write(res)


class _ReanimCalculator:
    fps: float

    def __init__(self, tree: Element, root: Path):
        self.tree = tree
        self.root = root
        self._attach = False

    def start(self):
        fps = float(self.tree[0].text)  # float?
        self.fps = fps
        items = []
        for child in self.tree[1:]:
            item = self.track(child)
            items.append(item)
        return Reanim(fps, items)

    def track(self, tree: Element) -> 'ReanimItem':
        assert tree.tag == 'track'
        is_attach, name = self.is_attach(tree)
        res: ReanimItemWithData
        if is_attach:
            if not any(i for i in tree[2:]):
                return ReanimSingleAttachItem(name, ItemData().updated(self.frame(tree[1])), self.fps)
            else:
                res = ReanimAttacherItem(name, self.fps)
            self._attach = True
        else:
            res = ReanimNormalItem(name)
            self._attach = False
        frame = 0
        raw = ItemData()
        for child in tree[1:]:
            data = self.frame(child)
            raw = raw.updated(data)
            res.set_data_at(raw, frame)
            frame += 1
        res.read_complete_recall()
        return res

    def frame(self, tree: Element):
        assert tree.tag == 't'
        res: dict[str, Any] = {}
        for child in tree:
            inner = child.text
            if inner is None:
                if child.tag == 'i':
                    res['image_name'] = ''
                    res['image'] = None
                continue
            match child.tag:
                case 'x':
                    res['x'] = float(inner)
                case 'y':
                    res['y'] = float(inner)
                case 'sx':
                    res['scale_x'] = float(inner)
                case 'sy':
                    res['scale_y'] = float(inner)
                case 'kx':
                    res['x_rotate'] = float(inner)
                case 'ky':
                    res['y_rotate'] = float(inner)
                case 'a':
                    res['opacity'] = float(inner)
                case 'i':
                    res['image_name'] = inner
                    img = Resources.instance().load_pixmap(inner)
                    res['image'] = img
                case 'f':
                    if inner == '-1':
                        res['hidden'] = True
                    elif inner == '0':
                        res['hidden'] = False
                case 'text':
                    res['text'] = inner
        return res

    def is_attach(self, tree: Element) -> tuple[bool, str]:
        assert tree.tag == 'track'
        name = tree[0].text
        assert name is not None
        if not name.startswith(ATTACH):
            return False, name
        for child in tree[1:]:
            assert child.tag == 't'
            for cc in child:
                if cc.tag == 'text':
                    text = cc.text
                    assert text is not None
                    if text.startswith(ATTACH):
                        return True, name[len(ATTACH):]
        return False, name


class Item:
    name: str

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def paint(self, frame: float, painter: QPainter) -> None: pass
    @abstractmethod
    def bounding_rect_at(self, frame: float) -> QRectF | None: pass
    @abstractmethod
    def max_frame(self) -> int: pass
    @abstractmethod
    def internal_to(self, start: float, end: float) -> 'Self': ...


@mypy_extensions.trait
class ReanimItem(Item, metaclass=ABCMeta):
    @abstractmethod
    def read_complete_recall(self): pass
    @abstractmethod
    def to_xml(self) -> Element: pass


class ItemWithData(Item, metaclass=ABCMeta):
    def __init__(self, name: str = ''):
        super().__init__(name)
        self._data: dict[int, ItemData] = {}

    def set_data_at(self, data: 'ItemData', frame: int):
        self._data[frame] = data

    def data_at(self, frame: float) -> 'ItemData':
        if int(frame) == frame and int(frame) in self._data.keys():
            return self._data[int(frame)]
        a, b = find_range(list(self._data.keys()), frame)
        progress = (frame - a) / (b - a)
        return self._data[a].interpolated(self._data[b], progress)

    def transform_at(self, frame: float):
        return self.data_at(frame).to_transform()

    def hidden_at(self, frame: float) -> bool:
        f = max(i for i in self._data.keys() if i <= frame)
        return self._data[f].hidden

    def pos_at(self, frame: float):
        if int(frame) == frame and int(frame) in self._data.keys():
            data = self._data[int(frame)]
            return QPointF(data.x, data.y)
        a, b = find_range(list(self._data.keys()), frame)
        progress = (frame - a) / (b - a)
        data_a = self._data[a]
        data_b = self._data[b]
        x = interpolated(data_a.x, data_b.x, progress)
        y = interpolated(data_a.y, data_b.y, progress)
        return QPointF(x, y)

    def opacity_at(self, frame: float):
        return self.data_at(frame).opacity

    def max_frame(self) -> int:
        return max(self._data.keys())


@mypy_extensions.trait
class ReanimItemWithData(ItemWithData, ReanimItem, metaclass=ABCMeta):
    def to_xml(self) -> Element:
        def _add_ele(parent: Element, tag: str, text: str):
            e = Element(tag)
            e.text = text
            parent.append(e)

        res = Element('track')
        name = Element('name')
        name.text = self.name
        res.append(name)
        previous = ItemData()
        for frame in range(self.max_frame() + 1):
            t = Element('t')
            data = self.data_at(frame)
            if data.x != previous.x:
                _add_ele(t, 'x', f'{data.x:.1f}')
            if data.y != previous.y:
                _add_ele(t, 'y', f'{data.y:.1f}')
            if data.opacity != previous.opacity:
                _add_ele(t, 'a', f'{data.opacity}')
            if data.scale_x != previous.scale_x:
                _add_ele(t, 'sx', f'{data.scale_x:.3f}')
            if data.scale_y != previous.scale_y:
                _add_ele(t, 'sy', f'{data.scale_y:.3f}')
            if data.x_rotate != previous.x_rotate:
                _add_ele(t, 'kx', f'{data.x_rotate:.1f}')
            if data.y_rotate != previous.y_rotate:
                _add_ele(t, 'ky', f'{data.y_rotate:.1f}')
            if data.hidden != previous.hidden:
                _add_ele(t, 'f', '-1' if data.hidden else '0')
            if data.image_name != previous.image_name:
                _add_ele(t, 'i', data.image_name)
            previous = data
            res.append(t)
        return res


class NormalItem(ItemWithData, metaclass=ABCMeta):
    def __init__(self, name: str = ''):
        super().__init__(name)

    def paint(self, frame: float, painter: QPainter):
        if self.hidden_at(frame):
            return
        img = self.image_at(frame)
        if img is None or img.isNull():
            return
        painter.setOpacity(painter.opacity() * self.opacity_at(frame))
        painter.setTransform(self.transform_at(frame), True)
        painter.drawPixmap(0, 0, img)

    def image_at(self, frame: float) -> QPixmap | None:
        frames = list(self._data.keys())
        frames.sort()
        frames.reverse()
        for f in frames:
            if f <= frame:
                img = self._data[f].image
                if img is not None and not img.isNull():
                    return img
        return None

    def internal_to(self, start: float, end: float) -> 'Self':
        cls: type[Self] = type(self)
        res = cls()
        data = self.data_at(start)
        end_data = self.data_at(end)
        res.set_data_at(data, 0)
        res.set_data_at(end_data, 1)
        return res

    def bounding_rect_at(self, frame: float) -> QRectF | None:
        if self.hidden_at(frame):
            return None
        img = self.image_at(frame)
        if img is None or img.isNull():
            return None
        rect = img.rect()
        transform = self.transform_at(frame)
        return bounding_rect([
            transform.map(QPointF(0, 0)), transform.map(rect.bottomLeft()),
            transform.map(rect.topRight()), transform.map(rect.bottomRight())])

    def data_at(self, frame: float) -> 'ItemData':
        max_frame = self.max_frame()
        if frame >= max_frame:
            return self._data[max_frame]
        return super().data_at(frame)


class AttacherItem(ItemWithData, metaclass=ABCMeta):
    def __init__(self, name: str, fps: float):
        super().__init__(name)
        self.playing: Animation | None = None
        self.player: AnimationPlayer | None = None
        # 按 time_frames 从小到大排序
        self.anim: list[tuple[int, Animation | None, str, str]] = []  # (time_frames, animation, sub, external)
        self.fps = fps

    def paint(self, frame: float, painter: QPainter):
        self._recalc(frame)
        if self.player is None:
            return
        if self.hidden_at(frame):
            return
        painter.setOpacity(painter.opacity() * self.opacity_at(frame))
        transform = self.transform_at(frame)
        painter.setTransform(transform, True)
        self.player.paint(painter)

    def internal_to(self, start: float, end: float) -> 'Self':
        res = type(self)(self.name, self.fps)
        res.playing = self.playing
        self._recalc(start)
        if self.playing is None:
            return res
        anim = self.playing
        player = self.player
        if player is None:
            return res
        sub1 = player.playing
        start1, _ = anim.sub_anim_frame(sub1)
        a = start1 + player.now_anim_frame()

        self._recalc(end)
        p2 = self.playing
        player = self.player
        if anim is not p2 or player is None:
            return res  # 禁止不同动画间连接
        sub2 = player.playing
        start2, _ = anim.sub_anim_frame(sub2)
        b = start2 + player.now_anim_frame()
        res.anim = [(0, anim.internal_to(a, b), '', '')]
        return res

    def bounding_rect_at(self, frame: float) -> QRectF | None:
        self._recalc(frame)
        if self.player is None:
            return None
        if self.hidden_at(frame):
            return None
        return self.player.bounding_rect()

    def _recalc(self, frame: float) -> None:
        for start, anim, sub, external in reversed(self.anim):
            if start <= frame:
                break
        else:
            # raise ValueError(f'{frame} is out of range')
            return
        if anim is None:
            self.player = None
            self.playing = None
            return
        elif anim is not self.playing:
            self.player = AnimationPlayer(anim)
            self.playing = anim
        elif self.player is None:
            return
        if external == 'once':
            self.player.loop_count = 1
        self.player.goto(sub, (frame - start) / self.fps * anim.fps)


class SingleAttachItem(Item, metaclass=ABCMeta):
    def __init__(self, name: str, anim: Animation, start: float, max_frame: float, data: 'ItemData', fps: float):
        """max_frame: 开始循环的帧数"""
        super().__init__(name)
        self.anim = anim
        self.start = start
        self._max_frame = max_frame
        self.transform = data.to_transform()
        self.opacity = data.opacity
        self.data = data
        self.fps = fps
        self._ratio = self.anim.fps / self.fps

    def paint(self, frame: float, painter: QPainter) -> None:
        painter.setTransform(self.transform)
        painter.setOpacity(painter.opacity() * self.opacity)
        self.anim.paint(((self.start + frame) % self._max_frame) * self._ratio, painter, [])

    def max_frame(self) -> int:
        return int(self._max_frame)

    def internal_to(self, start: float, end: float) -> 'Self':
        return type(self)(self.name, self.anim, self.start + start, end - start, self.transform, self.fps)

    def bounding_rect_at(self, frame: float) -> QRectF | None:
        return self.anim.bounding_rect_at((self.start + frame) * self._ratio, [])


class ReanimNormalItem(NormalItem, ReanimItemWithData):
    def read_complete_recall(self): pass


class ReanimAttacherItem(AttacherItem, ReanimItemWithData):
    def to_xml(self) -> Element:
        res = Element('track')
        name = Element('name')
        name.text = f'{ATTACH}{self.name}'
        res.append(name)
        return res

    def read_complete_recall(self):
        previous_playing = ''
        previous_sub = ''
        previous_external = ''
        for frame, data in self._data.items():
            text = data.text
            if not text.startswith(ATTACH):
                continue
            playing, sub, external = _parse_attach_text(text)
            if playing != previous_playing or sub != previous_sub or external != previous_external:
                anim = Resources.instance().load_anim_by_name(playing) if playing else None
                self.anim.append((frame, anim, sub, external))
            previous_external = external
            previous_sub = sub
            previous_playing = playing
        self.anim.sort(key=lambda x: x[0])


class ReanimSingleAttachItem(SingleAttachItem, ReanimItem):
    def read_complete_recall(self):
        pass

    def to_xml(self) -> Element:
        res = Element('track')
        name = Element('name')
        name.text = f'{ATTACH}{self.name}'
        res.append(name)
        return res

    def __init__(self, name: str, data: 'ItemData', fps: float):
        playing, sub, external = _parse_attach_text(data.text)
        anim = Resources.instance().load_anim_by_name(playing)
        offset = float(external)
        if sub:
            start, end = anim.sub_anim_frame(sub)
            max_frame = end - start
            start += offset
        else:
            start = offset
            max_frame = anim.max_frame() + 1
        super().__init__(name, anim, start, max_frame, data, fps)


def _parse_attach_text(s: str):
    text = s[len(ATTACH):]
    s_pos = text.find('[')
    if s_pos != -1:
        value = text[:s_pos]
        external = text[s_pos + 1: -1]
    else:
        value = text
        external = ''
    pos = value.rfind('__')
    if pos == -1:
        playing = value
        sub = ''
    else:
        playing = value[:pos]
        sub = value[pos + len('__'):]
    return playing, sub, external


@dataclass
class ItemData:
    x: float = 0.
    y: float = 0.
    opacity: float = 1.
    scale_x: float = 1.
    scale_y: float = 1.
    x_rotate: float = 0.
    y_rotate: float = 0.
    image: QPixmap | None = None
    hidden: bool = False
    image_name: str = ''
    text: str = ''

    def interpolated(self, other: 'ItemData', progress: float):
        return ItemData(
            interpolated(self.x, other.x, progress),
            interpolated(self.y, other.y, progress),
            interpolated(self.opacity, other.opacity, progress),
            interpolated(self.scale_x, other.scale_x, progress),
            interpolated(self.scale_y, other.scale_y, progress),
            interpolated(self.x_rotate, other.x_rotate, progress),
            interpolated(self.y_rotate, other.y_rotate, progress),
            # image=self.image,
            # hidden=self.hidden,
            # image_name=self.image_name,
            # text=self.text,
        )

    def updated(self, other: dict):
        return ItemData(
            other.get('x', self.x),
            other.get('y', self.y),
            other.get('opacity', self.opacity),
            other.get('scale_x', self.scale_x),
            other.get('scale_y', self.scale_y),
            other.get('x_rotate', self.x_rotate),
            other.get('y_rotate', self.y_rotate),
            other.get('image', self.image),
            other.get('hidden', self.hidden),
            other.get('image_name', self.image_name),
            other.get('text', self.text),
        )

    def to_transform(self) -> QTransform:
        x_rotate = radians(self.x_rotate)
        y_rotate = radians(self.y_rotate)
        a = self.scale_x * cos(x_rotate)
        b = self.scale_x * sin(x_rotate)
        c = -self.scale_y * sin(y_rotate)
        d = self.scale_y * cos(y_rotate)
        tx = self.x
        ty = self.y
        matrix = QTransform(
            a, b, 0,
            c, d, 0,
            tx, ty, 1,
        )
        return matrix


class AnimationPlayer:
    def __init__(self, anim: Animation):
        self.speed = 1.
        self.loop_count = -1
        self.anim = anim
        self.__internal_anim: Animation | None = None
        self.__ground: NormalItem | None = cast(NormalItem | None, anim.find_item_by_name('_ground'))
        self.__previous_ground_pos: QPointF | None = None
        self.playing = ''
        self.hide_items: list[str] = []
        self.ground_moved: Callable[[QPointF], None] = lambda translate: None
        self.time = 0.  # 单位：s

    def update(self, elapsed_time: float):
        if self.loop_count == 0:
            return
        self.time += elapsed_time * self.speed
        if self.__internal_anim is not None:
            if self.now_anim_frame() > self.__internal_anim.max_frame():
                self.time %= self.__internal_anim.max_frame() / self.anim.fps
                self.__internal_anim = None
                self.__previous_ground_pos = None
            return
        if not self.playing:
            start = 0
            max_frame = self.anim.max_frame()
        else:
            start, end = self.anim.sub_anim_frame(self.playing)
            max_frame = end - start - 1
        if self.now_anim_frame() > max_frame:
            if self.loop_count != -1:
                self.loop_count -= 1
            self.time %= max_frame / self.anim.fps
            self.__previous_ground_pos = None
            return

        ground = self.__ground
        if ground is None:
            return
        frame = start + self.now_anim_frame()
        if ground.hidden_at(frame):
            self.__previous_ground_pos = None
            return
        pos = ground.pos_at(frame)
        previous = self.__previous_ground_pos
        if previous is not None:
            self.ground_moved(pos - previous)
        self.__previous_ground_pos = pos

    def now_anim_frame(self):
        return self.time * self.anim.fps

    def paint(self, painter: QPainter):
        if self.loop_count == 0:
            return
        hide_items = self.hide_items
        if self.__internal_anim is not None:
            self.__internal_anim.paint(self.now_anim_frame(), painter, hide_items)
        elif self.playing:
            anim = self.anim
            start, _ = anim.sub_anim_frame(self.playing)
            anim.paint(start + self.now_anim_frame(), painter, hide_items)
        else:
            self.anim.paint(self.now_anim_frame(), painter, hide_items)

    def bounding_rect(self):
        if self.__internal_anim is not None:
            return self.__internal_anim.bounding_rect_at(self.now_anim_frame(), self.hide_items)
        if self.playing:
            start, _ = self.anim.sub_anim_frame(self.playing)
            return self.anim.bounding_rect_at(start + self.now_anim_frame(), self.hide_items)
        return self.anim.bounding_rect_at(self.now_anim_frame(), self.hide_items)

    def set_anim(self, name: str):
        if name == self.playing:
            return
        if self.playing:
            self.__internal_anim = self.anim.internal_to(self.now_anim_frame(), name)
        self.time = 0.
        self.loop_count = -1
        self.playing = name

    def hide_item(self, name: str):
        self.hide_items.append(name)

    def show_item(self, name: str):
        if name in self.hide_items:
            self.hide_items.remove(name)

    def playing_frames(self) -> tuple[int, int]:
        if not self.playing:
            return 0, self.anim.max_frame()
        return self.anim.sub_anim_frame(self.playing)

    def set_anim_frame(self, frame: float) -> None:
        if self.loop_count == 0:
            return
        self.time = frame / self.anim.fps
        self.__internal_anim = None

    def max_frame(self) -> int:
        if self.playing:
            start, end = self.anim.sub_anim_frame(self.playing)
            return end - start - 1
        return self.anim.max_frame()

    def goto(self, anim: str, frame: float) -> None:
        self.playing = anim
        elapsed_loop, frame = divmod(frame, self.max_frame())
        self.time = frame / self.anim.fps
        if self.loop_count != -1:
            self.loop_count -= int(elapsed_loop)
            if self.loop_count < 0:
                self.loop_count = 0


def interpolated(a: float, b: float, progress: float) -> float:
    return a + (b - a) * progress


def find_range(choices: list[real], base: float) -> tuple[real, real]:
    a = max(i for i in choices if i <= base)
    b = min(i for i in choices if i >= base)
    return a, b


def bounding_rect(points: list[QPointF | QRectF | QPoint | QRect]) -> QRectF:
    if not points:
        return QRectF()
    if isinstance(points[0], (QRectF, QRect)):
        points = [rect.topLeft() for rect in points] + [rect.bottomRight() for rect in points]
    min_x = min(point.x() for point in points)
    min_y = min(point.y() for point in points)
    max_x = max(point.x() for point in points)
    max_y = max(point.y() for point in points)
    return QRectF(QPointF(min_x, min_y), QPointF(max_x, max_y))
