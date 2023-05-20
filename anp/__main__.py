from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PySide6.QtCore import QTimer, QRectF, QPointF
from PySide6.QtGui import QAction, QImage, QPainter, Qt
from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QGraphicsScene, QGraphicsView, QVBoxLayout, \
    QDialog, QLabel, QSpinBox, QHBoxLayout, QCheckBox

app = QApplication()

from anp import AnimatedItem, Animation
from Resources import Resources


class SameIntervalAnimItem(AnimatedItem):
    def __init__(self, anim: Animation, interval: float):
        super().__init__(anim)
        self.interval = interval

    def advance(self, phase: int) -> None:
        if not phase:
            return
        self._player.update(self.interval)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.resize(800, 600)

        self.file_menu = self.menuBar().addMenu("文件（&F）")
        self.file_menu.addAction(QAction("打开（&O）", self, triggered=self.open))
        self.file_menu.addAction(QAction("导出（&S）", self, triggered=self.save))
        self.file_menu.addAction(QAction("加载资源（&R）", self, triggered=self.load_resource))
        self.setting_menu = self.menuBar().addAction(QAction("设置（&S）", self, triggered=self.change_settings))

        self.timer = QTimer(self)
        self.timer.setInterval(1000 // self.settings.render_fps)
        self.timer.timeout.connect(lambda: (self.scene.advance(), self.scene.update()))

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setParent(self)
        self.view.setGeometry(self.geometry())

        self.v_layout1 = QVBoxLayout(self)
        self.v_layout1.addWidget(self.view)

        self.menuBar().raise_()

        self.anim: Animation | None = None
        self.item: SameIntervalAnimItem | None = None
        self.resources_root: Path | None = None  # 通过 load_resource 加载的资源根路径

    def open(self):
        if self.item is not None:
            self.scene.removeItem(self.item)
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开 .reanim 文件", filter='*.reanim')
        path = Path(file_path)
        if not path.is_file():
            return
        if self.resources_root is None:
            set_resources_root(path.parent.parent)  # 便于不加载 resources.xml 直接查看文件
        self.anim = Resources.instance().load_reanim(path)
        self.item = self.make_item()
        self.scene.addItem(self.item)
        self.timer.start()

    def save(self):
        suffix2coding = {
            'mp4': 'mp4v',
            'avi': 'XVID',
            'reanim': '',
        }
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出", filter=', '.join(f'*.{name}' for name in suffix2coding.keys()))
        anim = self.anim
        if not file_path:
            return
        if file_path.endswith('.reanim'):
            anim.save(file_path)
            return
        bounding = anim.bounding_rect_at(0, [])
        for i in range(1, anim.max_frame() + 1):
            bounding = bounding_rect(bounding, anim.bounding_rect_at(i, []))
        size = bounding.size()
        import cv2
        fps: Final = 60.0
        img = QImage(size.toSize(), QImage.Format_ARGB32_Premultiplied)

        coding = suffix2coding[file_path.split('.')[-1]]
        if isinstance(coding, str):
            fourcc = cv2.VideoWriter_fourcc(*(list(coding) + [''] * (4 - len(coding))))
        else:
            fourcc = coding
        writer = cv2.VideoWriter(file_path, fourcc, fps, size.toSize().toTuple())
        sec = 0
        painter = QPainter(img)
        painter.translate(-bounding.topLeft())
        while sec < anim.max_frame() / anim.fps:
            anim_frame = sec * anim.fps
            img.fill(Qt.transparent)
            anim.paint(anim_frame, painter, [])
            img.save('./temp.bmp')
            cv_img = cv2.imread('./temp.bmp')
            writer.write(cv_img)
            sec += 1 / fps
        del painter
        writer.release()
        Path('./temp.bmp').unlink()

    def load_resource(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载资源文件", filter='resources.xml')
        if not file_path:
            return
        path = Path(file_path)
        Resources.instance().load_properties(path, strict=False)
        self.resources_root = path.parent.parent
        set_resources_root(self.resources_root)

    def change_settings(self):
        settings_win = SettingsWindow(self)
        self.settings = settings_win.get_settings()
        self.settings_updated()

    def settings_updated(self):
        self.timer.setInterval(1000 // self.settings.render_fps)
        if self.item is not None:
            self.scene.removeItem(self.item)
            self.item = self.make_item()
            self.scene.addItem(self.item)

    def make_item(self) -> AnimatedItem:
        if self.settings.use_same_interval:
            return SameIntervalAnimItem(self.anim, 1 / self.settings.render_fps)
        return AnimatedItem(self.anim)


@dataclass
class Settings:
    render_fps: int = 60
    use_same_interval: bool = False


class SettingsWindow(QDialog):
    def __init__(self, parent: MainWindow):
        super().__init__(parent)
        self.settings = parent.settings

        self.label1 = QLabel("每秒渲染的次数：", self)
        self.render_fps = QSpinBox(self)
        self.render_fps.setRange(0, 120)
        self.render_fps.setValue(self.settings.render_fps)

        self.label2 = QLabel("更新时使用等同间隔（启用后可能会造成速度变慢，禁用可能会掉帧）", self)
        self.use_same_interval = QCheckBox(self)
        self.use_same_interval.setChecked(self.settings.use_same_interval)

        self.h_layout1 = QHBoxLayout()
        self.h_layout1.addWidget(self.label1)
        self.h_layout1.addWidget(self.render_fps)
        self.h_layout2 = QHBoxLayout()
        self.h_layout2.addWidget(self.label2)
        self.h_layout2.addWidget(self.use_same_interval)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.h_layout1)
        self.main_layout.addLayout(self.h_layout2)

    def get_settings(self) -> Settings:
        self.exec()
        self.settings.render_fps = self.render_fps.value()
        self.settings.use_same_interval = self.use_same_interval.isChecked()
        return self.settings


def bounding_rect(a: QRectF, b: QRectF) -> QRectF:
    points = []
    for rect in (a, b):
        points.extend([rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight()])
    min_x = min(point.x() for point in points)
    min_y = min(point.y() for point in points)
    max_x = max(point.x() for point in points)
    max_y = max(point.y() for point in points)
    return QRectF(QPointF(min_x, min_y), QPointF(max_x, max_y))


def main():
    # app = QApplication()
    main_win = MainWindow()
    main_win.show()
    exit(app.exec())


def set_resources_root(root: str | Path):
    if isinstance(root, str):
        root = Path(root)
    import Resources
    Resources.resources_root = root


if __name__ == '__main__':
    main()
