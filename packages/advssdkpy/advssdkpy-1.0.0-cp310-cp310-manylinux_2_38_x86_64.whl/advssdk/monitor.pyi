from typing import List, NamedTuple, Callable, Any


class MonitorDataOnValueChanged(NamedTuple):
    id: str
    value: int | float
    isWarningConditionMet: bool
    isErrorConditionMet: bool


class MonitorDataOnAvailabilityChanged(NamedTuple):
    id: str
    value: int | float | None


class __Monitor:
    def getIds(self) -> List[str]: ...
    def getDataType(self, monitorId: str) -> str: ...
    def fetchValue(self, monitorId: str) -> float: ...

    def setOnValueChangedCallback(
            self,
            monitorId: str,
            func: Callable[[MonitorDataOnValueChanged], Any]) -> None: ...

    def setOnAvailabilityChangedCallback(
            self,
            monitorId: str,
            func: Callable[[MonitorDataOnAvailabilityChanged], Any]) -> None: ...
