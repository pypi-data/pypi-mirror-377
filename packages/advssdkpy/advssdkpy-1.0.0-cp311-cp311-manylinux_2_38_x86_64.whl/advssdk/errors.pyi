class AdvsSdkInternalException(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


class AdvsSdkInvalidArgumentError(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


class AdvsSdkInvalidOperationError(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


class AdvsSdkNoMemoryException(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


class AdvsSdkPointerException(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


class AdvsSdkAxiException(Exception):
    @classmethod
    def __init__(cls, *args, **kwargs) -> None: ...


def _throwAdvsError(code: int, message: str) -> None: ...
