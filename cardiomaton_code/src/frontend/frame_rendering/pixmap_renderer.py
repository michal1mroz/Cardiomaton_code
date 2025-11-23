from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPixmap, QImage


class PixmapRenderer:
    def __init__(self, image: QImage) -> None:
        self._image = image

    @property
    def image(self) -> QImage:
        return self._image

    @image.setter
    def image(self, img: QImage) -> None:
        self._image = img

    def to_pixmap(self, target_size: QSize) -> QPixmap:
        return QPixmap.fromImage(self._image).scaled(
            target_size,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        )
