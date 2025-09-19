from typing import List, NamedTuple, Callable

from advssdk.bias import __Bias
from advssdk.board import __Board
from advssdk.chip import __Chip
from advssdk.configuration import __Configuration
from advssdk.cooling import __Cooling
from advssdk.extsync import __ExtSync
from advssdk.monitor import __Monitor
from advssdk.trigger import __Trigger
from advssdk.acquisition import __Acquisition
from advssdk.hw_version import __HwVersion
from advssdk.device_props import __DeviceProps
from advssdk.axi import __Axi
from advssdk.nvmem import __Nvmem


class DeviceDescriptor(NamedTuple):
    connectionString: str
    product: str
    manufacturer: str
    serialNumber: str
    usbVid: int
    usbPid: int
    usbInstancePath: str
    isHighSpeed: bool
    isSuperSpeed: bool


class SdkVersion(NamedTuple):
    major: int
    minor: int
    patch: int


class Device:
    bias: __Bias
    board: __Board
    chip: __Chip
    config: __Configuration
    cooling: __Cooling
    extsync: __ExtSync
    monitor: __Monitor
    trigger: __Trigger
    acq: __Acquisition
    hw_version: __HwVersion
    props: __DeviceProps
    axi: __Axi
    nvmem: __Nvmem

    def __init__(self) -> None: ...
    def close(self) -> None: ...
    def finalize(self) -> None: ...
    def isOpened(self) -> bool: ...
    def open(self, locator: str) -> None: ...
    def setLogFunction(self, func: Callable[[str, int], None]) -> None: ...
    def enumerate(self) -> List[DeviceDescriptor]: ...


def getCompileTimeVersion() -> SdkVersion: ...


def getRuntimeVersion() -> SdkVersion: ...
