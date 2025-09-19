from typing import List


class Sector:
    startingAddress: int
    endingAddress: int


class Region:
    sectorSize: int
    sectors: List[Sector]


class NonVolatileMemory:
    id: str
    partNumber: str
    regions: List[Region]

    def program(self, startingAddress: int, data: bytes) -> None: ...
    def read(self, startingAddress: int, dataLen: int) -> bytes: ...


class __Nvmem:
    def getIds(self) -> List[str]: ...
    def selectMemory(self, flashId: str) -> NonVolatileMemory: ...
