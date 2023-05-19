from pathlib import Path
from typing import Final, TYPE_CHECKING
from xml.etree.ElementTree import fromstring, Element

from PySide6.QtGui import QPixmap, QPainter, QBitmap, Qt

if TYPE_CHECKING:
    from anp import Animation

__all__ = (
    'Resources',
    'parse_xml',
    'parse_xml_string',
)

_resources: 'Resources | None' = None
XML_HEADER: Final = '<?xml version="1.0" encoding="UTF-8"?>'
REANIM_NAME_HEADER: Final = 'IMAGE_REANIM_'
resources_root = Path()  # 填入 PvZ 程序所在文件夹路径


class Resources:
    prop_all: dict[str, dict[str, Path]]
    img_cache: dict[str, QPixmap]
    anim_cache: dict[str, 'Animation']

    def load_properties(self, file: str | Path, strict: bool = True) -> None:
        if isinstance(file, str):
            file = Path(file)
        self.load_properties_from_str(file.read_text('utf-8'), file.parent.parent, strict)

    def load_properties_from_str(self, s: str, root: Path, strict: bool = True) -> None:
        tree = parse_xml_string(s)
        calc = _PropertyCalculator(tree, root, strict)
        self.prop_all = calc.calc()

    def find(self, name: str) -> Path | None:
        for value in self.prop_all.values():
            if name in value:
                return value[name]
        return None

    def resources(self, id_: str) -> dict[str, Path]:
        return self.prop_all[id_]

    def load_pixmap(self, name: str) -> QPixmap:
        if name in self.img_cache:
            return self.img_cache[name]
        path = self.find(name)
        if path:
            img = self._pixmap_with_mask(path)
        elif name.startswith(REANIM_NAME_HEADER):
            img = self._pixmap_with_mask(resources_root / 'reanim' / f'{name[len(REANIM_NAME_HEADER):]}')
        else:
            img = None
        if img is None or img.isNull():
            img = QPixmap(100, 100)
            painter = QPainter(img)
            painter.drawText(0, 0, name)
            del painter
        self.img_cache[name] = img
        return img

    @staticmethod
    def _pixmap_with_mask(path: Path) -> QPixmap:
        suffixes = _PropertyCalculator.suffixes_for('Image')
        need = path.stem.upper()
        mask_need = need + '_'
        img_path = None
        mask_path = None
        for file in path.parent.iterdir():
            if file.suffix.lower() in suffixes:
                stem = file.stem.upper()
                if stem == need:
                    img_path = file
                    if mask_path is not None:
                        break
                elif stem == mask_need:
                    mask_path = file
                    if img_path is not None:
                        break
        if img_path is None:
            return QPixmap()
        res = QPixmap(img_path)
        if mask_path is not None:
            mask = QPixmap(str(mask_path))
            res.setMask(mask.createMaskFromColor(Qt.black))
            print(mask_path)
        return res

    def load_reanim(self, name_or_path: str | Path) -> 'Animation':
        from anp import Reanim
        if isinstance(name_or_path, Path):
            return Reanim.load(name_or_path)  # 通过路径访问不缓存
        name = name_or_path
        if name in self.anim_cache:
            return self.anim_cache[name]
        anim = Reanim.load(resources_root / 'reanim' / f'{name}.reanim')
        self.anim_cache[name] = anim
        return anim

    def load_anim_by_name(self, name: str) -> 'Animation':
        return self.load_reanim(name)

    @staticmethod
    def instance():
        global _resources
        if _resources is not None:
            return _resources
        _resources = Resources()
        _resources.prop_all = {}
        _resources.img_cache = {}
        _resources.anim_cache = {}
        return _resources


class _PropertyCalculator:
    def __init__(self, tree: Element, root: Path, strict: bool):
        self.tree = tree
        self.root = root
        self.strict = strict
        self.path = Path()
        self.id_prefix = ''

    def calc(self) -> dict[str, dict[str, Path]]:
        return self.resources_manifest(self.tree)

    def resources_manifest(self, tree: Element) -> dict[str, dict[str, Path]]:
        res: dict[str, dict[str, Path]] = {}
        for child in tree:
            id_ = child.get('id')
            assert id_ is not None, f'Expect the node has id, but it only has {child.keys()}.'
            res[id_] = self.resources(child)
        return res

    def resources(self, tree: Element) -> dict[str, Path]:
        res: dict[str, Path] = {}
        for child in tree:
            if child.tag == 'SetDefaults':
                self.set_defaults(child)
            else:
                res |= self.resource(child)
        return res

    def set_defaults(self, tree: Element) -> None:
        prop = tree.attrib
        if 'path' in prop:
            self.path = Path(prop['path'])
        if 'idprefix' in prop:
            self.id_prefix = prop['idprefix']

    def resource(self, tree: Element) -> dict[str, Path]:
        tree_id = tree.get('id')
        assert tree_id is not None
        id_ = self.id_prefix + tree_id
        dir_ = self.root / self.path
        prop_path = tree.get('path')
        assert prop_path is not None
        if '.' in prop_path:
            return {id_: dir_ / prop_path}
        suffixes = self.suffixes_for(tree.tag)
        for file in dir_.iterdir():
            if file.is_file() and file.stem.upper() == prop_path.upper() and file.suffix.lower() in suffixes:
                return {id_: file}
        if self.strict:
            raise ValueError(f'There is not file with name {prop_path} in {dir_.joinpath()}')
        else:
            print(f'miss {tree.tag.lower()} {prop_path} in {dir_.joinpath()}')
            return {}

    @staticmethod
    def suffixes_for(type_: str) -> tuple[str, ...]:
        if type_ == 'Image':
            return '.gif', '.png', '.jpg'
        elif type_ == 'Sound':
            return '.ogg', '.mo3'
        return ()


def parse_xml_string(s: str) -> Element:
    if not s.startswith('<?'):
        res = fromstring(f'{XML_HEADER}<dummy-top>{s}</dummy-top>')
        return res
    return fromstring(s)


def parse_xml(path: Path) -> Element:
    s = path.read_text('utf-8')
    return parse_xml_string(s)
