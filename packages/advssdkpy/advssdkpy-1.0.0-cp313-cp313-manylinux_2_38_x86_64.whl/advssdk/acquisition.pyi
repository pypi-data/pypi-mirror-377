from typing import Any, List, Callable
from numpy.typing import ArrayLike

Tpx3DdToaTotPacketCallback = Callable[[ArrayLike, object], Any]
Tpx3SeqItotEventPacketCallback = Callable[[ArrayLike], Any]
Tpx3SeqToaTotPacketCallback = Callable[[ArrayLike], Any]

Tpx3DdToaTotVectorCallback = Callable[[ArrayLike, ArrayLike, ArrayLike, object], Any]
Tpx3SeqItotEventVectorCallback = Callable[[ArrayLike, ArrayLike, ArrayLike], Any]
Tpx3SeqToaTotVectorCallback = Callable[[ArrayLike, ArrayLike, ArrayLike], Any]

AcqDataCallback = Tpx3DdToaTotPacketCallback | Tpx3DdToaTotVectorCallback \
                  | Tpx3SeqItotEventPacketCallback | Tpx3SeqItotEventVectorCallback \
                  | Tpx3SeqToaTotPacketCallback | Tpx3SeqToaTotVectorCallback

RawDataCallback = Callable[[ArrayLike], Any]


class __Acquisition:
    def getChannelIds(self) -> List[str]: ...
    def abort(self, channelId: str) -> None: ...
    def begin(self, channelId: str) -> None: ...
    def end(self, channelId: str) -> None: ...

    def setDataCallback(self, channelId: str, func: AcqDataCallback) -> None: ...
    def setRawDataCallback(self, channelId: str, func: RawDataCallback) -> None: ...
