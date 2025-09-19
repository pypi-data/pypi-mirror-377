from typing import NamedTuple

from numpy.typing import ArrayLike


class PixelMaskDimensions(NamedTuple):
    width: int
    height: int


class __Configuration:
    def load(self, configType: str, content: str) -> None: ...
    def getMaskSize(self) -> PixelMaskDimensions: ...
    def getMask(self) -> ArrayLike: ...
    def setMask(self, mask: ArrayLike) -> None: ...
